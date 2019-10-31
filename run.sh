#! /bin/bash
source ./venv/bin/activate
gunicorn app:asyncApp --worker-class aiohttp.GunicornWebWorker --bind unix:///tmp/wechat-push.sock

