import os

# Detect git, meson, ninja, patch, unzip make, gcc, ...

def host_platform():
	if os.name == "nt":
		return "w64"
	return "unix"

def git_clone(url):
	os.system("git clone " + url)

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
