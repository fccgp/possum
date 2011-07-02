#!/bin/bash
Xephyr -ac -screen 1024x768 -br -reset -terminate :3 2>/dev/null &
sleep 1
pushd /home/pos/possum > /dev/null
DISPLAY=:3 python gui/efl.py &
popd > /dev/null
echo
echo "[press enter to stop Possum GUI]"
echo
read
pkill Xephyr
