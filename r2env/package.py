from r2env.tools import git_clone

def do_link(self):
	print("Linking")
	print(self.name())

def do_unlink(self):
	print("Unlinking")

def fetch_package(self):
	print("Fetch")
	git_clone("https://github.com/radareorg/r0")

class Package:
	def __init__(self, cfg):
		self.cfg = cfg
	def name(self):
		return ""
	def platform(self):
		return ""
	def fetch(self):
		# do nothing
		return ""
	def install(self):
		# do nothing
		return ""
	def tostring(self):
		pkgname = self.header["name"]
		res = []
		for p in self.header["profiles"]:
			row = pkgname + "@" + p["version"] + " #" + p["platform"]
			res.append(row)
		return "\n".join(res)
