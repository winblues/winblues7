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
    plasma-activities-devel \
    plasma-activities-stats-devel \
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
    libdrm-devel \
    polkit-qt6-1-devel \
    libksysguard-devel \
    kf6-kitemmodels-devel

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
        -DCMAKE_PREFIX_PATH="$DESTDIR$PREFIX" \
        "$@"
    cmake --build "$REPOS/$name/build" -j"$NPROC"
    DESTDIR="$DESTDIR" cmake --install "$REPOS/$name/build"
}

# 1. libplasma  (base library, must come first)
cmake_build_install \
    https://gitgud.io/aeroshell/libplasma.git \
    libplasma

# 2. uac-polkit-agent
cmake_build_install \
    https://gitgud.io/aeroshell/uac-polkit-agent.git \
    uac-polkit-agent \
    -DCMAKE_INSTALL_LIBEXECDIR=libexec/kf6

# 3. SMOD  (window decoration + glow effect)
cmake_build_install \
    https://gitgud.io/aeroshell/smod.git \
    smod

# 4. aeroshell-workspace  (plasmoids, plasma components)
cmake_build_install \
    https://gitgud.io/aeroshell/aeroshell-workspace.git \
    aeroshell-workspace

# 5. aeroshell-kwin-components  (Wayland KWin effects/scripts)
cmake_build_install \
    https://gitgud.io/aeroshell/aeroshell-kwin-components.git \
    aeroshell-kwin-components \
    -DKWIN_BUILD_WAYLAND=ON

# 6. aeroshell-sddm-kcm  (SDDM configuration KCM)
cmake_build_install \
    https://gitgud.io/aeroshell/aeroshell-sddm-kcm.git \
    aeroshell-sddm-kcm

# 7. aerothemeplasma-icons
cmake_build_install \
    https://gitgud.io/aeroshell/atp/aerothemeplasma-icons.git \
    aerothemeplasma-icons

# 8. aerothemeplasma-sounds
cmake_build_install \
    https://gitgud.io/aeroshell/atp/aerothemeplasma-sounds.git \
    aerothemeplasma-sounds

# 9. aerothemeplasma main repo  (plasma themes, misc; pinned commit)
git init "$REPOS/aerothemeplasma"
git -C "$REPOS/aerothemeplasma" remote add origin https://gitgud.io/wackyideas/aerothemeplasma.git
git -C "$REPOS/aerothemeplasma" fetch --depth=1 origin "$ATP_COMMIT"
git -C "$REPOS/aerothemeplasma" checkout FETCH_HEAD

echo "=== aerothemeplasma root listing ==="
ls "$REPOS/aerothemeplasma/"
echo "=== CMakeLists.txt search ==="
find "$REPOS/aerothemeplasma" -name 'CMakeLists.txt' -not -path '*/.git/*' | sort

if [ -f "$REPOS/aerothemeplasma/CMakeLists.txt" ]; then
    cmake \
        -S "$REPOS/aerothemeplasma" \
        -B "$REPOS/aerothemeplasma/build" \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="$PREFIX" \
        -DCMAKE_PREFIX_PATH="$DESTDIR$PREFIX" \
        -DCMAKE_INSTALL_LIBEXECDIR=libexec
    cmake --build "$REPOS/aerothemeplasma/build" -j"$NPROC"
    DESTDIR="$DESTDIR" cmake --install "$REPOS/aerothemeplasma/build"
else
    echo "No root CMakeLists.txt — building each top-level cmake subdirectory"
    while IFS= read -r cmakefile; do
        subdir=$(dirname "$cmakefile")
        parent=$(dirname "$subdir")
        # Skip nested cmake projects (parent also has CMakeLists.txt)
        [ -f "$parent/CMakeLists.txt" ] && continue
        cmake \
            -S "$subdir" \
            -B "$subdir/build" \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_INSTALL_PREFIX="$PREFIX" \
            -DCMAKE_PREFIX_PATH="$DESTDIR$PREFIX" \
            -DCMAKE_INSTALL_LIBEXECDIR=libexec
        cmake --build "$subdir/build" -j"$NPROC"
        DESTDIR="$DESTDIR" cmake --install "$subdir/build"
    done < <(find "$REPOS/aerothemeplasma" -name 'CMakeLists.txt' -not -path '*/.git/*' -maxdepth 3 | sort)
fi

SHORT_SHA=${ATP_COMMIT:0:7}
echo "=== Installed file list ==="
find "$DESTDIR" -type f | sort
echo "=== End of file list ==="

tar -czf /workspace/atp-files.tar.gz -C "$DESTDIR" .
echo "Built: atp-files.tar.gz (commit ${SHORT_SHA}, $(du -sh /workspace/atp-files.tar.gz | cut -f1))"
