# Secure Distributed Deployment and Performance Evaluation of Large Language Models on Kubernetes

This repository contains the implementation and experimental environment for my Master's thesis at **Frankfurt University of Applied Sciences**.

The thesis investigates the deployment, security, and performance evaluation of Large Language Model (LLM) inference workloads on Kubernetes clusters.

## Research Focus

The project studies how a distributed LLM serving application can be deployed on Kubernetes and how security mechanisms affect its performance.

The main research focus is the relationship between:

* LLM inference performance
* Kubernetes resource utilization
* scalability and workload distribution
* reliability of the serving system
* Kubernetes security mechanisms
* performance overhead introduced by security controls

The evaluation is intended to compare a baseline deployment with progressively secured configurations. The final evaluation will also consider deployment in a managed cloud Kubernetes environment in addition to the local development environment.

## Project Architecture

The application is based on a small distributed LLM serving stack consisting of:

* **FastAPI** — API layer for handling inference requests
* **Ollama** — local LLM inference server
* **qwen2.5:0.5b** — primary LLM used for the prototype
* **Kubernetes** — container orchestration and distributed deployment
* **Prometheus** — metrics collection
* **Grafana** — monitoring and visualization
* **Metrics Server** — Kubernetes resource metrics
* **k6** — workload generation and performance testing
* **Docker** — containerization
* **Kind** — local Kubernetes cluster for development and initial evaluation

## Security Scope

Security is evaluated as an incremental part of the deployment.

The planned security mechanisms include:

* Kubernetes RBAC
* Kubernetes Secrets
* Network Policies
* Ingress
* TLS
* mutual TLS (mTLS)
* authenticated API access
* secure service-to-service communication

The project aims to measure the effect of these controls rather than treating security only as a configuration task.

## Performance Evaluation

The performance evaluation will use controlled workload scenarios to examine the behaviour of the LLM serving system under different deployment and security configurations.

Planned workload scenarios include:

* Smoke testing
* Average-load testing
* Stress testing
* Spike testing
* Breakpoint testing
* Soak testing

The evaluation will consider metrics such as:

* request latency
* percentile latency
* request throughput
* CPU utilization
* memory utilization
* resource consumption
* system behaviour under increasing load

Measured results will be documented separately from the implementation configuration.

## Repository Structure

```text
.
├── apps/              # Application source code
├── docker/             # Docker-related configuration
├── docs/               # Project and research documentation
├── kubernetes/         # Kubernetes manifests and configurations
├── monitoring/         # Monitoring configuration
├── results/            # Experimental results and generated output
├── tests/              # Application and performance tests
├── .editorconfig       # Editor configuration
├── .gitignore          # Git ignore rules
├── .pre-commit-config.yaml
├── .yamllint           # YAML linting configuration
├── Makefile            # Development and validation commands
└── pyproject.toml      # Python project configuration
```

## Development Environment

The initial development and testing environment uses:

```text
Windows 11
└── WSL2
    └── Docker Desktop
        └── Kind Kubernetes Cluster
```

The local environment provides a controlled platform for developing and validating the deployment before the final cloud-based evaluation.

## Research Approach

The project follows an incremental implementation and evaluation approach.

The deployment is first established as a functional baseline. Monitoring and workload testing are then used to establish measurable system behaviour. Security mechanisms are subsequently introduced and evaluated to identify their effect on the performance and resource requirements of the system.

This allows the implementation work and experimental evaluation to remain connected to the research question rather than treating deployment and benchmarking as separate activities.

## Thesis Status

This repository is under active development as part of the Master's thesis.

The implementation, security configuration, performance experiments, and cloud evaluation will be completed incrementally. Results will only be added after the corresponding experiments have been executed and documented.

## Academic Context

**Thesis:** Secure Distributed Deployment and Performance Evaluation of Large Language Models on Kubernetes

**Institution:** Frankfurt University of Applied Sciences

**Degree:** Master of Science in Information Technology
