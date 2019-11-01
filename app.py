import argparse

from aiohttp import web

import pushbot


def runDirectly():
    parser = argparse.ArgumentParser(description="Wechat message pusher")
    parser.add_argument(
        '--host', help='host to listen, default as 127.0.0.1', default='127.0.0.1')
    parser.add_argument(
        '--port', help='port to listen, default as 8080', default=8080)
    args = parser.parse_args()

    app = pushbot.createApp()
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    runDirectly()
