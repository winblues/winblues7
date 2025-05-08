rebase:
  #!/bin/bash
  bluebuild switch --tempdir /var/tmp recipes/recipe.yml

build:
  #!/bin/bash
  bluebuild build -B podman --tempdir /var/tmp recipes/recipe.yml

build-rpm:
  #!/bin/bash
  podman run --rm --cap-add=SYS_ADMIN --privileged --volume ./:/anda --volume mock_cache:/var/lib/mock --workdir /anda ghcr.io/terrapkg/builder:f42 anda \
      build -c terra-42-x86_64 pkgs/aerothemeplasma/pkg
