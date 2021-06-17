PYTHON?=python3

all:
	pip install .

pub:
	rm -rf dist
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py build
	twine upload --repository-url https://upload.pypi.org/legacy/ --verbose dist/*
	#twine upload --repository=r2env --verbose dist/*

install:
	pip install .

uninstall:
	pip uninstall r2env

.PHONY: all clean pub install uninstall
