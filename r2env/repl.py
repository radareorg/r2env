import argparse
from r2env.tools import host_platform
import r2env
import sys

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
shell     - open a new shell with PATH env var set

Environment:

R2ENV_HOME=~/.local/share/r2env
R2ENV_PATH=system,home
"""

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("action", help="run action", action="store")
	parser.add_argument("-v", "--version", help="show version string", action="store_true")
	args = parser.parse_args()
	
	e = r2env.R2Env()

	if args.version:
		print(e.version())
		return
	if args.action == "list":
		for pkg in e.installed_packages():
			print(pkg.tostring())
	elif args.action == "host":
		print(host_platform())
	elif args.action == "version":
		print(e.version())
	elif args.action == "search":
		for pkg in e.available_packages():
			print(pkg.tostring())
	else:
		print(help_message)
		sys.exit(1)
	#print("r2env")
	#print(e.version())
