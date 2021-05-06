from r2env.package import Package
from r2env.repl import main

def load_packages(cfg):
	from r2env.db import Radare2
	pkgs = []
	pkgs.append(Radare2(cfg))
	return pkgs

help_message = """
Usage: r2env [action] [args...]
Actions:

list      - list installed packages and their size git size, install size
files     - list files owned by a package
search    - search for packages in the database
install   - calls pkg.link after pkg.install
uninstall - uninstall the given package(s)
update    - update 
link      - symlink the package to make it available in $PATH
unlink    - remove symlinks to uninstall a package
version   - show version string

Environment:

R2ENV_HOME=~/.local/share/r2env
"""

cfg = {
	"srcdir": "", # depends on the pkg
	"linkdir": "/usr",
	"envdir": 123,
	"prefix": "",
}

class R2Env:
	def __init__(self):
		self.db = load_packages(cfg)
	def help(self):
		return help_message
	def du(self):
		return ""
	def version(self):
		return "0.1.0"
	def packages(self):
		return self.db
