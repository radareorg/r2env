PYTHON?=python3
PIP?=pip3

all:
	$(PIP) install .

pub:
	rm -rf dist
	$(PYTHON) setup.py sdist
	twine upload --repository=pypi --verbose dist/*

install:
	$(PIP) install .

uninstall:
	$(PIP) uninstall r2env

.PHONY: all clean pub install uninstall
