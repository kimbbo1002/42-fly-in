PYTHON = poetry run python3
MAIN = fly_in.py
VENV = .venv
CONFIG ?=

install:
	poetry install

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint:
	poetry run flake8
	poetry run mypy . --explicit-package-bases --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	poetry run flake8
	poetry run mypy . --explicit-package-bases --strict

clean:
	rm -rf `find . -type d -name "__pycache__"`
	rm -rf .mypy_cache

fclean: clean
	rm -rf poetry.lock

.PHONY: install run debug clean lint lint-strict fclean