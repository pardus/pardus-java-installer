project('pardus-java-installer')

subdir('po')
subdir('debian')

# install sources
install_subdir('src', install_dir: '/usr/share/pardus/pardus-java-installer')
install_subdir('ui', install_dir: '/usr/share/pardus/pardus-java-installer')

# icons
install_data(
    'pardus-java-installer.svg',
    install_dir: '/usr/share/icons/hicolor/scalable/apps',
)

# desktop files
install_data(
    'tr.org.pardus.java-installer.desktop',
    install_dir: '/usr/share/applications/',
)

# command
install_data('pardus-java-installer', install_dir: '/usr/bin')
