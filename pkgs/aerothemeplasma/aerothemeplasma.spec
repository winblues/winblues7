%global debug_package %{nil}

%global commit d572194634735a6a727dc71cc4cf1aaf3ca8ce7a
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20260204

Name:           aerothemeplasma
Version:        0
Release:        0.9.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Windows 7-inspired KDE Plasma desktop theme

License:        AGPLv3
URL:            https://gitgud.io/wackyideas/aerothemeplasma
Source0:        https://gitgud.io/wackyideas/%{name}/-/archive/%{commit}/%{name}-%{commit}.zip

# Build requirements for C++ components
BuildRequires:  ninja-build

BuildRequires:  cmake make gcc-c++
BuildRequires:  extra-cmake-modules
BuildRequires:  pkgconfig
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
BuildRequires:  gmp-ecm-devel 
BuildRequires:  kf6-knewstuff-devel 
BuildRequires:  kf6-knotifyconfig-devel 
BuildRequires:  kf6-attica-devel 
BuildRequires:  kf6-krunner-devel 
BuildRequires:  kf6-sonnet-devel 
BuildRequires:  kf6-kitemmodels-devel 
BuildRequires:  kf6-kstatusnotifieritem-devel
BuildRequires:  kf6-qqc2-desktop-style
# Plasma dependencies
BuildRequires:  plasma-workspace-devel
BuildRequires:  kwin-devel
BuildRequires:  kwin-x11-devel
BuildRequires:  kdecoration-devel
BuildRequires:  libplasma-devel 
BuildRequires:  plasma-activities-devel 
BuildRequires:  plasma-wayland-protocols 
BuildRequires:  kf5-plasma-devel
BuildRequires:  plasma5support-devel 
BuildRequires:  plasma-activities-stats-devel 
# Qt dependencies
BuildRequires:  qt-devel 
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qt5compat-devel
BuildRequires:  qt6-qtmultimedia-devel
BuildRequires:  qt6-qtwayland-devel
BuildRequires:  qt6-qtdeclarative-devel 
BuildRequires:  qt6-qt5compat-devel 
BuildRequires:  qt6-qtwayland-devel
# Other dependencies
BuildRequires:  wayland-devel
BuildRequires:  plasma-wayland-protocols-devel
BuildRequires:  libepoxy-devel
BuildRequires:  libdrm-devel
BuildRequires:  polkit-qt6-1-devel 
BuildRequires:  curl

# Specific extras for the theme
Requires:       kvantum
Requires:       tar
Requires:       unzip
Requires:       kf6-frameworkintegration

%description
AeroThemePlasma is a KDE Plasma desktop customization that mimics the visual style of 
Windows 7, including cursors, sounds, color schemes, KWin effects, and SDDM theme.
This is the default theme for Winblues 7.

%prep
%autosetup -n %{name}-%{commit}

%build
# Build the C++ KWin decoration
mkdir -p build-decoration
pushd build-decoration
%cmake ../kwin/decoration \
    -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release -B .
make %{?_smp_mflags}
popd

