#!/bin/bash

set -exuo pipefail

SHA=3f17650
FC_VERSION=43
REGISTRY=ghcr.io/winblues/aerothemeplasma

oras pull "${REGISTRY}:${SHA}-fc${FC_VERSION}" --output /tmp/atp-files
tar -xzf /tmp/atp-files/atp-files.tar.gz -C /
rm -rf /tmp/atp-files

kbuildsycoca6
