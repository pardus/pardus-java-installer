#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os, subprocess


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs("{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True)
            mo_file = "{}/{}/LC_MESSAGES/{}".format(podir, po.split(".po")[0], "pardus-java-installer.mo")
            msgfmt_cmd = 'msgfmt {} -o {}'.format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(("/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                       ["po/" + po.split(".po")[0] + "/LC_MESSAGES/pardus-java-installer.mo"]))
    return mo


changelog = 'debian/changelog'
version = ""
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
    f = open('src/__version__', 'w')
    f.write(version)
    f.close()

data_files = [
    ("/usr/share/applications/", ["tr.org.pardus.java-installer.desktop"]),
    ("/usr/share/pardus/pardus-java-installer/src",
     ["src/main.py", "src/MainWindow.py", "src/PackageManager.py", "src/Actions.py", "src/__version__"]),
    ("/usr/share/pardus/pardus-java-installer/ui", ["ui/MainWindow.glade"]),
    ("/usr/share/polkit-1/actions", ["tr.org.pardus.pkexec.pardus-java-installer.policy"]),
    ("/usr/bin/", ["pardus-java-installer"]),
    ("/usr/share/icons/hicolor/scalable/apps/", ["pardus-java-installer.svg"])
] + create_mo_files()

setup(
    name="Pardus Java Installer",
    version=version,
    packages=find_packages(),
    scripts=["pardus-java-installer"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Emin Fedar",
    author_email="emin.fedar@pardus.org.tr",
    description="Pardus Java Installer application.",
    license="GPLv3",
    keywords="java install installer",
    url="https://www.pardus.org.tr",
)
