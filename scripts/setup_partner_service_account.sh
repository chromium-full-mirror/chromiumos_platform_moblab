#!/bin/bash
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

if [ "$#" -ne 1 ]; then
  echo 'Usage: ./setup_service_account <PARTNER>'
  echo '  PARTNER: chromeos-moblab-<PARTNER>'
  exit 1
fi

PARTNER='chromeos-moblab-'$1

set -x
set -e

gcloud config set project chromeos-partner-moblab
gcloud iam service-accounts create $PARTNER --display-name "$PARTNER"
gcloud iam service-accounts keys create \
    ~/$PARTNER-key.json \
    --iam-account $PARTNER@chromeos-partner-moblab.iam.gserviceaccount.com
gsutil cp ~/$PARTNER-key.json gs://$PARTNER/pubsub-key-do-not-delete.json
gcloud beta pubsub topics add-iam-policy-binding moblab-notification --member \
    serviceAccount:$PARTNER@chromeos-partner-moblab.iam.gserviceaccount.com \
    --role roles/pubsub.publisher
