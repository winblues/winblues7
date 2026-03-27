#!/bin/bash
# Builds AeroThemePlasma and all its sub-repos inside a Fedora 43 container.
# Produces /workspace/atp-files.tar.gz containing the full installed filesystem tree.
#
# Expected mount: -v <repo-root>:/workspace:Z
# Expected files:  /workspace/atp-commit.txt (pinned aerothemeplasma commit SHA)

set -exuo pipefail

DESTDIR=/tmp/atp-destdir
REPOS=/tmp/atp-repos
PREFIX=/usr
NPROC=$(nproc)

# ---------------------------------------------------------------------------
# Build dependencies
# ---------------------------------------------------------------------------
dnf install -y \
    git cmake make gcc-c++ ninja-build extra-cmake-modules pkgconfig \
    kf6-ki18n-devel \
    kf6-kconfig-devel \
    kf6-kguiaddons-devel \
    kf6-kcoreaddons-devel \
    kf6-kpackage-devel \
    kf6-kio-devel \
    kf6-ksvg-devel \
    kf6-karchive-devel \
    kf6-kiconthemes-devel \
    kf6-kcmutils-devel \
    kf6-kglobalaccel-devel \
    kf6-kcrash-devel \
    kf6-kdeclarative-devel \
    kf6-kdbusaddons-devel \
    kf6-solid-devel \
    kf6-knotifications-devel \
    kf6-kwidgetsaddons-devel \
    kf6-kirigami-devel \
    kf6-kirigami-addons-devel \
    kf6-frameworkintegration-devel \
    plasma-workspace-devel \
    kwin-devel \
    kdecoration-devel \
    qt6-qtbase-devel \
    qt6-qtbase-private-devel \
    qt6-qtsvg-devel \
    qt6-qt5compat-devel \
    qt6-qtmultimedia-devel \
    qt6-qtwayland-devel \
    qt6-qtdeclarative-devel \
    wayland-devel \
    plasma-wayland-protocols-devel \
    libepoxy-devel \
    libdrm-devel

mkdir -p "$REPOS" "$DESTDIR"

ATP_COMMIT=$(cat /workspace/atp-commit.txt | tr -d '[:space:]')

# ---------------------------------------------------------------------------
# Helper: clone, cmake-build, and DESTDIR-install a repo
# ---------------------------------------------------------------------------
cmake_build_install() {
    local url=$1
    local name=$2
    shift 2
    # remaining args are passed to cmake configure

    git clone --depth=1 "$url" "$REPOS/$name"
    cmake \
        -S "$REPOS/$name" \
        -B "$REPOS/$name/build" \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="$PREFIX" \
        "$@"
    cmake --build "$REPOS/$name/build" -j"$NPROC"
    cmake --install "$REPOS/$name/build" --destdir "$DESTDIR"
}

# ---------------------------------------------------------------------------
# 1. libplasma  (base library, must come first)
# ---------------------------------------------------------------------------
cmake_build_install \
    https://gitgud.io/aeroshell/libplasma.git \
    libplasma

# ---------------------------------------------------------------------------
# 2. uac-polkit-agent
# ---------------------------------------------------------------------------
cmake_build_install \
    https://gitgud.io/aeroshell/uac-polkit-agent.git \
    uac-polkit-agent \
    -DCMAKE_INSTALL_LIBEXECDIR=libexec/kf6

# ---------------------------------------------------------------------------
# 3. SMOD  (window decoration + glow effect)
# ---------------------------------------------------------------------------
cmake_build_install \
    https://gitgud.io/aeroshell/smod.git \
    smod

# ---------------------------------------------------------------------------
# 4. aeroshell-workspace  (plasmoids, plasma components)
# ---------------------------------------------------------------------------
cmake_build_install \
    https://gitgud.io/aeroshell/aeroshell-workspace.git \
    aeroshell-workspace

# ---------------------------------------------------------------------------
# 5. aeroshell-kwin-components  (Wayland KWin effects/scripts)
# ---------------------------------------------------------------------------
cmake_build_install \
    https://gitgud.io/aeroshell/aeroshell-kwin-components.git \
    aeroshell-kwin-components \
    -DKWIN_BUILD_WAYLAND=ON

# ---------------------------------------------------------------------------
# 6. aeroshell-sddm-kcm  (SDDM configuration KCM)
# ---------------------------------------------------------------------------
cmake_build_install \
    https://gitgud.io/aeroshell/aeroshell-sddm-kcm.git \
    aeroshell-sddm-kcm

# ---------------------------------------------------------------------------
# 7. aerothemeplasma-icons
# ---------------------------------------------------------------------------
cmake_build_install \
    https://gitgud.io/aeroshell/atp/aerothemeplasma-icons.git \
    aerothemeplasma-icons

# ---------------------------------------------------------------------------
# 8. aerothemeplasma-sounds
# ---------------------------------------------------------------------------
cmake_build_install \
    https://gitgud.io/aeroshell/atp/aerothemeplasma-sounds.git \
    aerothemeplasma-sounds

# ---------------------------------------------------------------------------
# 9. aerothemeplasma main repo  (plasma themes, misc; pinned commit)
# ---------------------------------------------------------------------------
git clone https://gitgud.io/wackyideas/aerothemeplasma.git "$REPOS/aerothemeplasma"
git -C "$REPOS/aerothemeplasma" checkout "$ATP_COMMIT"

cmake \
    -S "$REPOS/aerothemeplasma" \
    -B "$REPOS/aerothemeplasma/build" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DCMAKE_INSTALL_LIBEXECDIR=libexec
cmake --build "$REPOS/aerothemeplasma/build" -j"$NPROC"
cmake --install "$REPOS/aerothemeplasma/build" --destdir "$DESTDIR"

# ---------------------------------------------------------------------------
# Package
# ---------------------------------------------------------------------------
SHORT_SHA=${ATP_COMMIT:0:7}
echo "=== Installed file list ==="
find "$DESTDIR" -type f | sort
echo "=== End of file list ==="

tar -czf /workspace/atp-files.tar.gz -C "$DESTDIR" .
echo "Built: atp-files.tar.gz (commit ${SHORT_SHA}, $(du -sh /workspace/atp-files.tar.gz | cut -f1))"
