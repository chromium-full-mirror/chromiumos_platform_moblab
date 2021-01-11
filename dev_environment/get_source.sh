#!/bin/bash
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

git clone https://chromium.googlesource.com/chromiumos/platform/moblab

cd moblab

read -p "Enter Your Email (chromium.org if you have otherwise google.com): "  email
git config --global user.email "${email}"
read -p "Enter your first and last name for Git to use in reviews "  name
git config --global user.name "${name}"
git config --local remote.origin.review https://chromium-review.googlesource.com
f=`git rev-parse --git-dir`/hooks/commit-msg ; mkdir -p $(dirname $f)
curl -Lo $f https://gerrit-review.googlesource.com/tools/hooks/commit-msg
chmod +x $f

# Set up all the git hooks
hooks4git --init

# Set up google cloud access
gcloud auth login
gcloud auth configure-docker
gcloud auth configure-docker us-docker.pkg.dev

# Create an override just using the defaults
cp src/dockerfiles/compose/.env src/dockerfiles/compose/override.env

echo "export REGISTRY=$(hostname -I | awk -F ' ' '{print $1}'):5000" > src/local_registry.mk
# Let the user know to set up git credentials
echo "In a browser go to https://www.googlesource.com/new-password and paste"
echo "the generated code into this shell."
