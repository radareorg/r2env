PYTHON?=python3

all:
	$(PYTHON) setup.py build
	$(MAKE) install

pub:
	twine upload --repository-url https://upload.pypi.org/legacy/ --verbose dist/*

install:
	sudo $(PYTHON) setup.py install

uninstall:
	yes | sudo pip uninstall r2env

.PHONY: all pub install uninstall
