PYTHON?=python3

all:
	pip install .

pub:
	rm -rf dist
	$(PYTHON) setup.py sdist
	twine upload --repository=pypi --verbose dist/*

install:
	pip install .

uninstall:
	pip uninstall r2env

.PHONY: all clean pub install uninstall
