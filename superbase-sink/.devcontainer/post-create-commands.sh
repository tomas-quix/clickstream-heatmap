#!/bin/bash
apt-get update
apt-get install -y curl
curl -fsSL https://github.com/quixio/quix-cli/raw/main/install.sh | bash -s -- -v=0.0.1-20240214.6
# other commands