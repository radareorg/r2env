import os
import sys
import r2env
import r2env.tools

def build_r0(profile):
	pkgver="r0" + "@" + profile["version"]
	envp = r2env.tools.env_path()
	if not envp:
		return False
	srcdir=os.path.join(envp, "src")
	gitdir=os.path.join(envp, "src", pkgver)
	dstdir=os.path.join(envp, "dst", pkgver)
	logdir=os.path.join(envp, "log")
	logfil=os.path.join(logdir, "r0.txt")
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
		rc = os.system("cd '" + gitdir + "' && git reset --hard ; git checkout master ; git reset --hard && git pull")
	else:
		rc = os.system("git clone https://github.com/radareorg/r0 '"+gitdir+"'")
	if rc != 0:
		print("Clone failed")
		return False
	if "tag" in profile:
		os.system("git checkout " + str(profile["tag"]))
	print("Building ...")
	print("tail -f "+logfil)
	rc = os.system("(cd " + gitdir + " &&  git clean -xdf && make -j4 PREFIX="+prefix+" 2>&1 && make install PREFIX="+prefix+" DESTDIR="+dstdir+")") # > " + logfil)
	if rc == 0:
		# clone r0 in srcdir
		os.system("date > "+dstdir+"/.timestamp.txt")
		os.system("cd " +gitdir+ " && git log |head -n1> "+dstdir+"/.commit.txt")
	else:
		print("Build failed")
		sys.exit(1)

def install_r0():
	print("INSTALL")

r0profiles = [
	{
		"platform": "any",
		"version": "git",
		"source": "https://github.com/radareorg/r0",
		"needs": ["git", "make" ]
	}
]

class R0(r2env.Package):
	header = {
		"name": "r0",
		"description": "r0, aka ired, aka minimalistic hex editor",
		"profiles": r0profiles
	}
	def build(self, profile):
		build_r0(profile)
