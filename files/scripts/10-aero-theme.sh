#!/bin/bash

set -exuo pipefail

URL=https://github.com/winblues/blue7/releases/download/aerothemeplasma-0-0.1.20250507git3c2990e.fc42/aerothemeplasma-0-0.1.20250507git3c2990e.fc42.x86_64.rpm

curl -L -o /tmp/aerothemeplasma.rpm "$URL"

RUN mkdir -p /tmp/winblues7-overlay

RUN cd /tmp/winblues7-overlay && \
    rpm2cpio /tmp/aerothemeplasma.rpm | cpio -idmv

RUN cp -rf /tmp/winblues7-overlay/usr/* /usr/ && \
    cp -rf /tmp/winblues7-overlay/etc/* /etc/ && \
    rm -rf /tmp/winblues7-overlay /tmp/*.rpm