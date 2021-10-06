#!/bin/bash
mkdir bootloader && \
ls -1t hekate_patches/*.ini | while read fn ; do cat "$fn" >> bootloader/patches.ini; done && \
zip -r patches.zip ./atmosphere ./bootloader && \
rm -rf bootloader