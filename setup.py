#!/usr/bin/env python3
from setuptools import setup, find_packages

data_files = [
    ("/usr/share/applications/", ["tr.org.pardus.java-installer.desktop"]),
    ("/usr/share/locale/tr/LC_MESSAGES/", ["translations/tr/LC_MESSAGES/pardus-java-installer.mo"]),
    ("/usr/share/pardus/pardus-java-installer/", ["icon.svg"]),
    ("/usr/share/pardus/pardus-java-installer/src", ["src/main.py", "src/MainWindow.py", "src/PackageManager.py", "src/Actions.py"]),
    ("/usr/share/pardus/pardus-java-installer/ui", ["ui/MainWindow.glade"]),
    ("/usr/share/polkit-1/actions", ["tr.org.pardus.pkexec.pardus-java-installer.policy"]),
    ("/usr/bin/", ["pardus-java-installer"]),
]

setup(
    name="Pardus Java Installer",
    version="0.1",
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
