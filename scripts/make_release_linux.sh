#!/bin/bash

# make vue page
cd detail-page
npm run build
mkdir -p ../release
cp -r dist ../release/
cd ..

# make pex
cd server
cp .env.example ../release/.env # copy default env
cp logging.json ../release/logging.json # copy default logging settings
# py36
make build/wechat_push_linux_x86_64-cp-36-cp36m.pex
chmod +x build/wechat_push_linux_x86_64-cp-36-cp36m.pex
cp build/wechat_push_linux_x86_64-cp-36-cp36m.pex ../release/
# py37
make build/wechat_push_linux_x86_64-cp-37-cp37m.pex
chmod +x build/wechat_push_linux_x86_64-cp-37-cp37m.pex
cp build/wechat_push_linux_x86_64-cp-37-cp37m.pex ../release/
cd ..

# make zip
cd release
zip wechat_push_linux_x86_64-cp-36-cp36m.zip -0 -q -r dist wechat_push_linux_x86_64-cp-36-cp36m.pex .env logging.json
zip wechat_push_linux_x86_64-cp-37-cp37m.zip -0 -q -r dist wechat_push_linux_x86_64-cp-37-cp37m.pex .env logging.json

rm *.pex
