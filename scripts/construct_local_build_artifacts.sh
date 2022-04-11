#!/bin/bash

# READ BELOW NOTES AND ASSUMPTIONS BEFORE YOU USE:

# NOTE 1: This script requires board as a parameter

# NOTE 2: This script is a general guidance for
# the user on the steps to be followed 
# and might have to be tweaked as per user settings. 
# It does not gaurantee a robust way of generating artifacts
# User is expected to have a fair understanding of
# https://chromium.googlesource.com/chromiumos/docs/+/HEAD/developer_guide.md

# Assumption 1: your chromiumos repo exists at $HOME/chromiumos. 
# If not, change the below variable base_dir

base_dir="$HOME/chromiumos"
if [ "$1" = "" ]; then
	echo 'please pass in board as first parameter'
	exit
fi

board=$1
echo 'board is set as '$board


# STEP 1: build the image after building the packages
# eval is needed below because of command substitution and "~" usage in base_dir
cd ${base_dir}/src/third_party/chromiumos-overlay/chromeos/config

milestone_string=$(./chromeos_version.sh |grep "^[[:space:]]*CHROME_BRANCH=" |cut -d= -f2)
version_string=$(./chromeos_version.sh |grep "^[[:space:]]*CHROMEOS_VERSION_STRING=" |cut -d= -f2)

cd ${base_dir}
# keep the build path as $board-local (adding extra words will cause issues)
full_build_path="${board}-local/R${milestone_string}-${version_string}"
echo 'full build path: '${full_build_path}

cros_sdk -- ./build_image --board="${board}" --noenable_rootfs_verification --builder_path="${full_build_path}" --version="${version_string}" test

# STEP 2: add payload extraction piece
echo 'extracting quick payload artifacts'
echo ''
echo 'Attention: It might happen that next step asks for a password to enter sudo mode'
echo 'and in the process of doing so can get stuck in the background'
echo 'If you see that the process is stopped, use `fg` command in the same terminal'
echo 'to get the process to the foreground and then you would be able to see pwd prompt'
# need to be inside chromiumos repo to run the below command
# TODO: change the dir inputs to constant structure once `cros_generate_quick_provision_payload` is fixed to take it
cros_sdk -- cros_generate_quick_provision_payload --image ../build/images/${board}/latest/chromiumos_test_image.bin --output ../build/images/${board}/latest/
echo 'done extracting quick payload artifacts'

# STEP 3: create autotest and tast tarballs
cd ${base_dir}/chromite/api/contrib
echo 'calling gen_call_scripts'
./gen_call_scripts -b ${board}
echo 'done calling gen_call_scripts'

cd call_scripts
# generate and move the autotest packages from tmp folder to the right folder
echo 'generating autotest packages'
./artifacts__bundle_autotest_files
echo 'moving autotest packages to the `latest` folder'
mv /tmp/autotest_packages.tar ${base_dir}/src/build/images/${board}/latest
mv /tmp/control_files.tar ${base_dir}/src/build/images/${board}/latest
mv /tmp/autotest_server_package.tar.bz2 ${base_dir}/src/build/images/${board}/latest
mv /tmp/test_suites.tar.bz2 ${base_dir}/src/build/images/${board}/latest

# generate and move the tast bundles from tmp folder to the right folder
echo 'generating tast bundles'
./artifacts__bundle_tast_files
echo 'moving tast bundles to the `latest` folder'
mv /tmp/tast_bundles.tar.bz2 ${base_dir}/src/build/images/${board}/latest
echo 'upload all the artifacts to the '${full_build_path}' directory'
#TODO: automate the upload
