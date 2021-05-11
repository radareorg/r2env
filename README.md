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
packages available, but we may try to use python-version if
possible, so it don't depend on system packages.

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


How to install
--------------

r2env is available via PIP. (`pip install r2env`)

To build + install from source just run: `make`

Usage
-----

First of all you may want to initialize the `.r2env` directory somewhere with `cd .. ; r2env init`.

Listing available packages is done via `r2env list`.

Source packages are managed with the `add`, `rm`, `use` and `unused`.

For example: Installing radare2 (assumes @git version)

```
cd /tmp
r2env init
r2env add radare2
r2env use radare2@git
r2env shell r2 -v
```

r2pm vs r2env
-------------

r2env aims to provide a packaging for r2 with support for binary packages and for all major platforms.

r2pm focus on providing more packages, it's written in shellscript, so it doesnt run on windows and requires r2 to work.

Therefor r2env is kind of `nvm` from nodejs or `pyenv` from python. A way to run multiple different versions of r2 in the system.
