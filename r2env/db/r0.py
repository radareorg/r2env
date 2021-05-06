import r2env
import r2env.tools

def build_radare():
	print("BUILD")

def install_radare():
	print("INSTALL")

r0profiles = {
	"git": {
		"platform": "any",
		"source": "https://github.com/radareorg/r0",
		"needs": ["git", "make" ]
	}
}

class Radare0(r2env.Package):
	header = {
		"name": "radare0",
		"description": "r0, aka ired, aka minimalistic hex editor",
		"profiles": r0profiles
	}
	def build(self, options):
		build_radare2()
	def install(self):
		install_radare2()
