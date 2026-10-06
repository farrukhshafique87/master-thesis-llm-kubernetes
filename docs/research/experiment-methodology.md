# Experiment Methodology

Status: **proposed** — confirm with the supervisor before the first measured run.
This document defines how every experiment is run. It contains no results.

## 1. Fixed decisions

| Topic            | Decision                                                         |
| ---------------- | ---------------------------------------------------------------- |
| Research Qs      | RQ1 total overhead, RQ2 local vs cloud, RQ3 per-control          |
| Deadline         | December 2026                                                    |
| Model            | Qwen2.5 0.5b via Ollama (larger models too slow on the local host)  |
| Inference params | temperature 0.0, seed 42, 64 output tokens, model kept loaded    |
| Configuration    | Kustomize: one base, overlays per environment and security level |
| Baseline         | `kind-baseline` overlay: no security controls                    |
| Secure           | `kind-secure` overlay: controls added as Kustomize components    |
| Run rule         | Only ONE environment (baseline or secure) runs at a time         |
| CNI              | Calico in all runs (baseline and secure)                         |

## 2. What "baseline" contains

The baseline has no RBAC restrictions beyond defaults, no NetworkPolicies, no
mTLS, no application Secrets and no ingress/authentication gateway. Container
hardening already in the base manifests (non-root user, dropped capabilities)
is part of **every** configuration and is therefore not counted as overhead.

## 3. Controlled variables

Same container images, model and model version, prompt, inference parameters,
Ollama settings (keep-alive, parallelism), resource requests/limits, Kubernetes
and Calico versions, load profile and tool versions. Any change is recorded in
the environment record (`scripts/record-environment.sh`).

## 4. Run protocol (proposed)

1. Pause the other environment (`make pause-baseline` / `make pause-secure`).
2. Run `scripts/record-environment.sh results/<exp>/ <namespace>`.
3. Run `tests/k6/smoke.js`. Abort if it fails.
4. Warm-up: 1 minute of the same load, discarded.
5. Measured run: 5 minutes, `--summary-export` to `results/<exp>/`.
6. Cool-down 2 minutes. Repeat for at least 3 repetitions (5 if time allows).
7. Interleave configurations (C0, C1, … C0, C1, …) instead of running all
   repetitions of one configuration first, to spread out time-dependent noise.
8. Close other heavy applications on the host during runs.

## 5. Two measurement paths

| Path        | Endpoint  | Why                                                        |
| ----------- | --------- | ---------------------------------------------------------- |
| Full        | `/chat`   | Realistic end-to-end cost including inference              |
| Lightweight | `/health` | No inference: exposes the per-request cost of the controls |

## 6. Analysis

Per configuration: median of repetitions with min–max spread. Overhead =
(secured − baseline) / baseline for P50, P95, P99, throughput, CPU and memory.
Report the spread so that differences inside the noise are not claimed as
overhead. Report Kind and cloud results separately (RQ2).

## 7. Threats to validity (to discuss in the thesis)

* Kind nodes are containers on one machine: no real network between nodes, and
  the load generator shares the host CPU.
* CPU-only inference; results do not transfer to GPU serving.
* Overhead of NetworkPolicies is specific to the CNI (Calico).
* Single model, single prompt, small repetition count.
* Cloud node types differ from the laptop; compare relative overhead only.
