import r2env
import r2env.tools
import os
import sys
import dploy
from r2env.tools import env_path

r2profiles = [
	{
		"version": "git",
		"platform": "unix",
		"source": "https://github.com/radareorg/radare2",
		"needs": [ "git", "make" ]
	},
	{
		"version": "git",
		"platform": "w64",
		"source": "https://github.com/radareorg/radare2",
		"needs": [ "git", "meson", "ninja" ]
	},
	{
		"version": "5.2.1",
		"platform": "unix",
		"source": "https://github.com/radareorg/radare2",
		"tag": "5.2.1",
		"needs": [ "git", "meson", "ninja" ]
	}
]

def build_radare2(profile):
	envp = env_path()
	srcdir=os.path.join(envp, "src")
	gitdir=os.path.join(envp, "src", "radare2@git")
	dstdir=os.path.join(envp, "dst", "radare2@git")
	logdir=os.path.join(envp, "log")
	logfil=os.path.join(logdir, "radare2.txt")
	prefix=os.path.join(envp, "prefix")

	rc = 0
	try:
		os.mkdir(srcdir)
	except: pass
	try:
		os.mkdir(dstdir)
	except: pass
	try:
		os.mkdir(logdir)
	except: pass
	if os.path.isdir(gitdir):
		rc = os.system("cd '" + gitdir + "' && git reset --hard; git pull")
	else:
		rc = os.system("cd " + srcdir + ";git clone --depth=1 https://github.com/radareorg/radare2 'radare2@git'")
	if rc != 0:
		print("Clone failed")
		return False
	if profile.tag is not None:
		print("Using TAG")
		print("git reset --hard " + str(profile.tag))
	print("Building ...")
	print("tail -f "+logfil)
	os.system("(cd " + srcdir + "/radare2; git clean -xdf; rm -rf shlr/capstone; ./configure --prefix="+dstdir+" 2>&1;make -j4 2>&1 && make install) > " + logfil)
	# clone radare2 in srcdir
	os.system("date > "+dstdir+"/.timestamp.txt")
	os.system("git log |head -n1> "+dstdir+"/.commit.txt")
	

class Radare2(r2env.Package):
	header = {
		"name": "radare2",
		"profiles": r2profiles
	}
	def build(self, profile):
		print("Building radare2")
		build_radare2(profile)
		print("magic done")

