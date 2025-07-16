# Bills of Mortality Data Processor - Makefile
# Python conversion of R scripts for Death by Numbers project

.PHONY: help install run test clean format lint check-deps dev-install shell

# Default target
help:
	@echo "📊 Bills of Mortality Data Processor"
	@echo "=====================================\n"
	@echo "Available commands:"
	@echo "  make install       - Install dependencies with Poetry"
	@echo "  make run           - Run the full data processor (all datasets)"
	@echo "  make run-simple    - Run simple processor (single dataset)"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean output files and cache"
	@echo "  make format        - Format code with Black"
	@echo "  make lint          - Run linting with Flake8"
	@echo "  make check-deps    - Check for outdated dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make shell         - Open Poetry shell"
	@echo "  make jupyter       - Start Jupyter notebook"
	@echo "  make build         - Build the package"
	@echo "  make full-process  - Run complete processing pipeline"
	@echo "  make check-data    - Check if data directory exists"
	@echo ""

# Installation and setup
install:
	@echo "🔧 Installing dependencies..."
	poetry install --no-dev

dev-install:
	@echo "🔧 Installing development dependencies..."
	poetry install

# Running the processor
run:
	@echo "🚀 Running Bills of Mortality processor..."
	poetry run python run_full_processor.py

run-simple:
	@echo "🚀 Running simple processor (single dataset)..."
	poetry run python -m bomr.process_bills

run-with-args:
	@echo "🚀 Running with custom arguments..."
	poetry run python -m bomr.process_bills --data-dir $(DATA_DIR) --output-dir $(OUTPUT_DIR)

# Example: make run-custom DATA_DIR=./my-data OUTPUT_DIR=./my-output
run-custom:
	@echo "🚀 Running full processor with custom directories..."
	poetry run python run_full_processor.py $(DATA_DIR) $(OUTPUT_DIR)

run-custom-simple:
	@echo "🚀 Running simple processor with custom directories..."
	poetry run python -m bomr.process_bills --data-dir $(DATA_DIR) --output-dir $(OUTPUT_DIR)

# Testing
test:
	@echo "🧪 Running tests..."
	poetry run python test_conversion.py

test-verbose:
	@echo "🧪 Running tests with verbose output..."
	poetry run python -v test_conversion.py

# Code quality
format:
	@echo "🎨 Formatting code with Black..."
	poetry run black bomr/ test_conversion.py

format-check:
	@echo "🎨 Checking code formatting..."
	poetry run black --check bomr/ test_conversion.py

lint:
	@echo "🔍 Running linting with Flake8..."
	poetry run flake8 bomr/ test_conversion.py

lint-fix:
	@echo "🔍 Running linting and attempting to fix issues..."
	poetry run flake8 bomr/ test_conversion.py --show-source

# Development tools
shell:
	@echo "🐚 Opening Poetry shell..."
	poetry shell

jupyter:
	@echo "📓 Starting Jupyter notebook..."
	poetry run jupyter notebook

# Data management
check-data:
	@echo "📁 Checking data directory..."
	@if [ -d "../../../bom-data/data-csvs" ]; then \
		echo "✅ Data directory found"; \
		echo "📊 CSV files found: $$(find ../../../bom-data/data-csvs -name "*.csv" | wc -l)"; \
	else \
		echo "❌ Data directory not found: ../../../bom-data/data-csvs"; \
		echo "💡 Please check the path or create test data"; \
	fi

list-data:
	@echo "📋 Available CSV files:"
	@find ../../../bom-data/data-csvs -name "*.csv" -exec basename {} \; 2>/dev/null | sort || echo "No data directory found"

# Output management
clean:
	@echo "🧹 Cleaning output files and cache..."
	rm -rf data/*.csv
	rm -rf bomr/__pycache__/
	rm -rf .pytest_cache/
	rm -rf *.pyc
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

clean-all: clean
	@echo "🧹 Deep clean including virtual environment..."
	poetry env remove --all 2>/dev/null || true

# Package management
check-deps:
	@echo "📦 Checking for outdated dependencies..."
	poetry show --outdated

update-deps:
	@echo "📦 Updating dependencies..."
	poetry update

build:
	@echo "📦 Building package..."
	poetry build

# Full processing pipeline
full-process: check-data run
	@echo "✅ Full processing pipeline completed!"
	@echo "📊 Output files:"
	@ls -la data/ 2>/dev/null || echo "No output directory found"

# Comparison with R version
compare-outputs:
	@echo "🔍 Comparing Python vs R outputs..."
	@if [ -f "data/bills_weekly.csv" ] && [ -f "../bills_weekly.csv" ]; then \
		echo "Comparing bills_weekly.csv files..."; \
		wc -l data/bills_weekly.csv ../bills_weekly.csv; \
	else \
		echo "Output files not found for comparison"; \
	fi

# Development workflow
dev-setup: dev-install
	@echo "🔧 Setting up development environment..."
	poetry run pre-commit install 2>/dev/null || echo "Pre-commit not configured"

dev-run: format lint test run
	@echo "✅ Development workflow completed!"

# Docker support (future)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t bomr-python .

docker-run:
	@echo "🐳 Running in Docker container..."
	docker run -v $(PWD)/../../../bom-data:/data bomr-python

# Utility commands
info:
	@echo "📋 Project Information"
	@echo "======================"
	@echo "Python version: $$(poetry run python --version)"
	@echo "Poetry version: $$(poetry --version)"
	@echo "Project directory: $$(pwd)"
	@echo "Virtual environment: $$(poetry env info --path)"
	@echo ""

status:
	@echo "📊 Project Status"
	@echo "=================="
	@echo "Dependencies installed: $$(poetry show | wc -l) packages"
	@echo "Data files available: $$(find ../../../bom-data/data-csvs -name "*.csv" 2>/dev/null | wc -l || echo "N/A")"
	@echo "Output files: $$(ls data/*.csv 2>/dev/null | wc -l || echo "0")"
	@echo ""

# Quick commands for common tasks
quick-test: test
quick-run: run
quick-clean: clean

# Examples for documentation
examples:
	@echo "📚 Usage Examples"
	@echo "=================="
	@echo "# Basic usage (full processor):"
	@echo "make run"
	@echo ""
	@echo "# Simple processor (single dataset):"
	@echo "make run-simple"
	@echo ""
	@echo "# Run with custom data directory:"
	@echo "make run-custom DATA_DIR=./my-data OUTPUT_DIR=./results"
	@echo ""
	@echo "# Development workflow:"
	@echo "make dev-run"
	@echo ""
	@echo "# Clean and run:"
	@echo "make clean && make run"
	@echo ""

# All-in-one commands
all: install format lint test run
	@echo "✅ Complete workflow executed successfully!"

ci: format-check lint test
	@echo "✅ CI pipeline completed!"