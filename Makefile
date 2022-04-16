.PHONY: style types test quality init check

PY_VER=python3.8
PY_VER_SHORT=py$(shell echo $(PY_VER) | sed 's/[^0-9]*//g')
VENV=env
PACKAGE_NAME=dicom_img_anon
CODE_PATHS=$(PACKAGE_NAME) tests setup.py util.py
LINE_LEN=120
PYTHON=$(VENV)/bin/python3
COVERAGE=$(VENV)/bin/coverage

style: $(VENV)
	$(PYTHON) -m autoflake -r -i --remove-all-unused-imports --remove-unused-variables $(CODE_PATHS)
	$(PYTHON) -m isort $(CODE_PATHS) --line-length $(LINE_LEN) 
	$(PYTHON) -m autopep8 -a -r -i --max-line-length=$(LINE_LEN) $(CODE_PATHS) 
	$(PYTHON) -m black --line-length $(LINE_LEN) --target-version $(PY_VER_SHORT) $(CODE_PATHS)

types: node_modules
	npx --no-install pyright $(CODE_PATHS) -p pyrightconfig.json

test: $(VENV)
	$(COVERAGE) run --source $(PACKAGE_NAME) -m pytest tests $(CIRCLECI_TEST_FLAGS) -s

quality: $(VENV)
	$(PYTHON) -m black --check $(CODE_PATHS) --line-length=120
	$(PYTHON) -m flake8 $(CODE_PATHS)

$(VENV):
	$(MAKE) init

init:
	python3 -m virtualenv -p $(PY_VER) $(VENV)
	$(VENV)/bin/pip install -e .[dev]

node_modules:
	npm install

coverage:
	$(MAKE) test
	for command in xml html report ; do \
		$(COVERAGE) $$command --omit=$(PACKAGE_NAME)/version.py ; \
	done

check:
	$(MAKE) style
	$(MAKE) quality
	$(MAKE) types
	$(MAKE) coverage

circleci:
	circleci local execute --job run_check -e CODECOV_TOKEN=$(CODECOV_TOKEN)

clean:
	rm -rf \
		node_modules \
		env \
		*.egg-info \
		__pycache__ \
		.pytest_cache \
		.coverage \
		coverage.xml

reset:
	$(MAKE) clean
	$(MAKE) check
