#!/usr/bin/env bash

#ino serial -p /dev/loadmega -b 115200 -- --echo
picocom /dev/mega -b 115200 --echo
