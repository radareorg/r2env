r2env
=====

[![CI](https://github.com/radareorg/r2env/actions/workflows/ci.yml/badge.svg)](https://github.com/radareorg/r2env/actions/workflows/ci.yml)

This repository contains the tool available via pip to install
and manage multiple versions of radare2 and its plugins.

r2-tools doesn't conflict with r2pm in the sense that it's not
going to support all the packages and plugins and it's

r2env supports source and binary packages.

Dependencies
------------

* r2env should be self contained

Some tools may be used if installed in the system, making some
packages available, but we may try to use python-version if possible, so we dont depend on system packages.

* git
* unzip
* make
* patch

Package description
-------------------
INI, JSON or python class, loaded at runtime, but it is k=v stuff

* name: iaito
* platform: windows
* version: 5.2.1
* source: https://path/to/zip

Actions
-------
* install / uninstall
* link / unlink
* update - pip install -U r2env
* upgrade - upgrade r2 and all the deps in sync


sss to install
--------------

r2env is available via PIP.

```
pip install r2env
```

Usage
-----

Installing radare2

```
r2env install radare2
```

r2pm vs r2env
-------------