# Build C++ KWin effects
for effect in kwin/effects_cpp/*; do
    if [ -d "$effect" ] && [ -f "$effect/CMakeLists.txt" ]; then
        EFFECT_NAME=$(basename "$effect")
        if [ "$EFFECT_NAME" == "kwin-effect-smodsnap-v2" ] || [ "$EFFECT_NAME" == "smodglow" ]; then
            continue
        fi

        mkdir -p build-$EFFECT_NAME
        pushd build-$EFFECT_NAME
        %cmake ../$effect \
            -G "Unix Makefiles" \
            -DKWIN_BUILD_WAYLAND=ON \
            -DCMAKE_BUILD_TYPE=Release -B .
        make %{?_smp_mflags}
        popd
    fi
done

# Build plasmoids
for plasmoid in plasma/plasmoids/src/*; do
    if [ -d "$plasmoid" ] && [ -f "$plasmoid/CMakeLists.txt" ]; then
        PLASMOID_NAME=$(basename "$plasmoid")
        mkdir -p build-$PLASMOID_NAME
        pushd build-$PLASMOID_NAME
        %cmake ../$plasmoid \
            -G "Unix Makefiles" \
            -DCMAKE_BUILD_TYPE=Release -B .
        make %{?_smp_mflags}
        popd
    fi
done

#Build kcmloader
mkdir -p build-kcmloader
pushd build-kcmloader
%cmake ../plasma/aerothemeplasma-kcmloader \
    -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release -B .
make %{?_smp_mflags}
popd

#Build libplasma
VERSION=$(rpm -q plasma-workspace-devel --queryformat '%%{VERSION}')
URL="https://invent.kde.org/plasma/libplasma/-/archive/v${VERSION}/libplasma-v${VERSION}.tar.gz"
ARCHIVE="libplasma-v${VERSION}.tar.gz"
SRCDIR="libplasma-v${VERSION}"
mkdir build-libplasma
curl $URL -o ./build-libplasma/$ARCHIVE
tar -xvf ./build-libplasma/$ARCHIVE -C ./build-libplasma/
cp -r misc/libplasma/src ./build-libplasma/$SRCDIR/
mkdir -p ./build-libplasma/$SRCDIR/build
pushd ./build-libplasma/$SRCDIR/build
%cmake .. \
      -G "Unix Makefiles"  \
      -DCMAKE_BUILD_TYPE=Release -B .
make %{?_smp_mflags}
mkdir ../../build
cp -r * ../../build
popd

%install
# Clear buildroot
rm -rf %{buildroot}

# Install C++ KWin decoration
pushd build-decoration
%make_install
popd

# Install C++ KWin effects
for effect in kwin/effects_cpp/*; do
    if [ -d "$effect" ] && [ -f "$effect/CMakeLists.txt" ]; then
        EFFECT_NAME=$(basename "$effect")
        if [ -d build-$EFFECT_NAME ]; then
            pushd build-$EFFECT_NAME
            %make_install
          popd
        fi
    fi
done

#install compiled plasmoids
for plasmoid in plasma/plasmoids/src/*; do
    if [ -d "$plasmoid" ] && [ -f "$plasmoid/CMakeLists.txt" ]; then
        PLASMOID_NAME=$(basename "$plasmoid")
        if [ -d build-$PLASMOID_NAME ]; then
            pushd build-$PLASMOID_NAME
            %make_install
          popd
        fi
    fi
done

#Install kcmloader
pushd build-kcmloader
%make_install
popd

#Install libplasma patches
pushd ./build-libplasma/build
%make_install
# since make installs all parts of libplasma, remove any unneeded files that this is not patching
rm -r %{buildroot}%{_includedir}/Plasma
rm -r %{buildroot}%{_includedir}/PlasmaQuick
rm -r %{buildroot}%{_libdir}/cmake
rm -r %{buildroot}%{_libdir}/qt6/plugins/kf6
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/kirigami
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/plasma/components
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/plasma/configuration
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/plasma/core/DefaultToolTip.qml
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/plasma/core/DialogBackground.qml
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/plasma/core/corebindingsplugin.qmltypes
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/plasma/core/kde-qmlmodule.version
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/plasma/core/qmldir
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/plasma/extras
rm -r %{buildroot}%{_libdir}/qt6/qml/org/kde/plasma/plasmoid
rm -r %{buildroot}%{_datadir}/kdevappwizard
rm -r %{buildroot}%{_datadir}/locale/*/LC_MESSAGES/libplasma6.mo
rm -r %{buildroot}%{_datadir}/plasma/desktoptheme/breeze-dark
rm -r %{buildroot}%{_datadir}/plasma/desktoptheme/breeze-light
rm -r %{buildroot}%{_datadir}/plasma/desktoptheme/default
rm -r %{buildroot}%{_datadir}/qlogging-categories6
popd

# Install SMOD window decoration resource file
mkdir -p %{buildroot}%{_datadir}/smod/decorations
cp -r kwin/smod/decorations/Aero.smod.rcc %{buildroot}%{_datadir}/smod/decorations/

