#!/bin/bash

set -exuo pipefail

VERSION=0-0.9.20260204gitd572194.fc43
URL=https://github.com/winblues/winblues7/releases/download/aerothemeplasma-${VERSION}/aerothemeplasma-${VERSION}.x86_64.rpm

curl -L -o /tmp/aerothemeplasma.rpm "$URL"

mkdir -p /tmp/winblues7-overlay

cd /tmp/winblues7-overlay &&
  rpm2cpio /tmp/aerothemeplasma.rpm | cpio -idmv

cp -rf /tmp/winblues7-overlay/usr/* /usr/ &&
  cp -rf /tmp/winblues7-overlay/etc/* /etc/ &&
  rm -rf /tmp/winblues7-overlay /tmp/*.rpm

kbuildsycoca6
update-mime-database /usr/share/mime
