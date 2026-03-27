rebase:
  #!/bin/bash
  bluebuild switch -B podman --tempdir /var/tmp recipes/recipe.yml

build:
  #!/bin/bash
  bluebuild build -B podman --tempdir /var/tmp recipes/recipe.yml

build-atp-oci:
  #!/bin/bash
  set -euo pipefail
  SHA=$(cat atp-commit.txt | tr -d '[:space:]')
  SHORT_SHA=${SHA:0:7}
  TAG="${SHORT_SHA}-fc43"
  podman run --rm \
    --volume ./:/workspace:Z \
    registry.fedoraproject.org/fedora:43 \
    bash /workspace/build/build-atp.sh
  oras push \
    ghcr.io/winblues/aerothemeplasma:${TAG} \
    --artifact-type application/vnd.aerothemeplasma.config.v1+json \
    ./atp-files.tar.gz:application/vnd.aerothemeplasma.files.v1.tar+gzip
  echo "Pushed ghcr.io/winblues/aerothemeplasma:${TAG}"

update-atp-commit:
  #!/bin/bash
  set -euo pipefail
  SHA=$(git ls-remote https://gitgud.io/wackyideas/aerothemeplasma.git HEAD | cut -f1)
  echo "$SHA" > atp-commit.txt
  echo "Updated atp-commit.txt to ${SHA:0:7}"
