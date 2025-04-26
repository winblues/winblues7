#!/bin/bash

set -exuo pipefail

patch_file=$(realpath 10-aero-theme.diff)

cd /tmp/
wget https://gitgud.io/wackyideas/aerothemeplasma/-/archive/master/aerothemeplasma-master.tar.gz
tar xf aerothemeplasma-master.tar.gz
cd aerothemeplasma-master

patch -p1 <"${patch_file}"

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

# Kvantum
#echo "Installing Kvantum theme..."
#KV_DIR="$HOME/.config"
#cp -r "$PWD/misc/kvantum/Kvantum" "$KV_DIR"
#echo "Done."

#Sounds
echo "Unpacking sound themes..."
SOUNDS_DIR="/usr/share/sounds"
tar -xf "$PWD/misc/sounds/sounds.tar.gz" --directory "$SOUNDS_DIR"
echo "Done."

#Icons
echo "Unpacking icon theme..."
ICONS_DIR="$/usr/share/icons"
tar -xf "$PWD/misc/icons/Windows 7 Aero.tar.gz" --directory "$ICONS_DIR"
echo "Done."

#Cursors
echo "Unpacking cursor theme..."
CURSOR_DIR="/usr/share/icons"
tar -xf "$PWD/misc/cursors/aero-drop.tar.gz" --directory "$CURSOR_DIR"
echo "Done."

#Mimetype
echo "Installing mimetypes..."
MIMETYPE_DIR="$/usr/share/mime/packages"
for filename in "$PWD/misc/mimetype/"*; do
  cp -r "$filename" "$MIMETYPE_DIR"
done
update-mime-database
echo "Done."

#Optional
echo "Do you want to install a custom font configuration for Segoe UI fonts? (y/N)"
read answer
FONTCONF_DIR="$HOME/.config"

if [ "$answer" != "${answer#[Yy]}" ]; then
  if test -f "$FONTCONF_DIR/fontconfig/fonts.conf"; then
    echo "Backing up fonts.conf to fonts.conf.old"
    cp -r "$FONTCONF_DIR/fontconfig/fonts.conf" "$FONTCONF_DIR/fontconfig/fonts.conf.old"
  fi
  echo "Installing custom font configuration..."
  cp -r "$PWD/misc/fontconfig/" "$FONTCONF_DIR"

  HAS_VAR=$(grep "QML_DISABLE_DISTANCEFIELD" /etc/environment)
  echo "Adding QML_DISABLE_DISTANCEFIELD=1 to /etc/environment"
  if [[ -n "$HAS_VAR" ]]; then
    echo "Variable already added, skipping..."
  else
    pkexec echo "QML_DISABLE_DISTANCEFIELD=1" >>/etc/environment
  fi
fi
echo "Done."
echo "Do you want to install custom branding for Info Center? (y/N)"
read answer
BRANDING_DIR="$HOME/.config/kdedefaults"

if [ "$answer" != "${answer#[Yy]}" ]; then
  for filename in "$PWD/misc/branding/"*; do
    cp -r "$filename" "$BRANDING_DIR"
  done
  kwriteconfig6 --file "$BRANDING_DIR/kcm-about-distrorc" --group General --key LogoPath "$BRANDING_DIR/kcminfo.png"
fi
echo "Done."

TMP_DIR="/tmp/atp"
mkdir -p "$TMP_DIR"

echo "Do you want to install the command prompt font (Terminal Vector)? (y/N)"
read answer
if [ "$answer" != "${answer#[Yy]}" ]; then
  curl -L https://www.yohng.com/files/TerminalVector.zip >"$TMP_DIR/TerminalVector.zip"
  unzip "$TMP_DIR/TerminalVector.zip" -d "$TMP_DIR"
  kfontinst "$TMP_DIR/TerminalVector.ttf"
fi
echo "Done."
