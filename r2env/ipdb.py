# ipdb stands for installed package database

import os
import shutil
import dploy
from r2env.tools import env_path

# srcdir=os.path.join(env_path(), 'src')
# dstdir=os.path.join(env_path(), 'dst')

def list():
	dstdir=os.path.join(env_path(), 'dst')
	res = []
	if os.path.isdir(dstdir):
		for d in os.listdir(dstdir):
			print(d)
		# list names of installed packages
	return res

def clean(pkgname):
	pkgdir=os.path.join(src, pkgname)
	if os.path.exists(pkgdir) and os.path.isdir(pkgdir):
		dploy.unstow('')
		shutil.rmtree(pkgdir)

def uninstall():
	res = []
	# list names of installed packages
	return res
