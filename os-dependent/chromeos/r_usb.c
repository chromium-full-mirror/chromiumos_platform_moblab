// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <err.h>
#include <libusb.h>
#include <stdint.h>
#include <stdio.h>

int main(int argc, const char *argv[]) {
  libusb_device **devs;
  int ret;
  ssize_t cnt;

  if (argc > 1) {
    printf("Reset all USB devices.\n\nUsage: %s\n", argv[0]);
    return 1;
  }

  ret = libusb_init(NULL);
  if (ret < 0)
    errx(1, "libusb_init failed");

  cnt = libusb_get_device_list(NULL, &devs);
  if (cnt < 0)
    errx(1, "libusb_get_device_list failed");

  for (ssize_t i = 0; i < cnt; ++i) {
    libusb_device *dev = devs[i];
    libusb_device_handle *handle;
    int buflen;
    unsigned char buf[1024];

    ret = libusb_open(dev, &handle);
    if (ret < 0) {
      warnx("opening %p failed", dev);
      continue;
    }

    buflen =
        libusb_get_string_descriptor_ascii(handle, 2, buf, sizeof(buf) - 1);
    ret = libusb_reset_device(handle);
    if (buflen)
      printf("resetting %p %d (%s)\n", dev, ret, buf);

    libusb_close(handle);
  }

  libusb_free_device_list(devs, 1);
  libusb_exit(NULL);
  return 0;
}
