# Makefile for Salah Tracker BDD Tests

.PHONY: help install-bdd test-bdd test-smoke test-regression test-api test-ui clean-reports

# Default target
help:
	@echo "Salah Tracker BDD Test Commands:"
	@echo "  install-bdd     Install BDD dependencies"
	@echo "  test-bdd        Run all BDD tests"
	@echo "  test-smoke      Run smoke tests only"
	@echo "  test-regression Run regression tests"
	@echo "  test-api        Run API tests only"
	@echo "  test-ui         Run UI tests only"
	@echo "  clean-reports   Clean test reports"
	@echo "  check-deps      Check BDD dependencies"

# Install BDD dependencies
install-bdd:
	@echo "Installing BDD dependencies..."
	pip install -r config/requirements-bdd.txt

# Run all BDD tests
test-bdd:
	@echo "Running all BDD tests..."
	behave

# Run smoke tests
test-smoke:
	@echo "Running smoke tests..."
	behave --tags @smoke

# Run regression tests
test-regression:
	@echo "Running regression tests..."
	behave --tags @regression

# Run API tests
test-api:
	@echo "Running API tests..."
	behave --tags @api

# Run UI tests
test-ui:
	@echo "Running UI tests..."
	behave --tags @ui

# Check dependencies
check-deps:
	@echo "Checking BDD dependencies..."
	@command -v behave >/dev/null 2>&1 || { echo "behave not found. Install with: pip install behave"; exit 1; }
	@echo "BDD dependencies OK"

# Clean test reports
clean-reports:
	@echo "Cleaning test reports..."
	rm -rf reports/
	mkdir -p reports

# Run specific feature
test-feature:
	@echo "Running specific feature: $(FEATURE)"
	behave features/$(FEATURE)

# Run with specific tags
test-tags:
	@echo "Running tests with tags: $(TAGS)"
	behave --tags $(TAGS)

# Generate HTML report
test-report:
	@echo "Running tests and generating report..."
	behave --format html --outdir reports

# Quick test (smoke only)
test-quick:
	@echo "Running quick tests..."
	behave --tags @smoke

# Full test suite (all BDD tests)
test-full:
	@echo "Running full test suite..."
	behave

# Development setup
dev-setup:
	@echo "Setting up development environment..."
	pip install -r config/requirements.txt
	pip install -r config/requirements-bdd.txt
	@command -v behave >/dev/null 2>&1 || { echo "behave not found. Install with: pip install behave"; exit 1; }

# CI/CD pipeline
ci-test:
	@echo "Running CI/CD tests..."
	behave --tags @smoke
