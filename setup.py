#!/usr/bin/env python3
from setuptools import setup, find_packages,os

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
    ("/usr/share/locale/tr/LC_MESSAGES/", ["translations/tr/LC_MESSAGES/pardus-java-installer.mo"]),
    ("/usr/share/pardus/pardus-java-installer/", ["icon.svg"]),
    ("/usr/share/pardus/pardus-java-installer/src", ["src/main.py", "src/MainWindow.py", "src/PackageManager.py", "src/Actions.py", "src/__version__"]),
    ("/usr/share/pardus/pardus-java-installer/ui", ["ui/MainWindow.glade"]),
    ("/usr/share/polkit-1/actions", ["tr.org.pardus.pkexec.pardus-java-installer.policy"]),
    ("/usr/bin/", ["pardus-java-installer"]),
]

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
