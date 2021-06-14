# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    setup_requires=['pbr'],
    pbr=True,
    data_files=[('config', ['r2env/config/config.json', 'r2env/config/profiles.json'])]
)
