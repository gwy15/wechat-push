#! /bin/bash
source ./venv/bin/activate
gunicorn pushbot:asyncApp --worker-class aiohttp.GunicornWebWorker --bind unix:///tmp/wechat-push.sock

