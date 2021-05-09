from r2env.package import Package
from r2env.repl import main
import r2env.ipdb
import os


def load_packages(cfg):
	from r2env.db import Radare2
	from r2env.db import R0
	pkgs = []
	pkgs.append(Radare2(cfg))
	pkgs.append(R0(cfg))
	return pkgs

cfg = {
	"srcdir": "", # depends on the pkg
	"linkdir": "/usr",
	"envdir": 123,
	"prefix": "",
}

class R2Env:
	def __init__(self):
		self.db = load_packages(cfg)
	def init(self):
		if not os.path.isdir(".r2env"):
			os.mkdir(".r2env")
	def version(self):
		return "0.2.0"
	def available_packages(self):
		return self.db
	def installed_packages(self):
		return ipdb.list()
	def clean_package(self, pkgname):
		return ipdb.clean(pkgname)
