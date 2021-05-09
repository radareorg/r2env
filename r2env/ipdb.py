# ipdb stands for installed package database

import os
import shutil
import dploy
from r2env.tools import env_path

# srcdir=os.path.join(env_path(), 'src')
# dstdir=os.path.join(env_path(), 'dst')

def list():
	envdir = env_path()
	if envdir is None:
		return []
	dstdir = os.path.join(envdir, "dst")
	res = []
	if os.path.isdir(dstdir):
		for d in os.listdir(dstdir):
			res.append(d)
	return res

def clean(pkgname):
	srcdir=os.path.join(env_path(), "src")
	pkgdir=os.path.join(srcdir, pkgname)
	if os.path.exists(pkgdir) and os.path.isdir(pkgdir):
		try:
			print("unstow " + pkgdir)
			dploy.unstow(pkgdir, prefix)
			# shutil.rmtree(pkgdir)
		except:
			pass
	else:
		print("Nothing to do")

def uninstall():
	res = []
	# list names of installed packages
	return res
