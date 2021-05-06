import argparse
import r2env

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("action", help="run action", action="store")
	parser.add_argument("-v", "--version", help="show version string", action="store_true")
	args = parser.parse_args()
	
	e = r2env.R2Env()

	if parser.version:
		print(e.version())
		return
	if action == "list":
		print(e.packages())
	elif action == "version":
		print(e.version())
	elif action == "search":
		for pkg in e.packages():
			print(pkg.name())
	else:
		return
	#print("r2env")
	#print(e.version())
