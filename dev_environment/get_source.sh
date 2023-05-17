#!/bin/bash
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

git clone https://chromium.googlesource.com/chromiumos/platform/moblab
git clone https://chromium.googlesource.com/chromiumos/platform/satlab
git clone https://chromium.googlesource.com/chromiumos/platform/xolabs-common-core
git clone https://chromium.googlesource.com/chromiumos/config
git clone https://chromium.googlesource.com/chromiumos/infra/proto

set -euo pipefail

function setup_git() {
    pushd "${1}"
    git config --local user.email "${2}"
    git config --local user.name "${3}"
    git config --local remote.origin.review https://chromium-review.googlesource.com
    f=`git rev-parse --git-dir`/hooks/commit-msg ; mkdir -p $(dirname $f)
    curl -Lo $f https://gerrit-review.googlesource.com/tools/hooks/commit-msg
    chmod +x $f
    popd
}

read -p "Enter Your Email (chromium.org if you have otherwise google.com): "  email
read -p "Enter your first and last name for Git to use in reviews "  name

for repo in "moblab" "satlab" "xolabs-common-core" "config" "proto"; do
    setup_git "$repo" "${email}" "${name}"
done

# Set up all the git hooks on moblab ( moblab presubmit checks )
cd moblab
hooks4git --init
rm .hooks4git-*

# Set up google cloud access
gcloud auth login
gcloud auth configure-docker
gcloud auth configure-docker us-docker.pkg.dev

# Create an override just using the defaults
cp src/dockerfiles/compose/.env src/dockerfiles/compose/override.env

echo "export REGISTRY := $(hostname -i | awk -F ' ' '{print $1}'):5000" > src/local_registry.mk

# Let the user know to set up git credentials
echo "In a browser go to https://www.googlesource.com/new-password and paste"
echo "the generated code into this shell."
