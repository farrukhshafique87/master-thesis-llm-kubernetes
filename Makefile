.PHONY: help format lint validate validate-kube validate-yaml test clean

help:
	@echo "Available targets:"
	@echo "  format          Format Python code"
	@echo "  lint            Run Ruff"
	@echo "  validate-yaml   Validate YAML syntax"
	@echo "  validate-kube   Validate Kubernetes manifests"
	@echo "  validate        Run all validations"
	@echo "  test            Run pytest"
	@echo "  clean           Remove Python cache"

format:
	black apps/llm-api
	isort apps/llm-api

lint:
	ruff check apps/llm-api

validate-yaml:
	yamllint .

validate-kube:
	kubectl kustomize kubernetes/base | kubeconform -strict -summary

validate:
	make lint
	make validate-yaml
	make validate-kube

test:
	cd apps/llm-api && pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
