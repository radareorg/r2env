PYTHON?=python3

all:
	pip install .

pub:
	twine upload --repository-url https://upload.pypi.org/legacy/ --verbose dist/*

install:
	pip install .

uninstall:
	pip uninstall r2env

.PHONY: all clean pub install uninstall
