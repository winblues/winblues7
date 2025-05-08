%global debug_package %{nil}

%global commit 3c2990e202d67be2a383581eb491ef74e7ffaf5d
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20250508

Name:           aerothemeplasma
Version:        0
Release:        0.1.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Windows 7-inspired KDE Plasma desktop theme

License:        AGPLv3
URL:            https://gitgud.io/wackyideas/aerothemeplasma
Source0:        https://gitgud.io/wackyideas/%{name}/-/archive/%{commit}/%{name}-%{commit}.zip

# Build requirements for C++ components
BuildRequires:  cmake >= 3.16
BuildRequires:  extra-cmake-modules
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qt5compat-devel
BuildRequires:  kf6-ki18n-devel
BuildRequires:  kf6-kconfigwidgets-devel
BuildRequires:  kf6-kcoreaddons-devel
BuildRequires:  kf6-kguiaddons-devel
BuildRequires:  kf6-kiconthemes-devel
BuildRequires:  kf6-kservice-devel
BuildRequires:  kf6-kconfig-devel
BuildRequires:  kf6-kcmutils-devel
BuildRequires:  kf6-kpackage-devel
BuildRequires:  kf6-kwindowsystem-devel
BuildRequires:  kdecoration-devel
BuildRequires:  kwin-devel
BuildRequires:  plasma-framework-devel
BuildRequires:  kf6-kdeclarative-devel

# KDE6 Dependencies
Requires:       plasma-workspace
Requires:       plasma-desktop
Requires:       kwin
Requires:       sddm-kcm
# Specific extras for the theme
Requires:       kvantum
Requires:       tar
Requires:       unzip

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
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release
%ninja_build
popd

# Build C++ KWin effects
for effect in kwin/effects_cpp/*; do
    if [ -d "$effect" ] && [ -f "$effect/CMakeLists.txt" ]; then
        EFFECT_NAME=$(basename "$effect")
        mkdir -p build-$EFFECT_NAME
        pushd build-$EFFECT_NAME
        %cmake ../$effect \
            -G Ninja \
            -DCMAKE_BUILD_TYPE=Release
        %ninja_build
        popd
    fi
done

%install
# Clear buildroot
rm -rf %{buildroot}

# Install C++ KWin decoration
pushd build-decoration
%ninja_install
popd

# Install C++ KWin effects
for effect in kwin/effects_cpp/*; do
    if [ -d "$effect" ] && [ -f "$effect/CMakeLists.txt" ]; then
        EFFECT_NAME=$(basename "$effect")
        pushd build-$EFFECT_NAME
        %ninja_install
        popd
    fi
done

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
  mkdir -p %{buildroot}%{_datadir}/sddm/themes/aero
  cp -r plasma/sddm/sddm-theme-mod/* %{buildroot}%{_datadir}/sddm/themes/aero/
fi

# Install sound files
if [ -f "misc/sounds/sounds.tar.gz" ]; then
  tar -xf misc/sounds/sounds.tar.gz -C %{buildroot}%{_datadir}/sounds
fi

# Install icons and cursors
tar -xf "misc/icons/Windows 7 Aero.tar.gz" -C %{buildroot}%{_datadir}/icons
tar -xf misc/cursors/aero-drop.tar.gz -C %{buildroot}%{_datadir}/icons

# Install color scheme
install -Dm644 plasma/color_scheme/AeroColorScheme1.colors \
  %{buildroot}%{_datadir}/color-schemes/AeroColorScheme1.colors

# Install plasma desktop theme
mkdir -p %{buildroot}%{_datadir}/plasma/desktoptheme/Seven-Black
cp -r plasma/desktoptheme/Seven-Black/* %{buildroot}%{_datadir}/plasma/desktoptheme/Seven-Black/

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

# Create default KDE config files
mkdir -p %{buildroot}%{_sysconfdir}/xdg

# Set default plasma theme
cat > %{buildroot}%{_sysconfdir}/xdg/plasmarc << 'EOF'
[Theme]
name=Seven-Black
EOF

# Set default color scheme
cat > %{buildroot}%{_sysconfdir}/xdg/kdeglobals << 'EOF'
[General]
ColorScheme=AeroColorScheme1
Name=Winblues 7
XftAntialias=true
XftHintStyle=hintslight
XftSubPixel=rgb
fixed=Monospace,10,-1,5,50,0,0,0,0,0
font=Segoe UI,10,-1,5,50,0,0,0,0,0
menuFont=Segoe UI,10,-1,5,50,0,0,0,0,0
smallestReadableFont=Segoe UI,8,-1,5,50,0,0,0,0,0
toolBarFont=Segoe UI,9,-1,5,50,0,0,0,0,0
audioTheme=WindowsMedia

[KDE]
LookAndFeelPackage=authui7
SingleClick=false

[WM]
activeFont=Segoe UI,10,-1,5,50,0,0,0,0,0
EOF

# Set default window decoration
cat > %{buildroot}%{_sysconfdir}/xdg/kwinrc << 'EOF'
[org.kde.kdecoration2]
library=org.smod.smod
theme=

[Plugins]
blurEnabled=true
contrastEnabled=false
EOF

# Set default cursor theme
cat > %{buildroot}%{_sysconfdir}/xdg/kcminputrc << 'EOF'
[Mouse]
cursorTheme=Aero-drop
EOF

# Set SDDM theme
mkdir -p %{buildroot}%{_sysconfdir}/sddm.conf.d
cat > %{buildroot}%{_sysconfdir}/sddm.conf.d/10-aero-theme.conf << 'EOF'
[Theme]
Current=aero
EOF

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
%{_datadir}/aerotheme
%{_datadir}/mime/packages/*
%{_libdir}/qt6/plugins/org.kde.kdecoration3/org.smod.smod.so
%{_libdir}/qt6/plugins/kwin/effects/*.so
%{_datadir}/kwin/effects/*/
%{_datadir}/kpackage/KWin/Effect/*
%{_datadir}/locale/*/LC_MESSAGES/breeze_kwin_deco.mo
%{_datadir}/locale/*/LC_MESSAGES/smod_deco.mo
%config(noreplace) %{_sysconfdir}/fonts/conf.d/99-aerotheme-segoe.conf
%config(noreplace) %{_sysconfdir}/xdg/plasmarc
%config(noreplace) %{_sysconfdir}/xdg/kdeglobals
%config(noreplace) %{_sysconfdir}/xdg/kwinrc
%config(noreplace) %{_sysconfdir}/xdg/kcminputrc
%config(noreplace) %{_sysconfdir}/sddm.conf.d/10-aero-theme.conf


%changelog
* Thu May 08 2025 Adam Fidel <adam@fidel.cloud> - 0-0.1.20250508git3c2990e
- Initial RPM packaging of AeroThemePlasma
