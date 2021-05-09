all:
	python3 setup.py build
	sudo python3 setup.py install

pub:
	twine upload --repository-url https://upload.pypi.org/legacy/ --verbose dist/*
