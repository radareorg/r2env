PYTHON?=python3

all:
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py build
	$(MAKE) install

clean:
	sudo rm -rf dist r2env.egg-info

pub:
	twine upload --repository-url https://upload.pypi.org/legacy/ --verbose dist/*

install:
	sudo $(PYTHON) setup.py install

uninstall:
	yes | sudo pip uninstall r2env
	sudo rm -f /usr/local/bin/r2env
	sudo rm -f /usr/bin/r2env

.PHONY: all clean pub install uninstall
