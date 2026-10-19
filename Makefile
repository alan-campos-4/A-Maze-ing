NAME = a_maze_ing.py
CONF = config.txt

VENV = .venv
BIN = $(VENV)/bin
PYTHON = python3
MAZE_PACKAGE = mazegen

GREEN = "\033[0;32m"
RED   = "\033[0;31m"
BLUE  = "\033[0;33m"
END   = "\033[0m"

.PHONY: install run debug clean lint lint-strict build venv fclean analyze

.DEFAULT: help

help:
	@echo "  make install ........ Install the project dependencies"
	@echo "  make run ............ Execute the main script"
	@echo "  make debug .......... Execute the main script in debug mode"
	@echo "  make clean .......... Delete the extra folders"
	@echo "  make lint ........... Examine the project with flake and mypy"
	@echo ""
	@echo "  make venv ........... Create the virtual environment"
	@echo "  make fclean ......... Delete the virtual environment folder"
	@echo "  make analyze ........ Analyze the output file"

install:
	@echo "Installing dependencies..."
	@if $(BIN)/pip install -r requirements.txt; then \
		echo $(GREEN)"Installation complete."$(END); \
	else \
		echo $(RED)"Installation failed."$(END); \
	fi

run:
	@if [ -d "./$(VENV)" ]; then \
		$(BIN)/$(PYTHON) $(NAME) $(CONF); \
	else \
		$(PYTHON) $(NAME) $(CONF); \
	fi

debug:
	@if [ -d "./$(VENV)" ]; then \
		$(BIN)/$(PYTHON) -m pdb $(NAME) $(CONF); \
	else \
		$(PYTHON) -m pdb $(NAME) $(CONF); \
	fi

lint:
	@-flake8 . --exclude .git,.mypy_cache,.venv,__pycache__
	@-mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	@-flake8 . --exclude .git,.mypy_cache,.venv,__pycache__
	@-mypy . --strict --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

clean:
	@-find . -type f -name "*.pyc" -delete
	@-find . -path '*/__pycache__*' -delete
	@-find . -path '*/.mypy_cache*' -delete
	@-rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/
	@echo $(RED)"Directory cleared."$(END)

build:
	$(BIN)/$(PYTHON) -m build $(MAZE_PACKAGE) -o .

venv:
	@if [ ! -d "./$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
		echo $(GREEN)"Venv created."$(END); \
		echo "Activate with source $(BIN)/activate"; \
		echo "Exit with deactivate."; \
	else \
		echo "Venv folder already exists."; \
	fi

fclean: clean
	@if [ -d "./$(VENV)" ]; then \
		rm -rf $(VENV); \
		echo $(RED)"Venv deleted."$(END); \
	else \
		echo "Venv folder not found."; \
	fi

analyze:
	@-$(BIN)/$(PYTHON) maze_analyzer.py maze.txt

