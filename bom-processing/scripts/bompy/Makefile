# Bills of Mortality Data Processing
# ==================================

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Directories
DATA_RAW_DIR := data-raw
DATA_OUTPUT_DIR := data
SRC_DIR := src
LOGS_DIR := logs
NOTEBOOKS_DIR := notebooks

##@ Setup Commands

.PHONY: install
install: ## Install dependencies with Poetry
	@echo -e "$(CYAN)Installing dependencies...$(RESET)"
	poetry install

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo -e "$(CYAN)Installing development dependencies...$(RESET)"
	poetry install --with dev

.PHONY: setup
setup: install ## Complete setup (install dependencies)
	@echo -e "$(GREEN) Setup complete!$(RESET)"

##@ Processing Commands

.PHONY: process-all
process-all: ## Process all CSV files and generate PostgreSQL outputs
	@echo -e "$(CYAN) Processing all Bills of Mortality data...$(RESET)"
	@mkdir -p $(LOGS_DIR)
	poetry run python process_all_data.py
	@echo -e "$(GREEN) Processing complete! Check $(DATA_OUTPUT_DIR)/ for outputs$(RESET)"
	@echo -e "$(YELLOW) Logs saved to $(LOGS_DIR)/$(RESET)"

.PHONY: test-bills
test-bills: ## Test bills processor with sample data
	@echo -e "$(CYAN) Testing bills processor...$(RESET)"
	@mkdir -p $(LOGS_DIR)
	poetry run python tests/test_bills_processor.py

.PHONY: test-schema
test-schema: ## Test schema alignment with sample data
	@echo -e "$(CYAN) Testing schema alignment...$(RESET)"
	@mkdir -p $(LOGS_DIR)
	poetry run python tests/test_schema_alignment.py

##@ Data Management

