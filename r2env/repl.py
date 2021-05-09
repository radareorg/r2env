import argparse
from r2env.tools import host_platform
from r2env.tools import user_home
from r2env.tools import env_path
import r2env
import dploy
import sys
import os

help_message = """
Usage: r2env [action] [args...]
Actions:

init      - create .r2env in current directory
path      - display current .r2env settings
list      - list packages
add [pkg] - build and install given package
use [pkg] - set symlinks using dploy/stow into .r2env/prefix
version   - show version string
shell     - open a new shell with PATH env var set

"""

def enter_shell(r2path):
	sys.path.insert(0, r2path + "/prefix/bin")
	#newpath = r2path + "/prefix/bin:" + os.environ["PATH"]
	#os.environ["PATH"] = newpath
	print("enter [.r2env/prefix] shell")
	os.system(os.environ["SHELL"])
	print("leave [.r2env/prefix] shell")

def add_package(pkg):
	print("Adding package")
	options = []
	pkg.build(options)
	pkg.install()

def run_action(e, action, args):
	if action == "list":
		print("## Installed:")
		for pkg in e.installed_packages():
			print(pkg.tostring())
		print("## Available:")
		for pkg in e.available_packages():
			print(pkg.tostring())
	elif action == "init":
		e.init()
	elif action == "path":
		print("home " + user_home())
		print("cwdp " + os.getcwd())
		renv = env_path()
		if renv is not None:
			print("renv " + renv)
			print("path " + renv + "/bin")
	elif action == "add":
		for pkg in e.available_packages():
			name = pkg.header["name"]
			if name in args:
				add_package(pkg)
				return True
			for profile in pkg.header["profiles"]:
				namever = name + "@" + profile["version"]
				if namever in args:
					add_package(pkg)
					return True
		print("Cannot find pkg")
	elif action == "use":
		envp = env_path()
		prefix = os.path.join(envp, "prefix")
		try:
			os.mkdir(prefix)
		except: pass
		for arg in args:
			dstdir = os.path.join(envp, "dst", arg)
			if os.path.isdir(dstdir):
				print(dstdir)
				print(prefix)
				os.system("dploy stow '" + dstdir + "' '" + prefix + "'")
				# dploy.stow(dstdir, prefix)
			else:
				print("Cannot find " + dstdir)
	elif action == "shell":
		enter_shell(env_path())
	elif action == "host":
		print(host_platform())
	elif action == "version":
		print(e.version())
	else:
		return False
	return True

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("action", help="run action (see 'r2env help' for more details).", action="store")
	parser.add_argument("-v", "--version", help="show version string", action="store_true")
	parser.add_argument('args', metavar='N', nargs='*', type=str, help='arguments ...')
	args = parser.parse_args()
	
	e = r2env.R2Env()

	if args.version:
		print(e.version())
		return
	if not run_action(e, args.action, args.args):
		print(help_message)
		sys.exit(1)
	sys.exit(0)
	#print("r2env")
	#print(e.version())
