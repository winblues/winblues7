rebase:
  #!/bin/bash
  bluebuild switch -B podman --tempdir /var/tmp recipes/recipe.yml

build:
  #!/bin/bash
  bluebuild build -B podman --tempdir /var/tmp recipes/recipe.yml

# Build ATP inside a Fedora 43 container; produces ./atp-files.tar.gz locally.
build-atp:
  #!/bin/bash
  set -euo pipefail
  podman run --rm \
    --volume ./:/workspace:Z \
    registry.fedoraproject.org/fedora:43 \
    bash /workspace/build/build-atp.sh

# Push an already-built ./atp-files.tar.gz to GHCR.
push-atp:
  #!/bin/bash
  set -euo pipefail
  SHA=$(cat atp-commit.txt | tr -d '[:space:]')
  TAG="${SHA:0:7}-fc43"
  oras push \
    ghcr.io/winblues/aerothemeplasma:${TAG} \
    --artifact-type application/vnd.aerothemeplasma.config.v1+json \
    ./atp-files.tar.gz:application/vnd.aerothemeplasma.files.v1.tar+gzip
  echo "Pushed ghcr.io/winblues/aerothemeplasma:${TAG}"

# Build and push in one step (used by CI).
build-atp-oci: build-atp push-atp

update-atp-commit:
  #!/bin/bash
  set -euo pipefail
  SHA=$(git ls-remote https://gitgud.io/wackyideas/aerothemeplasma.git HEAD | cut -f1)
  echo "$SHA" > atp-commit.txt
  echo "Updated atp-commit.txt to ${SHA:0:7}"
