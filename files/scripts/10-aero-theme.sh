#!/bin/bash

set -exuo pipefail

patch_file=$(realpath 10-aero-theme.diff)

cd /tmp/
wget https://gitgud.io/wackyideas/aerothemeplasma/-/archive/master/aerothemeplasma-master.tar.gz
tar xf aerothemeplasma-master.tar.gz
cd aerothemeplasma-master

patch -p1 < "${patch_file}"

mv plasma/smod /usr/share

for d in desktoptheme look-and-feel plasmoids layout-templates shells; do
  rsync -aP plasma/${d} /usr/share/plasma/${d}
done

mv plasma/sddm/sddm-theme-mod /usr/share/sddm/themes

# TODO move this build to its own repo
dev_pkgs="plasma-workspace-devel kvantum qt6-qtmultimedia-devel qt6-qt5compat-devel libplasma-devel qt6-qtbase-devel qt6-qtwayland-devel plasma-activities-devel kf6-kpackage-devel kf6-kglobalaccel-devel qt6-qtsvg-devel wayland-devel plasma-wayland-protocols kf6-ksvg-devel kf6-kcrash-devel kf6-kguiaddons-devel kf6-kcmutils-devel kf6-kio-devel kdecoration-devel kf6-ki18n-devel kf6-knotifications-devel kf6-kirigami-devel kf6-kiconthemes-devel cmake gmp-ecm-devel kf5-plasma-devel libepoxy-devel kwin-devel kf6-karchive kf6-karchive-devel plasma-wayland-protocols-devel qt6-qtbase-private-devel qt6-qtbase-devel"

dnf5 install -y $dev_pkgs

bash compile.sh
bash install_plasmoids.sh
bash install_plasma_components.sh

