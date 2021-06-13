# -*- coding: utf-8 -*-

import r2env.tools
import os
import sys
from r2env.tools import env_path


def build_radare2(profile):
    pkgver = "radare2" + "@" + profile["version"]
    envp = env_path()
    srcdir = os.path.join(envp, "src")
    gitdir = os.path.join(envp, "src", pkgver)
    dstdir = os.path.join(envp, "dst", pkgver)
    logdir = os.path.join(envp, "log")
    logfil = os.path.join(logdir, "radare2.txt")
    prefix = os.path.join(envp, "prefix")

    rc = 0
    try:
        os.mkdir(srcdir)
    except:
        pass
    try:
        os.mkdir(dstdir)
    except:
        pass
    try:
        os.mkdir(logdir)
    except:
        pass

    if os.path.isdir(gitdir):
        rc = os.system("cd '" + gitdir + "' && git reset --hard && git checkout master ; git reset --hard ; git pull")
    else:
        giturl = profile["source"]
        rc = os.system("git clone " + giturl + " '" + gitdir + "'")
    if rc != 0:
        print("Clone failed")
        return False
    if "tag" in profile:
        os.system("cd " + gitdir + " && git checkout " + str(profile["tag"]))
    print("Building ...")
    print("tail -f " + logfil)
    use_meson = profile["meson"]
    if use_meson:
        rc = os.system(
            "(cd " + gitdir + " && git clean -xdf && rm -rf build && meson --buildtype=release local=true --prefix=" + prefix + " 2>&1 && ninja -C build && ninja -C build install) > " + logfil)
    else:
        # rc = os.system("(cd " + gitdir + " && git clean -xdf && rm -rf shlr/capstone; ./configure --with-rpath --prefix="+dstdir+" 2>&1 && make -j4 2>&1 && make install DESTDIR="+dstdir+") > " + logfil)
        rc = os.system(
            "(cd " + gitdir + " && git clean -xdf && rm -rf shlr/capstone; ./configure --with-rpath --prefix=" + dstdir + " 2>&1 && make -j4 2>&1 && make install) > " + logfil)
    if rc == 0:
        # clone radare2 in srcdir
        os.system("date > " + dstdir + "/.timestamp.txt")
        os.system("git log |head -n1> " + dstdir + "/.commit.txt")
    else:
        print("Build failed")
        sys.exit(1)


class Radare2(r2env.Package):
    header = {
        "name": "radare2",
        "profiles": r2profiles
    }

    def build(self, profile):
        print("Building radare2")
        build_radare2(profile)
        print("magic done")
