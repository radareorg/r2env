import r2env
import r2env.tools

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

class Radare2(r2env.Package):
	header = {
		"name": "radare2",
		"profiles": r2profiles
	}
	def build(self, options):
		build_radare2()
	def install(self):
		install_radare2()

def build_radare():
	print("BUILD")

def install_radare():
	print("INSTALL")

