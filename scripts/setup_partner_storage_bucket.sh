#!/bin/bash
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

if [ "$#" -ne 1 ]; then
  echo 'Usage: ./setup_storage_bucket <PARTNER>'
  echo '  PARTNER: chromeos-moblab-<PARTNER>'
  exit 1
fi

PARTNER_BUCKET='gs://chromeos-moblab-'$1
GSUTIL='gsutil'
PARTNER_EMAIL='cros.moblab.'$(echo $1 | sed 's/-/./')'@gmail.com'

set -x

${GSUTIL} mkdir -p chromeos-partner-moblab ${PARTNER_BUCKET}
${GSUTIL} acl ch -u ${PARTNER_EMAIL}:WRITE ${PARTNER_BUCKET}
${GSUTIL} defacl ch -u ${PARTNER_EMAIL}:READ ${PARTNER_BUCKET}
${GSUTIL} -m acl ch -R -u ${PARTNER_EMAIL}:READ ${PARTNER_BUCKET}
${GSUTIL} acl ch -g \
    00b4903a97fb6344be6306829e053825e18a04ab0cc5513e9585a2b8c9634c80:FULL_CONTROL \
    -g 00b4903a97ce95daf4ef249a9c21dddd83fdfb7126720b7c3440483b6229a03c:FULL_CONTROL \
    ${PARTNER_BUCKET}
${GSUTIL} defacl ch -g \
    00b4903a97fb6344be6306829e053825e18a04ab0cc5513e9585a2b8c9634c80:FULL_CONTROL \
    -g 00b4903a97ce95daf4ef249a9c21dddd83fdfb7126720b7c3440483b6229a03c:FULL_CONTROL \
    ${PARTNER_BUCKET}
${GSUTIL} acl ch -g google.com:READ  ${PARTNER_BUCKET}
${GSUTIL} defacl ch -g google.com:READ ${PARTNER_BUCKET}
