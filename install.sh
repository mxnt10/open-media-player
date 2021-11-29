#!/bin/bash

pkgver='1.3'
install_root=${install_root:-""}

set -e
[ "$install_root" != "" ] && {
  mkdir -p "$install_root"/usr/{bin,share/{applications,pixmaps,omp/icons},doc/omp-"$pkgver"}
} || {
  mkdir -p /usr/{share/omp/icons,doc/omp-"$pkgver"}
}

install -Dm 0644 appdata/omp.png "$install_root"/usr/share/pixmaps
install -Dm 0644 appdata/logo.png "$install_root"/usr/share/pixmaps
install -Dm 0644 appdata/omp.desktop "$install_root"/usr/share/applications

cp -a ChangeLog LICENSE README.md "$install_root"/usr/doc/omp-"$pkgver"
cp -Tr src "$install_root"/usr/share/omp
cp -Tr icons "$install_root"/usr/share/omp/icons

echo '#!/bin/bash
cd /usr/share/omp
python3 OpenMediaPlayer.py "$@"' > "$install_root"/usr/bin/omp

chmod 755 "$install_root"/usr/bin/omp
exit 0
