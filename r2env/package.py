# -*- coding: utf-8 -*-

from r2env.tools import git_clone

class Package:
    def __init__(self, dst_path):
        self._dst_path = dst_path

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
