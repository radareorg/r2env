import r2env
import r2env.tools
import os
import sys
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
	}
]

def build_radare2(options):
	envp = env_path()
	srcdir=os.path.join(envp, "src")
	dstdir=os.path.join(envp, "dst")
	logdir=os.path.join(envp, "log")
	logfil=os.path.join(logdir, "radare2.txt")
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
	if os.path.isdir(os.path.join(srcdir, "radare2")):
		rc = os.system("cd " + srcdir + ";git pull")
	else:
		rc = os.system("cd " + srcdir + ";git clone --depth=1 https://github.com/radareorg/radare2 radare2")
	if rc != 0:
		print("Clone failed")
	print("Building ...")
	print("tail -f "+logfil)
	os.system("(cd " + srcdir + "/radare2; git clean -xdf; rm -rf shlr/capstone; ./configure --prefix="+dstdir+";make -j4;make install) > " + logfil)
	# clone radare2 in srcdir
	
	os.system("git clone https://")
	# install in dstdir

def install_radare2():
	print("INSTALL")


class Radare2(r2env.Package):
	header = {
		"name": "radare2",
		"profiles": r2profiles
	}
	def build(self, options):
		print("Building radare2")
		build_radare2(options)
		print("magic done")
	def install(self):
		install_radare2()

