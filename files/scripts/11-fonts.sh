#!/bin/bash

set -exuo pipefail

cd /tmp
wget https://github.com/mrbvrz/segoe-ui-linux/archive/refs/heads/master.zip
unzip master.zip
cd segoe-ui-linux-master

mkdir -p /usr/share/fonts/Microsoft/TrueType/SegoeUI/
mv font/* /usr/share/fonts/Microsoft/TrueType/SegoeUI
fc-cache -f /usr/share/fonts/Microsoft/TrueType/SegoeUI/
