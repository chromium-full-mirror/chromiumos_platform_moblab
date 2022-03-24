#!/bin/bash

# THIS script requires board as a parameter
# READ BELOW ASSUMPTIONS BEFORE YOU USE:
# Assumption 1: your chromiumos repo exists at ~/chromiumos. If not, change the below variable

base_dir="$HOME/chromiumos"
if [ "$1" = "" ]; then
	echo 'please pass in board as first parameter'
	exit
fi

board=$1
echo 'board is set as '$board


# STEP 1: build the image after building the packages
# eval is needed below because of command substitution and "~" usage in base_dir 
eval cd ${base_dir}/src/third_party/chromiumos-overlay/chromeos/config

milestone_string=$(./chromeos_version.sh |grep "^[[:space:]]*CHROME_BRANCH=" |cut -d= -f2 | tr - _) 
version_string=$(./chromeos_version.sh |grep "^[[:space:]]*CHROMEOS_VERSION_STRING=" |cut -d= -f2 | tr - _)

cd ${base_dir}
# keep the build path as $board-local (adding extra words will cause issues)
full_build_path="$board-local/R$milestone_string-$version_string-a1"
echo 'full build path: '$full_build_path

cros_sdk -- ./build_image --board=$board --noenable_rootfs_verification --builder_path=$full_build_path test


# STEP 2: add payload extraction piece
echo 'extracting quick payload artifacts'
# need to be inside chromiumos repo to run the below command
# TODO: change the dir inputs to constant structure once `cros_generate_quick_provision_payload` is fixed to take it 
cros_sdk -- cros_generate_quick_provision_payload --image ../build/images/${board}/latest/chromiumos_test_image.bin --output ../build/images/${board}/latest/


# STEP 3: create autotest tarballs
cd ${base_dir}/chromite/api/contrib
echo 'calling gen_call_scripts'
./gen_call_scripts -b $board

echo 'done calling gen_call_scripts'
cd call_scripts
./artifacts__bundle_autotest_files
# move the autotest packages from tmp folder to the right folder
echo 'generated autotest packages and moving them to the `latest` folder'
mv /tmp/autotest_packages.tar ${base_dir}/src/build/images/${board}/latest
mv /tmp/control_files.tar ${base_dir}/src/build/images/${board}/latest
mv /tmp/autotest_server_package.tar.bz2 ${base_dir}/src/build/images/${board}/latest
mv /tmp/test_suites.tar.bz2 ${base_dir}/src/build/images/${board}/latest

echo 'upload all the artifacts to the '$full_build_path' directory'
#TODO: automate the upload
