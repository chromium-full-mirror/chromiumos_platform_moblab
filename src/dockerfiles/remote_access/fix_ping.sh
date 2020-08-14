# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

test_and_fix_ping() {
    docker exec $1 ping -c 1 localhost
    if [ $? -ne 0 ]; then
        echo "Fixing the ping capabilities."
        docker exec -u root $1 apt install -y libcap2-bin
        docker exec -u root $1 setcap cap_net_raw+ep /bin/ping
    fi
    echo "Fix ping check complete."
}

while true
do
    test_and_fix_ping default_autotest-monitordb_1
    test_and_fix_ping default_autotest_1
    sleep 120
done
