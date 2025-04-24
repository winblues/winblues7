%global commit 3c2990e202d67be2a383581eb491ef74e7ffaf5d
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20250423

Name:           aerothemeplasma
Version:        0
Release:        0.1.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Windows 7-inspired KDE Plasma desktop theme

License:        AGPLv3
URL:            https://gitgud.io/wackyideas/aerothemeplasma
Source0:        https://gitgud.io/wackyideas/%{name}/-/archive/%{commit}/%{name}-%{commit}.zip


# Build dependencies
BuildRequires:  cmake ninja-build make gcc-c++
BuildRequires:  extra-cmake-modules
# KDE Framework dependencies
BuildRequires:  kf6-ki18n-devel
BuildRequires:  kf6-kconfig-devel
BuildRequires:  kf6-kguiaddons-devel
BuildRequires:  kf6-kcoreaddons-devel
BuildRequires:  kf6-kpackage-devel
BuildRequires:  kf6-kio-devel
BuildRequires:  kf6-ksvg-devel
BuildRequires:  kf6-karchive-devel
BuildRequires:  kf6-kiconthemes-devel 
BuildRequires:  kf6-kcmutils-devel
BuildRequires:  kf6-kglobalaccel-devel
BuildRequires:  kf6-kcrash-devel
BuildRequires:  kf6-kdeclarative-devel
BuildRequires:  kf6-kdbusaddons-devel
BuildRequires:  kf6-solid-devel
BuildRequires:  kf6-knotifications-devel
BuildRequires:  kf6-kwidgetsaddons-devel
BuildRequires:  kf6-kirigami-devel
BuildRequires:  kf6-kirigami-addons-devel
# Plasma dependencies
BuildRequires:  plasma-workspace-devel
BuildRequires:  kwin-devel
BuildRequires:  kdecoration-devel
# Qt dependencies
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qt5compat-devel
BuildRequires:  qt6-qtmultimedia-devel
BuildRequires:  qt6-qtwayland-devel
BuildRequires:  qt6-qtdeclarative-devel
# Other dependencies
BuildRequires:  wayland-devel
BuildRequires:  plasma-wayland-protocols-devel

# Runtime dependencies
Requires:       kpackagetool6
Requires:       sddmthemeinstaller
Requires:       tar
Requires:       unzip
Requires:       kfontinst

%description
AeroThemePlasma is a KDE Plasma desktop customization that mimics the visual style of Windows 7, including cursors, sounds, color schemes, KWin effects, and SDDM theme.

%prep
%autosetup -n %{name}-%{commit}

%build
# Build KWin decorations if CMakeLists.txt exists
if [ -f kwin/decoration/CMakeLists.txt ]; then
  mkdir -p kwin/decoration/build
  pushd kwin/decoration/build
  %cmake -G Ninja ..
  %ninja_build
  popd
fi

