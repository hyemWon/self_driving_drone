#!/bin/bash

cd ~/jetconda3/envs/py38/lib/python3.8/site-packages/mavsdk/bin
echo '1234' | sudo -S ./mavsdk_server -p 50051 serial:///dev/ttyASM0:57600
