import argparse
import r2env

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("action", help="run action", action="store")
	parser.add_argument("-v", "--version", help="show version string", action="store_true")
	args = parser.parse_args()
	
	e = r2env.R2Env()

	if args.version:
		print(e.version())
		return
	if args.action == "list":
		print(e.packages())
	elif args.action == "version":
		print(e.version())
	elif args.action == "search":
		for pkg in e.packages():
			print(pkg.name())
	else:
		return
	#print("r2env")
	#print(e.version())
