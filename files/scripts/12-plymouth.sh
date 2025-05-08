#!/bin/bash

set -exuo pipefail

COMMIT=dadc995c6e7d68d1e28b6429e0e2eacb2ce1cc41
URL=https://github.com/furkrn/PlymouthVista/archive/${COMMIT}.zip

cd /tmp
curl -L -o plymouth-vista.zip $URL
unzip plymouth-vista.zip
cd PlymouthVista-${COMMIT}

bash ./compile.sh

bash ./gen_blur.sh

    # I won't bother with a proper better way, this just works :\
    sed -i '/# START_WIN7_CONFIG/,/# END_WIN7_CONFIG/{ 
    /# START_WIN7_CONFIG/!{ 
        /# END_WIN7_CONFIG/!d 
    } 
    r /dev/stdin
}' PlymouthVista.script <<EOF
// Use Vista boot which is available even on Windows 11.
// 1 - Use Vista boot screen
// 0 - Use 7 boot screen
global.UseLegacyBootScreen = 0;

// Add shadow effect to shutdown screen text.
// 0 - Windows Vista style, no text shadow.
// 1 - Windows 7 style, show text shadow. 
global.UseShadow = 1;

// Change the background of the shutdown screen.
// vista - Use Vista background and branding.
// 7 - Use 7 background and branding.
global.AuthuiStyle = "7";
EOF


# "Do you want fade in effects in shutdown?"
# "1 - Automatic (Fade when shutdown is called from your desktop, don't fade when shutdown is called from SDDM)"
# "2 - Always (Fade when shutdown is called from your desktop, fade when shutdown is called from SDDM)"
# "3 - Never (Don't fade when shutdown is called from your desktop, don't fade when shutdown is called from SDDM)"
INPUT=2

if [[ $INPUT != 1 ]] && [[ $INPUT != 2 ]] then
    $INPUT = 0;
fi

sed -i '/# START_USED_BY_INSTALL_SCRIPT_PREF/,/# END_USED_BY_INSTALL_SCRIPT_PREF/{ 
    /# START_USED_BY_INSTALL_SCRIPT_PREF/!{ 
        /# END_USED_BY_INSTALL_SCRIPT_PREF/!d 
    } 
    r /dev/stdin
}' PlymouthVista.script <<EOF
global.Pref = $INPUT;
EOF

cp ./lucon_disable_anti_aliasing.conf /etc/fonts/conf.d/10-lucon_disable_anti_aliasing.conf

rm -rf /usr/share/plymouth/themes/PlymouthVista

cp -r $(pwd) /usr/share/plymouth/themes/PlymouthVista
ls -la /usr/share/plymouth/themes/PlymouthVista

if [[ $INPUT = 1 ]] then
    echo "Creating automatic services"
    chmod -R 777 /usr/share/plymouth/themes/PlymouthVista/

    cp $(pwd)/systemd/system/* /etc/systemd/system
    for f in $(pwd)/systemd/system/*.service; do
        systemctl enable $(basename $f)
    done

    cp $(pwd)/systemd/user/* /etc/systemd/user
        for f in $(pwd)/systemd/user/*.service; do
        systemctl --user -M $SUDO_USER@ enable update-plymouth-vista-state-logon.service
    done

fi

plymouth-set-default-theme PlymouthVista
