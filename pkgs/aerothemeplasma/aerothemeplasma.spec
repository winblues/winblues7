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

BuildRequires:  cmake ninja-build make gcc-c++
BuildRequires:  qt6-qtbase-devel qt6-qtbase-private-devel qt6-qtsvg-devel qt6-qt5compat-devel
BuildRequires:  kf6-kpackage-devel kf6-kio-devel kf6-ksvg-devel kf6-karchive-devel
BuildRequires:  plasma-workspace-devel kwin-devel kdecoration-devel
BuildRequires:  kf6-kiconthemes-devel kf6-kcmutils-devel kf6-kglobalaccel-devel
BuildRequires:  qt6-qtmultimedia-devel qt6-qtwayland-devel wayland-devel plasma-wayland-protocols-devel
Requires:       kpackagetool6 sddmthemeinstaller tar unzip kfontinst

%description
AeroThemePlasma is a KDE Plasma desktop customization that mimics the visual style of Windows 7, including cursors, sounds, color schemes, KWin effects, and SDDM theme.

%setup -q -n aerothemeplasma-%{commit}

%build
# Build KWin decorations
pushd kwin/decoration
%cmake -G Ninja
%ninja_build
popd

# Build KWin C++ effects
for dir in kwin/effects_cpp/*; do
  if [ -d "$dir" ]; then
    pushd "$dir"
    %cmake -G Ninja
    %ninja_build
    popd
  fi
done

# Build plasmoids
for dir in plasma/plasmoids/src/*; do
  if [ -d "$dir" ]; then
    pushd "$dir"
    %cmake -G Ninja
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

# Install Kvantum config, SDDM, icons, cursors, mimetypes, color schemes, etc.
cp -r misc/smod %{buildroot}%{_datadir}/
tar -xf misc/sounds/sounds.tar.gz -C %{buildroot}%{_datadir}/sounds
tar -xf misc/icons/Windows\ 7\ Aero.tar.gz -C %{buildroot}%{_datadir}/icons
tar -xf misc/cursors/aero-drop.tar.gz -C %{buildroot}%{_datadir}/icons

install -Dm644 plasma/color_scheme/AeroColorScheme1.colors \
  %{buildroot}%{_datadir}/color-schemes/AeroColorScheme1.colors

cp -r misc/mimetype/* %{buildroot}%{_datadir}/mime/packages/

# Fontconfig override (disabled by default, user can symlink if desired)
install -Dm644 misc/fontconfig/fonts.conf \
  %{buildroot}%{_sysconfdir}/fonts/conf.d/99-aerotheme-segoe.conf

# Branding files (optional)
mkdir -p %{buildroot}%{_datadir}/aerotheme/branding
cp -r misc/branding/* %{buildroot}%{_datadir}/aerotheme/branding/

# Plasmoid and KWin component sources
cp -r plasma %{buildroot}%{_datadir}/aerotheme/plasma
cp -r kwin %{buildroot}%{_datadir}/aerotheme/kwin

%files
%license LICENSE
%doc README.md
%{_datadir}/smod
%{_datadir}/sounds/*
%{_datadir}/icons/*
%{_datadir}/color-schemes/AeroColorScheme1.colors
%{_datadir}/mime/packages/*
%{_datadir}/aerotheme
%config(noreplace) %{_sysconfdir}/fonts/conf.d/99-aerotheme-segoe.conf

%changelog
* Wed Apr 23 2025 Adam Fidel <adam@blues.win> - 0-0.1.20250423git3c2990e
- Initial RPM packaging of AeroThemePlasma

