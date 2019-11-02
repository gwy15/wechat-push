#!/bin/bash

# make vue page
cd detail-page
rm -rf dist
npm run build
mkdir -p ../release
cp -r dist ../release/dist
cd ..

# make pex
cd server
make
cp build/*.pex ../release/
cd ..

# make zip
cd release
zip release_py36.zip -0 -q -r dist wechat_py36.pex
zip release_py37.zip -0 -q -r dist wechat_py37.pex
rm *.pex
rm -rf dist
