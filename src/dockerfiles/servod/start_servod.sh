# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x

PORT=9999
BOARD=$1
MODEL=$2
SERIAL=
CONFIG=
CONFIG_FILE_DIR="/var/lib/servod"

    mkdir -p /var/lib/servod

    .  /root/.local/hdctools/chromeos/servod_utils.sh

    log_output \
        "Pre-start PORT=$PORT BOARD=$BOARD MODEL=$MODEL SERIAL=$SERIAL."

    for CMD in iptables ip6tables ; do
      $CMD -A INPUT -p tcp --dport $PORT -j ACCEPT ||
        logger -t "${UPSTART_JOB}" "Failed to configure $CMD."
    done

    CONFIG_FILE=$CONFIG_FILE_DIR/config_$PORT

    log_output \
        "Update config. PORT=$PORT BOARD=$BOARD MODEL=$MODEL SERIAL=$SERIAL."

    # We'll want to update the config file with all the args passed in.
    update_config $CONFIG_FILE BOARD $BOARD
    update_config $CONFIG_FILE MODEL $MODEL
    update_config $CONFIG_FILE SERIAL $SERIAL
    update_config $CONFIG_FILE CONFIG $CONFIG

    # Load all config values, especially the SERIAL, from the latest config file
    # in case of missing from command line.
    . $CONFIG_FILE

    log_output "Store servo hub location and servo micro serial if presents. "\
        "$CONFIG_FILE $SERIAL"
    cache_servov4_hub_and_servo_micro $CONFIG_FILE $SERIAL

    log_output "Pre-start complete."
  LOG="/var/log/servod_$PORT.STARTUP.log"
  SERVO_MICRO_VIDPID=18d1:501a
  SERVO_V4_VIDPID=18d1:501b


  CONFIG_FILE=$CONFIG_FILE_DIR/config_$PORT
    if [ ! -f $CONFIG_FILE ]; then
      log_output "No configuration file ($CONFIG_FILE); terminating"
      exit 0
    fi

    # Config file must have the board and serial (in multi-servo environment)
    # declared like so:
    # BOARD=veyron_minnie
    # SERIAL=1234
    . $CONFIG_FILE
    if [ -z "$BOARD" ]; then
      log_output "No board specified; terminating"
      exit 0
    fi

    MODEL_MSG=""
    MODEL_FLAG=""
    if [ -n "$MODEL" ]; then
      MODEL_FLAG="--model ${MODEL}"
      MODEL_MSG=" model ${MODEL}"
    fi

    SERIAL_FLAG=""
    SERIAL_MSG=""
    if [ -z "$SERIAL" ]; then
      log_output "No serial specified"
    else
      SERIAL_FLAG="--serialname ${SERIAL}"
      SERIAL_MSG="using servo serial $SERIAL"
    fi

    log_output \
      "Launching servod for $BOARD $MODEL_MSG on port $PORT $SERIAL_MSG"
    BOARD_FLAG="--board ${BOARD}"
    PORT_FLAG="--port ${PORT}"

    if [ "$DEBUG" = "1" ]; then
      DEBUG_FLAG="--debug"
    else
      DEBUG_FLAG=""
    fi

    CONFIG_FLAG=""
    if [ ! -z "$CONFIG" ]; then
      CONFIG_FLAG="--config ${CONFIG}"
    fi

    if [ "$DUAL_V4" = "1" ]; then
      DUAL_V4_FLAG="--allow-dual-v4"
    else
      DUAL_V4_FLAG=""
    fi

    if [ -n "$SERIAL" ]; then
      log_output "Restart servo v4 and hub"
      # Slam this device just in case.
      # If the serial number is non-responsive, no problem, we cached the
      # path on startup.
      slam_servov4_hub "${HUB}"

      if [ -n "${SERVO_MICRO_SERIAL}" ]; then
        update_firmware "servo_micro" "${SERVO_MICRO_SERIAL}" \
            "${SERVO_MICRO_VIDPID}"
      fi
      update_firmware "servo_v4" "${SERIAL}" "${SERVO_V4_VIDPID}"
      # We need to wait for the servo to finish booting and
      # export its usb endpoints before calling servod.
      sleep 5
    fi
  /servod --log-dir --host 0.0.0.0 $BOARD_FLAG $MODEL_FLAG $SERIAL_FLAG $PORT_FLAG $DEBUG_FLAG $CONFIG_FLAG $DUAL_V4_FLAG&

  for CMD in iptables ip6tables ; do
    $CMD -D INPUT -p tcp --dport $PORT -j ACCEPT || true
  done

