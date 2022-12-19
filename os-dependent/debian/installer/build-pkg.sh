#!/bin/bash
# Script to create debian package for moblab-linux

set -e

PACKAGE=moblab
VERSION=0.0
MOBLAB_VER=${PACKAGE}-${VERSION}
echo "creating apt package: ${MOBLAB_VER}"

SOURCE_DIR=moblab_not_to_push
mkdir -p ${SOURCE_DIR}
mkdir -p ${SOURCE_DIR}/scripts
mkdir -p ${SOURCE_DIR}/init
mkdir -p ${SOURCE_DIR}/debian

cp Makefile_deb ${SOURCE_DIR}/Makefile

cp ../moblab_start     ${SOURCE_DIR}/scripts/moblab_start
cp ../moblab_stop      ${SOURCE_DIR}/scripts/moblab_stop
cp ../moblab_reset     ${SOURCE_DIR}/scripts/moblab_reset
cp ../moblab_prepare   ${SOURCE_DIR}/scripts/moblab_prepare
cp ../moblab_configure ${SOURCE_DIR}/scripts/moblab_configure

cp ../moblab_setup_configuration.conf ${SOURCE_DIR}/moblab_setup_configuration.conf

cp ../init/moblab-networking  ${SOURCE_DIR}/init/moblab-networking
cp ../init/moblab-host-server ${SOURCE_DIR}/init/moblab-host-server

cp ../host_server_debian.py ${SOURCE_DIR}/scripts/host_server_debian.py
cp -r ../../common ${SOURCE_DIR}/scripts/

# now copy the debian-pkg creation related files
cp pkg_files/* ${SOURCE_DIR}/debian/
# Create the package.
# Execution the command expected to be run in the folder.
cd ${SOURCE_DIR}
debuild -us -uc
cd ..
echo "Moblab package successfully created!"

upload_package()
{
  echo "---== starting upload packages ==---"
  # Before try to upload run this commands.
  # sudo apt install apt-transport-artifact-registry
  # echo 'deb ar+https://us-central1-apt.pkg.dev/projects/chromeos-partner-moblab moblab-linux main' | sudo tee -a  /etc/apt/sources.list.d/artifact-registry.list
  gcloud artifacts apt upload moblab-linux --source="moblab_0.0-5_all.deb" --project=chromeos-partner-moblab
}

if [[ $1 == upload ]]; then
    upload_package
fi