# Pardus Java Installer

Pardus Java Installer is an application for java installation and default java version selection.

It is currently a work in progress. Maintenance is done by <a href="https://www.pardus.org.tr/">Pardus</a> team.

[![Packaging status](https://repology.org/badge/vertical-allrepos/pardus-java-installer.svg)](https://repology.org/project/pardus-java-installer/versions)

### **Dependencies**

This application is developed based on Python3 and GTK+ 3. Dependencies:
```bash
gir1.2-glib-2.0 gir1.2-gtk-3.0 python3-gi
```

### **Run Application from Source**

Install dependencies
```bash
sudo apt install gir1.2-glib-2.0 gir1.2-gtk-3.0 python3-gi
```
Clone the repository
```bash
git clone https://github.com/pardus/pardus-java-installer.git ~/pardus-java-installer
```
Run application
```bash
python3 ~/pardus-java-installer/src/Main.py
```

### **Build deb package**

```bash
sudo apt install devscripts git-buildpackage
sudo mk-build-deps -ir
gbp buildpackage --git-export-dir=/tmp/build/pardus-java-installer -us -uc
```

### **Screenshots**

![Pardus Java Installer 1](screenshots/pardus-java-installer-1.png)
