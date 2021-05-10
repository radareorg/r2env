import argparse
from r2env.tools import host_platform
from r2env.tools import user_home
from r2env.tools import env_path
from r2env.tools import get_size
from r2env.tools import autoversion
from r2env.tools import slurp
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
rm [pkg]  - remove pkg
add [pkg] - build and install given package
use [pkg] - set symlinks using dploy/stow into .r2env/prefix
version   - show version string
shell     - open a new shell with PATH env var set

"""

def enter_shell(r2path, args):
	newpath = os.path.join(r2path, "prefix", "bin")
	p = newpath + ":" + os.environ["PATH"]
	if len(args) == 0:
		print("enter [.r2env/prefix] shell")
	# macos
	os.environ["DYLD_LIBRARY_PATH"] = os.path.join(r2path, "prefix", "lib")
	os.environ["LD_LIBRARY_PATH"] = os.path.join(r2path, "prefix", "lib")
	os.environ["R2ENV_PATH"] = r2path
	dlp = os.path.join(r2path, "prefix", "lib")
	# os.system(os.environ["SHELL"])
	if len(args) == 0:
		os.system("export PATH='"+p+"';DYLD_LIBRARY_PATH="+dlp+" sh")
		print("leave [.r2env/prefix] shell")
	else:
		cmd = (" ".join(args))
		os.system("export PATH='"+p+"';DYLD_LIBRARY_PATH="+dlp+" " + cmd)
		

def add_package(pkg, profile):
	print("Adding package")
	pkg.build(profile)
	pkg.install()

def del_package(pkg, profile):
	print("Deleting package")
	pkg.clean(profile)

def cb_use(sauce, prefix):
	dploy.unstow([sauce], prefix)
	dploy.stow(  [sauce], prefix)

def cb_unuse(sauce, prefix):
	dploy.unstow([sauce], prefix)

def match_dst(args, cb):
	ret = False
	envp = env_path()
	if envp is None:
		print("No r2env defined")
		sys.exit(1)
	prefix = os.path.join(envp, "prefix")
	try:
		os.mkdir(prefix)
	except: pass
	for arg in args:
		dstdir = os.path.join(envp, "dst", arg)
		if os.path.isdir(dstdir):
			sauce = os.path.join(envp, "dst", arg, prefix[1:])
			cb(sauce, prefix)
			ret = True
	return ret

def match_pkg(pkgs, args, cb):
	envp = env_path()
	if envp is None:
		print("No r2env defined")
		sys.exit(1)
	targets = autoversion(args)
	for pkg in pkgs:
		name = pkg.header["name"]
		for profile in pkg.header["profiles"]:
			namever = name + "@" + profile["version"] + "#" + profile["platform"]
			if namever in args:
				cb(pkg, profile)
				return True
			namever = name + "@" + profile["version"]
			if namever in args:
				cb(pkg, profile)
				return True
	return False

def run_action(e, action, args):
	if action == "list":
		arg = args[0] if len(args) > 0 else ""
		if arg == "":
			print("-- Installed:")
		if arg.find("i") != -1 or arg == "":
			for pkg in e.installed_packages():
				pkgdir = os.path.join(env_path(), "dst", pkg)
				gitdir = os.path.join(env_path(), "src", pkg)
				ts = slurp(os.path.join(pkgdir, ".timestamp.txt"))
				sz = str(int(get_size(pkgdir) / (1024 * 1024)))
				sz2 = str(int(get_size(gitdir) / (1024 * 1024))) + " MB"
				padpkg = pkg.ljust(16);
				padsz = str(sz + " / " + sz2).ljust(16);
				print(padpkg + "  |  " + padsz + "  |  " + ts)
		if arg == "":
			print("")
			print("-- Available:")
		if arg.find("a") != -1 or arg == "":
			for pkg in e.available_packages():
				print(pkg.tostring())
	elif action == "init":
		e.init()
	elif action == "path":
		renv = env_path()
		if renv is not None:
			print(os.path.join(renv, "prefix", "bin"))
	elif action == "rm":
		envp = env_path()
		if envp is None:
			print("No r2env defined")
			sys.exit(1)
		for epkg in e.available_packages():
			for profile in epkg.header["profiles"]:
				name = epkg.header["name"]
				namever = name + "@" + profile["version"]
				if namever in args:
					del_package(epkg, profile)
					return True
		print("Cannot find pkg")
	elif action == "add":
		targets = autoversion(args)
		pkgs = e.available_packages()
		if not match_pkg(pkgs, targets, add_package):
			print("Cannot find pkg")
	elif action == "use":
		targets = autoversion(args)
		if not match_dst(targets, cb_use):
			print("Cannot find " + dstdir)
	elif action == "unuse":
		targets = autoversion(args)
		if not match_dst(targets, cb_unuse):
			print("Cannot find " + dstdir)
	elif action == "help":
		print(help_message)
	elif action == "shell":
		enter_shell(env_path(), args)
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
