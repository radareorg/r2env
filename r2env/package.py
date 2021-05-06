def do_link(self):
	print("Linking")
	print(self.name())

def do_unlink(self):
	print("Unlinking")

class Package:
	def __init__(self, cfg):
		self.cfg = cfg
	def name(self):
		return ""
	def platform(self):
		return ""
	def link(self):
		do_link(self)
	def unlink(self):
		do_unlink(self)
	def install(self):
		print("Installing package")
