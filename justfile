rebase:
  #!/bin/bash
  bluebuild switch --tempdir /var/tmp recipes/recipe.yml

build-rpm:
  #!/bin/bash
  podman run --rm --cap-add=SYS_ADMIN --privileged --volume ./:/anda --volume mock_cache:/var/lib/mock --workdir /anda ghcr.io/terrapkg/builder:frawhide anda \
      build -c terra-rawhide-x86_64 pkgs/aerothemeplasma/pkg
