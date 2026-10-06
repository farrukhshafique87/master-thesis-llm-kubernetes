.PHONY: help format lint validate validate-kube validate-yaml test clean \
        kind-up kind-down build load deploy-baseline deploy-secure \
        pull-model-baseline pull-model-secure pause-baseline pause-secure \
        resume-baseline resume-secure

IMAGE ?= llm-api:1.0.0
CLUSTER ?= thesis-cluster

help:
	@echo "Code quality:   format lint test validate"
	@echo "Cluster:        kind-up kind-down"
	@echo "Image:          build load"
	@echo "Deploy:         deploy-baseline deploy-secure"
	@echo "Model:          pull-model-baseline pull-model-secure"
	@echo "Run one env at a time: pause-<env> / resume-<env>"

format:
	black apps/llm-api
	isort apps/llm-api

lint:
	ruff check apps/llm-api

validate-yaml:
	yamllint .

validate-kube:
	kubectl kustomize kubernetes/overlays/kind-baseline | kubeconform -strict -summary
	kubectl kustomize kubernetes/overlays/kind-secure | kubeconform -strict -summary

validate:
	make lint
	make validate-yaml
	make validate-kube

test:
	cd apps/llm-api && pytest

kind-up:
	./scripts/kind-up.sh

kind-down:
	kind delete cluster --name $(CLUSTER)

build:
	docker build -t $(IMAGE) apps/llm-api

load:
	kind load docker-image $(IMAGE) --name $(CLUSTER)

deploy-baseline:
	kubectl apply -k kubernetes/overlays/kind-baseline

deploy-secure:
	kubectl apply -k kubernetes/overlays/kind-secure

pull-model-baseline:
	./scripts/pull-model.sh llm-baseline

pull-model-secure:
	./scripts/pull-model.sh llm-secure

pause-baseline:
	./scripts/pause-env.sh llm-baseline

pause-secure:
	./scripts/pause-env.sh llm-secure

resume-baseline:
	./scripts/resume-env.sh llm-baseline

resume-secure:
	./scripts/resume-env.sh llm-secure

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