# Build KWin C++ effects
for dir in kwin/effects_cpp/*; do
  if [ -d "$dir" ] && [ -f "$dir/CMakeLists.txt" ]; then
    mkdir -p "$dir/build"
    pushd "$dir/build"
    %cmake -G Ninja ..
    %ninja_build
    popd
  fi
done

for dir in plasma/plasmoids/src/*; do
  if [ -d "$dir" ] && [ -f "$dir/CMakeLists.txt" ]; then
    mkdir -p "$dir/build"
    pushd "$dir/build"
    %cmake -G Ninja ..
    %ninja_build
    popd
  fi
done

%install
mkdir -p %{buildroot}%{_datadir}/icons
mkdir -p %{buildroot}%{_datadir}/sounds
mkdir -p %{buildroot}%{_datadir}/plasma
mkdir -p %{buildroot}%{_datadir}/kwin
mkdir -p %{buildroot}%{_sysconfdir}/fonts/conf.d
mkdir -p %{buildroot}%{_datadir}/mime/packages
mkdir -p %{buildroot}%{_datadir}/color-schemes
mkdir -p %{buildroot}%{_datadir}/aerotheme

# Install KWin decorations
if [ -d kwin/decoration/build ]; then
  pushd kwin/decoration/build
  DESTDIR=%{buildroot} %ninja_install
  popd
fi

# Install KWin C++ effects
for dir in kwin/effects_cpp/*; do
  if [ -d "$dir" ] && [ -d "$dir/build" ]; then
    pushd "$dir/build"
    DESTDIR=%{buildroot} %ninja_install
    popd
  fi
done

# Install built plasmoids
for dir in plasma/plasmoids/src/*; do
  if [ -d "$dir" ] && [ -d "$dir/build" ]; then
    pushd "$dir/build"
    DESTDIR=%{buildroot} %ninja_install
    popd
  fi
done

# Install Kvantum config
if [ -d "misc/kvantum" ]; then
  mkdir -p %{buildroot}%{_datadir}/Kvantum
  cp -r misc/kvantum/Kvantum/* %{buildroot}%{_datadir}/Kvantum/
fi

# Install SDDM theme
if [ -d "plasma/sddm/sddm-theme-mod" ]; then
  mkdir -p %{buildroot}%{_datadir}/sddm/themes/aero
  cp -r plasma/sddm/sddm-theme-mod/* %{buildroot}%{_datadir}/sddm/themes/aero/
fi

# Install sound files
if [ -f "misc/sounds/sounds.tar.gz" ]; then
  tar -xf misc/sounds/sounds.tar.gz -C %{buildroot}%{_datadir}/sounds
fi

# Install icons and cursors
if [ -f "misc/icons/Windows 7 Aero.tar.gz" ]; then
  tar -xf "misc/icons/Windows 7 Aero.tar.gz" -C %{buildroot}%{_datadir}/icons
fi

if [ -f "misc/cursors/aero-drop.tar.gz" ]; then
  tar -xf misc/cursors/aero-drop.tar.gz -C %{buildroot}%{_datadir}/icons
fi

# Install color scheme
if [ -f "plasma/color_scheme/AeroColorScheme1.colors" ]; then
  install -Dm644 plasma/color_scheme/AeroColorScheme1.colors \
    %{buildroot}%{_datadir}/color-schemes/AeroColorScheme1.colors
fi

# Install plasma desktop theme
if [ -d "plasma/desktoptheme/Seven-Black" ]; then
  mkdir -p %{buildroot}%{_datadir}/plasma/desktoptheme/Seven-Black
  cp -r plasma/desktoptheme/Seven-Black/* %{buildroot}%{_datadir}/plasma/desktoptheme/Seven-Black/
fi

# Install look-and-feel
if [ -d "plasma/look-and-feel/authui7" ]; then
  mkdir -p %{buildroot}%{_datadir}/plasma/look-and-feel/authui7
  cp -r plasma/look-and-feel/authui7/* %{buildroot}%{_datadir}/plasma/look-and-feel/authui7/
fi

# Install QML plasmoids
for dir in plasma/plasmoids/io.gitgud.wackyideas.*; do
  if [ -d "$dir" ]; then
    APPLET_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/plasma/plasmoids/$APPLET_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/plasma/plasmoids/$APPLET_NAME/
  fi
done

# Install other KDE plasmoids
for dir in plasma/plasmoids/org.kde.*; do
  if [ -d "$dir" ]; then
    APPLET_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/plasma/plasmoids/$APPLET_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/plasma/plasmoids/$APPLET_NAME/
  fi
done

# Install panel layout templates
if [ -d "plasma/layout-templates" ]; then
  mkdir -p %{buildroot}%{_datadir}/plasma/layout-templates
  cp -r plasma/layout-templates/* %{buildroot}%{_datadir}/plasma/layout-templates/
fi

# Install KWin effects (QML effects)
for dir in kwin/effects/*; do
  if [ -d "$dir" ]; then
    EFFECT_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/kwin/effects/$EFFECT_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/kwin/effects/$EFFECT_NAME/
  fi
done

# Install KWin scripts
for dir in kwin/scripts/*; do
  if [ -d "$dir" ]; then
    SCRIPT_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/kwin/scripts/$SCRIPT_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/kwin/scripts/$SCRIPT_NAME/
  fi
done

# Install KWin tabbox themes
for dir in kwin/tabbox/*; do
  if [ -d "$dir" ]; then
    TABBOX_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/kwin/tabbox/$TABBOX_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/kwin/tabbox/$TABBOX_NAME/
  fi
done

# Install KWin outline
if [ -d "kwin/outline/plasma" ]; then
  mkdir -p %{buildroot}%{_datadir}/kwin/outline/plasma
  cp -r kwin/outline/plasma/* %{buildroot}%{_datadir}/kwin/outline/plasma/
fi

# Install mimetypes
if [ -d "misc/mimetype" ]; then
  cp -r misc/mimetype/* %{buildroot}%{_datadir}/mime/packages/
fi

# Install fontconfig override
if [ -f "misc/fontconfig/fonts.conf" ]; then
  install -Dm644 misc/fontconfig/fonts.conf \
    %{buildroot}%{_sysconfdir}/fonts/conf.d/99-aerotheme-segoe.conf
fi

# Branding files
mkdir -p %{buildroot}%{_datadir}/aerotheme/branding
if [ -d "misc/branding" ]; then
  cp -r misc/branding/* %{buildroot}%{_datadir}/aerotheme/branding/
fi

# Copy the helper scripts for reference
mkdir -p %{buildroot}%{_datadir}/aerotheme/scripts
install -m755 compile.sh %{buildroot}%{_datadir}/aerotheme/scripts/
install -m755 install_kwin_components.sh %{buildroot}%{_datadir}/aerotheme/scripts/
install -m755 install_misc_components.sh %{buildroot}%{_datadir}/aerotheme/scripts/
install -m755 install_plasma_components.sh %{buildroot}%{_datadir}/aerotheme/scripts/
install -m755 install_plasmoids.sh %{buildroot}%{_datadir}/aerotheme/scripts/

%files
%license LICENSE
%doc README.md INSTALL.md
%{_datadir}/plasma/desktoptheme/Seven-Black
%{_datadir}/plasma/look-and-feel/authui7
%{_datadir}/plasma/plasmoids/io.gitgud.wackyideas.*
%{_datadir}/plasma/plasmoids/org.kde.*
%{_datadir}/plasma/layout-templates
%{_datadir}/kwin/effects
%{_datadir}/kwin/scripts
%{_datadir}/kwin/tabbox
%{_datadir}/kwin/outline
%{_datadir}/sddm/themes/aero
%{_datadir}/Kvantum
%{_datadir}/sounds/*
%{_datadir}/icons/*
%{_datadir}/color-schemes/AeroColorScheme1.colors
%{_datadir}/mime/packages/*
%{_datadir}/aerotheme
%config(noreplace) %{_sysconfdir}/fonts/conf.d/99-aerotheme-segoe.conf

%changelog
* Thu Apr 24 2025 Adam Fidel <adam@blues.win> - 0-0.1.20250423git3c2990e
- Initial RPM packaging of AeroThemePlasma