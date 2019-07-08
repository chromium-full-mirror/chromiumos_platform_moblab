#!/bin/bash
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Script to generate a new empty base container for moblab, to use:
# 1) In a chroot install the most up to date lxc:
#    sudo USE=-python emerge lxc
# 2) Have a moblab online with the same version of lxc
# 3) ./build_base_image.sh <base_image_version_number> <ip of moblab>

set -x
set -e

DIRECTORY=$(pwd)
CONTAINER_NAME="moblab_base_${1}"
DISTRIBUTION="ubuntu"
REVISION="bionic"
ARCH="amd64"

MOBLAB_IP_ADDRESS="${2}"
MOBLAB_DIRECTORY="/mnt/moblab/containers"

PACKAGES="wget curl python2.7 unzip rsync openjdk-8-jre \
          gnupg lsb-release "
PYTHON_PACKAGES="lxml numpy crcmod"
function generate_package_install_script() {
  read -r -d '' PACKAGE_INSTALL_SCRIPT << EOM
  set -x
  # Wait for the networking to come up.
  sleep 60
  # Ensure the container is up to date
  sudo apt-get -y update
  sudo apt-get -y upgrade
  # Install the required packages
  sudo apt-get -y install ${PACKAGES}
  # Install the google cloud sdk
  export CLOUD_SDK_REPO="cloud-sdk-\$(lsb_release -c -s)"
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    sudo apt-key add -
  echo "deb http://packages.cloud.google.com/apt \$CLOUD_SDK_REPO main" | \
    sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
  sudo apt-get -y update
  sudo apt-get --no-install-recommends -y install google-cloud-sdk
  apt-get -y autoremove
  apt-get -y autoclean
  apt-get -y clean
  rm -rf /var/lib/apt/lists
  gsutil -v
  export PAGER=/bin/more
  nmcli
  nmcli con mod 'Wired connection 1' ipv4.dns '8.8.8.8 1.1.1.1 8.8.4.4 1.0.0.1'
  wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
  python2.7 /tmp/get-pip.py --target /usr/lib/python2.7/dist-packages
  python2.7 -m pip install --upgrade pip setuptools wheel ${PYTHON_PACKAGES}\
    --target /usr/lib/python2.7/dist-packages
EOM
}

function generate_container_control_script() {
  read -r -d '' CONTAINER_INIT_SCRIPT << EOM
  cd "${MOBLAB_DIRECTORY}"
  sudo lxc-stop -P "${MOBLAB_DIRECTORY}" -n ${CONTAINER_NAME}
  sudo rm -rf "${CONTAINER_NAME}"
  sudo tar xf "${CONTAINER_NAME}".tar
  sudo rm "${CONTAINER_NAME}".tar
  sudo lxc-start -P "${MOBLAB_DIRECTORY}" -n "${CONTAINER_NAME}" \
    -d -l trace -o lxc-start-trace-"${CONTAINER_NAME}"
  sudo lxc-attach -P "${MOBLAB_DIRECTORY}" -n "${CONTAINER_NAME}" \
    -- /usr/local/bin/container_install_script.sh
  sudo lxc-stop -P "${MOBLAB_DIRECTORY}" -n "${CONTAINER_NAME}"
  sudo tar -cJpf "${CONTAINER_NAME}".tar.xz "${CONTAINER_NAME}"
EOM
}

# This is just for documentation - it will not run in chroot, run outside
# and then use the output inside chroot.
function initial_setup() {
  go get -d -v github.com/lxc/distrobuilder ||
  cd "${HOME}/go/src/github.com/lxc/distrobuilder"
  make
  cd -
  sudo $HOME/go/bin/distrobuilder build-lxc ubuntu.yaml
}

function create_new_empty_container() {
  # Create a new empty container using a lxc templates
  sudo rm -rf "${DIRECTORY}/${CONTAINER_NAME}"
  sudo lxc-create -P "${DIRECTORY}" -t local -n "${CONTAINER_NAME}" -- -m ./meta.tar.xz -f ./rootfs.tar.xz

  # Set up the networking for the container on moblab
  local network_config="lxc.net.0.type = veth\nlxc.net.0.flags = up\nlxc.net.0.link = lxcbr0\nlxc.net.0.hwaddr = 00:16:3e:0a:31:c2"

  sudo sed -E s#"^lxc.rootfs.path =.*"#"lxc.rootfs.path = dir:/mnt/moblab/containers/${CONTAINER_NAME}/rootfs"#g -i "${DIRECTORY}/${CONTAINER_NAME}/config"

  # Install a script that will setup the container on the moblab.
  rm /tmp/container_install_script
  echo "${PACKAGE_INSTALL_SCRIPT}" >> /tmp/container_install_script
  local install_script_file="${DIRECTORY}"/"${CONTAINER_NAME}"\
/rootfs/usr/local/bin/container_install_script.sh
  sudo cp /tmp/container_install_script "${install_script_file}"
  sudo chmod uog+x "${install_script_file}"

  # Tar up the newly created container preserving permissions
  cd "${DIRECTORY}" || exit
  sudo tar -cJpf "${CONTAINER_NAME}".tar "${CONTAINER_NAME}"
}

function copy_container_to_moblab() {
  scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
    "${CONTAINER_NAME}".tar \
    moblab@"${MOBLAB_IP_ADDRESS}":/mnt/moblab/containers
}

function start_container_and_run_install_script() {
  ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
  moblab@"${MOBLAB_IP_ADDRESS}" "${CONTAINER_INIT_SCRIPT}"
}

function retrieve_container_from_moblab() {
  sudo rm -rf "${DIRECTORY}/${CONTAINER_NAME}.tar.xz"
  scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
  moblab@"${MOBLAB_IP_ADDRESS}"\
:/mnt/moblab/containers/"${CONTAINER_NAME}".tar.xz .
}

initial_setup
# Generate a new empty continer in a chroot you can not create new containers
# on moblab due /etc being RO filesystem
generate_package_install_script
create_new_empty_container

# Copy the newly created container to the moblab
copy_container_to_moblab

# Unpack and start the container on moblab, run the install script
generate_container_control_script
start_container_and_run_install_script

retrieve_container_from_moblab
