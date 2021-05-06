import r2env

def build_radare():
	print("BUILD")

def install_radare():
	print("INSTALL")

class Radare2(r2env.Package):
	def name(self):
		return "radare2"
	def version(self):
		return "git"
	def platform(self):
		return "unix"
	def build(self):
		build_radare2()
	def install(self):
		install_radare2()
