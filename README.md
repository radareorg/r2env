# r2env

[![CI](https://github.com/radareorg/r2env/actions/workflows/ci.yml/badge.svg)](https://github.com/radareorg/r2env/actions/workflows/ci.yml)

Create self-contained environments with multiple versions of radare2
and plugins, make it easy to switch between them.

* Build from source or install the system package if available.

## Installation

r2env is available via PIP.

* `pip install -U -f r2env`

If you want to try it directly from source.

* `pip install .`

## Usage

First we need to initialize the working directory:

```
r2env init
```

Listing available packages is done via `r2env list`.

Source packages are managed with the `add`, `rm`, `use` and `unused`.

For example: Installing radare2 (assumes @git version)

```
r2env init
r2env add radare2
r2env use radare2@git
r2env shell "r2 -v"
```

## Help

```
Usage: r2env [-flags] [action] [args...]

Flags:

-h, --help     - show this help
-v, --version  - display r2env version
-m, --meson    - use meson instead of acr
-p, --package  - install the dist package instead of building
-l, --list     - list available and installed packages

Actions:

init           - create ~/.r2env directory
config         - display current .r2env settings
add [pkg]      - build and install given package. See -p and -m
use [pkg]      - use r2 package defined. pkg should be a release version or git.
rm [pkg]       - remove package from ~/.r2env
path           - show path of current r2 in use
version        - show version of r2env
versions       - list installed packages
list           - list all packages available to r2env
shell          - enter a new shell with PATH env var set
purge          - remove ~/.r2env

Environment

R2ENV_PATH     - specify different path other than ~/.r2env

```

## r2pm vs r2env

r2env aims to provide a packaging for r2 with support for binary packages and for all major platforms.

r2pm focus on providing more packages, it's written in shellscript, so it doesnt run on windows and requires r2 to work.

Therefor r2env is kind of `nvm` from nodejs or `pyenv` from python. A way to run multiple different versions of r2 in the system.

This repository contains the tool available via pip to install
and manage multiple versions of radare2 and its plugins.

r2-tools doesn't conflict with r2pm in the sense that it's not
going to support all the packages and plugins and it's

