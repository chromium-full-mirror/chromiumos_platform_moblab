// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <stdio.h>
#include <usb.h>

void reset_usb_devs_on_bus(struct usb_bus *p_usb_bus) {
    if (p_usb_bus == NULL) {
        return;
    }
    struct usb_dev *p_usb_dev;
    for (p_usb_dev = p_usb_bus->devices;
         p_usb_dev;
         p_usb_dev = p_usb_dev->next) {
        char buf[1024];
        int ret;
        usb_dev_handle *usb_handler = usb_open(p_usb_dev);
        if (usb_handler) {
            int buf_len = usb_get_string_simple(usb_handler, 2, buf, 1023);
            ret = usb_reset(usb_handler);
            if (buf_len > 0) {
                printf("resetting %p %d (%s)\n", p_usb_dev, ret, buf);
            }
            usb_close(usb_handler);
        } else {
            printf("Can't open %p\n", p_usb_dev);
        }
    }
}

struct usb_bus *get_usb_busses() {
    /*refer libusb_dev*/
    usb_init();
    usb_find_busses();
    usb_find_devices();
    return usb_get_busses();
}

int main(void)
{
    struct usb_bus *p_usb_buses = get_usb_busses();
    if (p_usb_buses) {
        struct usb_bus *p_usb_bus = p_usb_buses;
        for (; p_usb_bus; p_usb_bus = p_usb_bus->next) {
            reset_usb_devices_on_bus(p_usb_bus);
        }
    }
    return 0;
}