# Install remaining SMOD files
mkdir -p %{buildroot}%{_datadir}/smod/kwin
cp -r kwin/smod/kwin/*.png %{buildroot}%{_datadir}/smod/kwin/
cp -r kwin/smod/snapeffecttextures.smod.rcc %{buildroot}%{_datadir}/smod/

# Create directories
mkdir -p %{buildroot}%{_datadir}/icons
mkdir -p %{buildroot}%{_datadir}/sounds
mkdir -p %{buildroot}%{_datadir}/plasma/desktoptheme
mkdir -p %{buildroot}%{_datadir}/plasma/look-and-feel
mkdir -p %{buildroot}%{_datadir}/sddm/themes
mkdir -p %{buildroot}%{_datadir}/color-schemes
mkdir -p %{buildroot}%{_datadir}/Kvantum
mkdir -p %{buildroot}%{_sysconfdir}/fonts/conf.d
mkdir -p %{buildroot}%{_datadir}/kwin/effects
mkdir -p %{buildroot}%{_datadir}/kwin/scripts
mkdir -p %{buildroot}%{_datadir}/kwin/tabbox
mkdir -p %{buildroot}%{_datadir}/kwin/outline
mkdir -p %{buildroot}%{_datadir}/plasma/plasmoids
mkdir -p %{buildroot}%{_sysconfdir}/xdg
mkdir -p %{buildroot}%{_datadir}/aerotheme/branding

# Install Kvantum theme
if [ -d "misc/kvantum" ]; then
  cp -r misc/kvantum/Kvantum/* %{buildroot}%{_datadir}/Kvantum/
fi

# Install SDDM theme
if [ -d "plasma/sddm/sddm-theme-mod" ]; then
  mkdir -p %{buildroot}%{_datadir}/sddm/themes/sddm-theme-mod
  cp -r plasma/sddm/sddm-theme-mod/* %{buildroot}%{_datadir}/sddm/themes/sddm-theme-mod/
fi

# Install sound files
if [ -f "misc/sounds/sounds.tar.gz" ]; then
  tar -xf misc/sounds/sounds.tar.gz -C %{buildroot}%{_datadir}/sounds
fi

# Install icons and cursors
tar -xf "misc/icons/Windows 7 Aero.tar.gz" -C %{buildroot}%{_datadir}/icons
tar -xf misc/cursors/aero-drop.tar.gz -C %{buildroot}%{_datadir}/icons

# Install color scheme
install -Dm644 plasma/color_scheme/Aero.colors \
  %{buildroot}%{_datadir}/color-schemes/Aero.colors

# Install plasma desktop theme
mkdir -p %{buildroot}%{_datadir}/plasma/desktoptheme/Seven-Black
cp -r plasma/desktoptheme/Seven-Black/* %{buildroot}%{_datadir}/plasma/desktoptheme/Seven-Black/

# Install shell overrides (including custom lock screen)
mkdir -p %{buildroot}%{_datadir}/plasma/shells/io.gitgud.wackyideas.desktop
cp -r plasma/shells/io.gitgud.wackyideas.desktop/* %{buildroot}%{_datadir}/plasma/shells/io.gitgud.wackyideas.desktop/

# Install look-and-feel
mkdir -p %{buildroot}%{_datadir}/plasma/look-and-feel/authui7
cp -r plasma/look-and-feel/authui7/* %{buildroot}%{_datadir}/plasma/look-and-feel/authui7/

# Install custom plasmoids
for dir in plasma/plasmoids/io.gitgud.wackyideas.*; do
  if [ -d "$dir" ]; then
    APPLET_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/plasma/plasmoids/$APPLET_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/plasma/plasmoids/$APPLET_NAME/
  fi
done

# Install panel layout templates
mkdir -p %{buildroot}%{_datadir}/plasma/layout-templates
cp -r plasma/layout-templates/* %{buildroot}%{_datadir}/plasma/layout-templates/

# Install fontconfig override
install -Dm644 misc/fontconfig/fonts.conf \
  %{buildroot}%{_sysconfdir}/fonts/conf.d/99-aerotheme-segoe.conf

# Install KWin effects directly (JavaScript-based ones)
for dir in kwin/effects/*; do
  if [ -d "$dir" ]; then
    EFFECT_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/kwin/effects/$EFFECT_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/kwin/effects/$EFFECT_NAME/
  fi
done

# Install KWin scripts directly
for dir in kwin/scripts/*; do
  if [ -d "$dir" ]; then
    SCRIPT_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/kwin/scripts/$SCRIPT_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/kwin/scripts/$SCRIPT_NAME/
  fi
done

# Install KWin tabbox themes directly
for dir in kwin/tabbox/*; do
  if [ -d "$dir" ]; then
    TABBOX_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/kwin/tabbox/$TABBOX_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/kwin/tabbox/$TABBOX_NAME/
  fi
done

# Install KWin outline directly
if [ -d "kwin/outline/plasma" ]; then
  mkdir -p %{buildroot}%{_datadir}/kwin/outline/plasma
  cp -r kwin/outline/plasma/* %{buildroot}%{_datadir}/kwin/outline/plasma/
fi

# Install system Plasmoids directly
for dir in plasma/plasmoids/org.kde.*; do
  if [ -d "$dir" ]; then
    APPLET_NAME=$(basename "$dir")
    mkdir -p %{buildroot}%{_datadir}/plasma/plasmoids/$APPLET_NAME
    cp -r "$dir"/* %{buildroot}%{_datadir}/plasma/plasmoids/$APPLET_NAME/
  fi
done

# Install mimetypes
if [ -d "misc/mimetype" ]; then
  mkdir -p %{buildroot}%{_datadir}/mime/packages
  cp -r misc/mimetype/* %{buildroot}%{_datadir}/mime/packages/
fi

# Branding files
if [ -d "misc/branding" ]; then
  cp -r misc/branding/* %{buildroot}%{_datadir}/aerotheme/branding/
fi

# Debug - list all installed files
echo "Listing all installed files in the buildroot:"
find %{buildroot} -type f | sort

%post
# Update mime database
update-mime-database %{_datadir}/mime &> /dev/null || :

# Update icon cache
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

# Update system cache
kbuildsycoca6 &> /dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
    update-mime-database %{_datadir}/mime &> /dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :
kbuildsycoca6 &> /dev/null || :

%files
%license LICENSE
%doc README.md INSTALL.md
%{_datadir}/plasma/desktoptheme/Seven-Black
%{_datadir}/plasma/shells/io.gitgud.wackyideas.desktop
%{_datadir}/plasma/look-and-feel/authui7
%{_datadir}/plasma/plasmoids/io.gitgud.wackyideas.*
# %{_datadir}/plasma/plasmoids/org.kde.*
%{_datadir}/plasma/layout-templates
%dir %{_datadir}/kwin/effects
%dir %{_datadir}/kwin/effects/*
%{_datadir}/kwin/effects/*/*
%{_datadir}/kwin/scripts
%{_datadir}/kwin/tabbox
%{_datadir}/kwin/outline
%{_datadir}/sddm/themes/sddm-theme-mod
%{_datadir}/Kvantum
%{_datadir}/sounds/*
%{_datadir}/icons/*
%{_datadir}/color-schemes/Aero.colors
%{_datadir}/aerotheme
%{_datadir}/mime/packages/*
%{_datadir}/smod/*
%{_bindir}/aerothemeplasma-kcmloader
%{_libdir}/qt6/qml/org/kde/plasma/core/libcorebindingsplugin.so
%{_libdir}/libPlasma*

# KDE decoration plugins
%{_libdir}/qt6/plugins/org.kde.kdecoration3/org.smod.smod.so
%{_libdir}/qt6/plugins/org.kde.kdecoration3.kcm/kcm_smoddecoration.so
%{_libdir}/qt6/plugins/kwin/effects/configs/*.so
%{_libdir}/qt6/plugins/kwin/effects/plugins/*.so

# Compiled plasmoids
%{_libdir}/qt6/plugins/plasma/applets/io.gitgud.wackyideas.*.so
%{_libdir}/qt6/qml/io/gitgud/wackyideas/*

# Include locale files
%{_datadir}/locale/*/LC_MESSAGES/breeze_kwin_deco.mo
%{_datadir}/locale/*/LC_MESSAGES/breeze_style_config.mo

# Include development files
%{_includedir}/SMOD/Decoration/*
%{_libdir}/pkgconfig/smoddecoration.pc

# Application desktop files
%{_datadir}/applications/kcm_smoddecoration.desktop

# Config files
%config(noreplace) %{_sysconfdir}/fonts/conf.d/99-aerotheme-segoe.conf

%changelog
* Thu May 08 2025 Adam Fidel <adam@fidel.cloud> - 0-0.1.20250508git3c2990e
- Initial RPM packaging of AeroThemePlasma