.PHONY: clean-data
clean-data: ## Clean output data directory
	@echo -e "$(YELLOW) Cleaning output data...$(RESET)"
	rm -rf $(DATA_OUTPUT_DIR)/*.csv
	@echo -e "$(GREEN) Output data cleaned$(RESET)"

.PHONY: clean-logs
clean-logs: ## Clean log files
	@echo -e "$(YELLOW) Cleaning log files...$(RESET)"
	rm -rf $(LOGS_DIR)/*.log
	rm -rf $(LOGS_DIR)/*.gz
	@echo -e "$(GREEN) Log files cleaned$(RESET)"

.PHONY: show-logs
show-logs: ## Show recent log files
	@echo -e "$(CYAN) Recent Log Files:$(RESET)"
	@if [ -d "$(LOGS_DIR)" ]; then \
		find $(LOGS_DIR) -name "*.log" -type f -exec stat -f "%m %N" {} \; | sort -n | tail -5 | while read time file; do \
			size=$$(du -h "$$file" | cut -f1); \
			echo -e "  $$(basename $$file): $$size"; \
		done; \
	else \
		echo -e "$(RED)No logs directory found$(RESET)"; \
	fi

.PHONY: tail-logs
tail-logs: ## Tail the most recent log file
	@echo -e "$(CYAN) Tailing most recent log...$(RESET)"
	@if [ -d "$(LOGS_DIR)" ]; then \
		latest_log=$$(find $(LOGS_DIR) -name "*.log" -type f -exec stat -f "%m %N" {} \; | sort -n | tail -1 | cut -d' ' -f2); \
		if [ -n "$$latest_log" ]; then \
			echo -e "$(GREEN)Following: $$latest_log$(RESET)"; \
			tail -f "$$latest_log"; \
		else \
			echo -e "$(RED)No log files found$(RESET)"; \
		fi; \
	else \
		echo -e "$(RED)No logs directory found$(RESET)"; \
	fi

.PHONY: show-stats
show-stats: ## Show statistics for generated data files
	@echo -e "$(CYAN) Data Statistics:$(RESET)"
	@if [ -d "$(DATA_OUTPUT_DIR)" ]; then \
		echo -e "$(GREEN)Output Files:$(RESET)"; \
		for file in $(DATA_OUTPUT_DIR)/*.csv; do \
			if [ -f "$$file" ]; then \
				records=$$(tail -n +2 "$$file" | wc -l | tr -d ' '); \
				size=$$(ls -lh "$$file" | awk '{print $$5}'); \
				echo -e "  $$(basename $$file): $$records records ($$size)"; \
			fi; \
		done; \
	else \
		echo -e "$(RED)No data directory found. Run 'make process-all' first.$(RESET)"; \
	fi

.PHONY: validate-outputs
validate-outputs: ## Validate generated CSV files
	@echo -e "$(CYAN) Validating output files...$(RESET)"
	@for file in parishes.csv weeks.csv years.csv all_bills.csv; do \
		if [ -f "$(DATA_OUTPUT_DIR)/$$file" ]; then \
			records=$$(tail -n +2 "$(DATA_OUTPUT_DIR)/$$file" | wc -l | tr -d ' '); \
			echo -e "$$file: $$records records"; \
		else \
			echo -e "$$file: File not found"; \
		fi; \
	done
	@echo -e "$(GREEN)Validation complete!$(RESET)"

.PHONY: check-coverage
check-coverage: ## Analyze data coverage by parish and year
	@echo -e "$(CYAN)Analyzing data coverage...$(RESET)"
	@if [ ! -f "$(DATA_OUTPUT_DIR)/all_bills.csv" ]; then \
		echo -e "$(RED)Error: No processed data found. Run 'make process-all' first.$(RESET)"; \
		exit 1; \
	fi
	poetry run python analyze_data_coverage.py
	@echo -e "$(GREEN)Coverage analysis complete!$(RESET)"

##@ Analysis Commands

.PHONY: notebooks
notebooks: ## Launch Jupyter Lab for data analysis
	@echo -e "$(CYAN)Launching Jupyter Lab...$(RESET)"
	@mkdir -p $(NOTEBOOKS_DIR)
	poetry run jupyter lab --notebook-dir="$(PWD)/$(NOTEBOOKS_DIR)"

.PHONY: notebook-run-all
notebook-run-all: ## Execute all analysis notebooks
	@echo -e "$(CYAN)Running all analysis notebooks...$(RESET)"
	@for notebook in $(NOTEBOOKS_DIR)/*.ipynb; do \
		if [ -f "$$notebook" ]; then \
			echo -e "$(YELLOW)Running $$(basename $$notebook)...$(RESET)"; \
			poetry run jupyter nbconvert --to notebook --execute --inplace "$$notebook" || echo -e "$(RED)Failed to run $$(basename $$notebook)$(RESET)"; \
		fi; \
	done
	@echo -e "$(GREEN)All notebooks executed$(RESET)"

.PHONY: notebook-convert
notebook-convert: ## Convert notebooks to HTML reports
	@echo -e "$(CYAN)Converting notebooks to HTML...$(RESET)"
	@mkdir -p $(NOTEBOOKS_DIR)/reports
	@for notebook in $(NOTEBOOKS_DIR)/*.ipynb; do \
		if [ -f "$$notebook" ]; then \
			echo -e "$(YELLOW)Converting $$(basename $$notebook)...$(RESET)"; \
			poetry run jupyter nbconvert --to html "$$notebook" --output-dir=$(NOTEBOOKS_DIR)/reports; \
		fi; \
	done
	@echo -e "$(GREEN)HTML reports generated in $(NOTEBOOKS_DIR)/reports/$(RESET)"

.PHONY: notebook-clean
notebook-clean: ## Clean notebook outputs and checkpoints
	@echo -e "$(YELLOW)Cleaning notebook outputs...$(RESET)"
	@find $(NOTEBOOKS_DIR) -name "*.ipynb" -exec jupyter nbconvert --clear-output --inplace {} \;
	@find $(NOTEBOOKS_DIR) -name ".ipynb_checkpoints" -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(NOTEBOOKS_DIR)/reports/
	@echo -e "$(GREEN)Notebook outputs cleaned$(RESET)"

.PHONY: notebook-info
notebook-info: ## Show information about available notebooks
	@echo -e "$(CYAN)Available Analysis Notebooks:$(RESET)"
	@if [ -d "$(NOTEBOOKS_DIR)" ]; then \
		for notebook in $(NOTEBOOKS_DIR)/*.ipynb; do \
			if [ -f "$$notebook" ]; then \
				name=$$(basename "$$notebook" .ipynb); \
				size=$$(du -h "$$notebook" | cut -f1); \
				echo -e "  $$name ($$size)"; \
				if command -v jupyter >/dev/null 2>&1; then \
					cells=$$(poetry run jupyter nbconvert --to notebook --stdout "$$notebook" 2>/dev/null | grep -o '"cell_type":' | wc -l | tr -d ' '); \
					if [ "$$cells" -gt 0 ]; then \
						echo -e "      $$cells cells"; \
					fi; \
				fi; \
			fi; \
		done; \
	else \
		echo -e "$(RED)No notebooks directory found$(RESET)"; \
	fi

##@ Development Commands

.PHONY: lint
lint: ## Run linting with black and isort
	@echo -e "$(CYAN)Linting code...$(RESET)"
	poetry run black --check $(SRC_DIR)/ *.py
	poetry run isort --check-only $(SRC_DIR)/ *.py

.PHONY: format
format: ## Format code with black and isort
	@echo -e "$(CYAN)Formatting code...$(RESET)"
	poetry run black $(SRC_DIR)/ *.py
	poetry run isort $(SRC_DIR)/ *.py
	@echo -e "$(GREEN)Code formatted$(RESET)"

.PHONY: typecheck
typecheck: ## Run type checking with mypy
	@echo -e "$(CYAN)Type checking...$(RESET)"
	poetry run mypy $(SRC_DIR)/

.PHONY: test
test: ## Run tests with pytest
	@echo -e "$(CYAN)Running tests...$(RESET)"
	poetry run pytest tests/ -v

.PHONY: check
check: lint typecheck ## Run all code quality checks
	@echo -e "$(GREEN)All checks passed$(RESET)"

##@ Information Commands

.PHONY: info
info: ## Show project information
	@echo -e "$(CYAN)Bills of Mortality Processing Pipeline$(RESET)"
	@echo -e "$(GREEN)Version:$(RESET) 1.0.0"
	@echo -e "$(GREEN)Python:$(RESET) $$(poetry run python --version)"
	@echo -e "$(GREEN)Poetry:$(RESET) $$(poetry --version)"
	@echo ""
	@echo -e "$(YELLOW)Input Data:$(RESET)"
	@if [ -d "$(DATA_RAW_DIR)" ]; then \
		csv_count=$$(find $(DATA_RAW_DIR) -name "*.csv" | wc -l | tr -d ' '); \
		echo -e "  $(DATA_RAW_DIR)/: $$csv_count CSV files"; \
	else \
		echo -e "  $(RED)$(DATA_RAW_DIR)/ directory not found$(RESET)"; \
	fi
	@echo ""
	@echo -e "$(YELLOW)Output Data:$(RESET)"
	@if [ -d "$(DATA_OUTPUT_DIR)" ]; then \
		csv_count=$$(find $(DATA_OUTPUT_DIR) -name "*.csv" | wc -l | tr -d ' '); \
		echo -e "  $(DATA_OUTPUT_DIR)/: $$csv_count CSV files"; \
	else \
		echo -e "  $(RED)$(DATA_OUTPUT_DIR)/ directory not found$(RESET)"; \
	fi

.PHONY: psql-commands
psql-commands: ## Show PostgreSQL import commands
	@echo -e "$(CYAN)PostgreSQL Import Commands:$(RESET)"
	@echo ""
	@echo -e "$(GREEN)-- Import in this order (respects foreign keys):$(RESET)"
	@echo -e "\\COPY years FROM 'years.csv' DELIMITER ',' CSV HEADER;"
	@echo -e "\\COPY parishes FROM 'parishes.csv' DELIMITER ',' CSV HEADER;"
	@echo -e "\\COPY weeks FROM 'weeks.csv' DELIMITER ',' CSV HEADER;"
	@echo -e "\\COPY all_bills FROM 'all_bills.csv' DELIMITER ',' CSV HEADER;"
	@echo ""
	@echo -e "$(YELLOW)Note: Ensure your PostgreSQL tables match the DDL schema$(RESET)"

##@ Utility Commands

.PHONY: copy-data
copy-data: 
	@echo -e "Copying data from the bo-data directory to the bompy directory..."
	cp ../../../bom-data/data-csvs/*.csv data-raw/
	@echo -e "Finished copying unprocessed data."

.PHONY: clean
clean: clean-data clean-logs notebook-clean ## Clean all generated files
	@echo -e "$(YELLOW)Cleaning project...$(RESET)"
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	@echo -e "$(GREEN)Project cleaned$(RESET)"

.PHONY: reset
reset: clean ## Reset project to clean state
	@echo -e "$(YELLOW)Resetting project...$(RESET)"
	rm -rf .venv/
	@echo -e "$(GREEN)Project reset. Run 'make setup' to reinstall$(RESET)"

.PHONY: help
help: ## Show this help message
	@echo -e "$(CYAN)Bills of Mortality Processing Pipeline$(RESET)"
	@echo -e "$(GREEN)=====================================$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(YELLOW)Quick Start:$(RESET)"
	@echo -e "  1. make setup          # Install dependencies"
	@echo -e "  2. make copy-data      # Copy over raw data for processing"
	@echo -e "  3. make process-all    # Process all data"
	@echo -e "  4. make show-stats     # View results"
	@echo -e "  5. make notebooks      # Launch Jupyter for analysis"
	@echo -e "  6. make psql-commands  # Get import commands"
