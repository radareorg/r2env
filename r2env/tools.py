import os
import sys

# Detect git, meson, ninja, patch, unzip make, gcc, ...

def autoversion(args):
	res = []
	for arg in args:
		if arg.find("@") == -1:
			res.append(arg + "@git")
		else:
			res.append(arg)
	return res

def host_platform():
	if os.name == "nt":
		return "w64"
	if os.file.exists("/default.prop"):
		return "android"
	return "unix"

def user_home():
	if int(sys.version[0]) < 3:
		return os.environ['HOME']
	from pathlib import Path
	return str(Path.home())

def slurp(f):
	try:
		f = open(f,"r")
		return str(f.read()).strip()
	except:
		return ""

def env_path():
	oldcwd = os.getcwd()
	while True:
		envdir = os.path.join(oldcwd, ".r2env")
		if os.path.isdir(envdir):
			return envdir
		os.chdir("..")
		cwd = os.getcwd()
		if oldcwd == cwd:
			return None
		oldcwd = cwd
	print("Run 'r2env init' first")
	# walk directories up
	return None

def git_clone(url):
	os.system("git clone " + url + " " + dstdir)

# XXX this is not going to work on windows
def check_tool(tool):
	if tool == "git":
		return os.system("git --help > /dev/null") == 0
	elif tool == "unzip":
		return os.system("unzip -h > /dev/null") == 0
	return False

def check(tools):
	for tool in tools:
		found = check_tool(tool)
		if found:
			print("found " + tool)
		else:
			print("oops  " + tool)

def get_size(start_path = '.'):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			# skip if it is symbolic link
			if not os.path.islink(fp):
				total_size += os.path.getsize(fp)
	return total_size
