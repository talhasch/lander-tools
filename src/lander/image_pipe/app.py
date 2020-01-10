import base64
import os
import tempfile

import magic
import requests
from flask import Flask, make_response, abort
from flask_caching import Cache
from werkzeug.middleware.proxy_fix import ProxyFix

app = None
cache = None


def __flask_setup():
    global app, cache

    app = Flask(__name__, static_folder=None)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    cache_config = {'CACHE_TYPE': 'filesystem',
                    'CACHE_THRESHOLD': 10000,
                    'CACHE_DEFAULT_TIMEOUT': 86400,
                    'CACHE_DIR': os.path.join(tempfile.gettempdir(), 'image_pipe')}
    cache = Cache(with_jinja2_ext=False, config=cache_config)
    cache.init_app(app)

    @app.route('/i-p-s')
    def index():
        return 'HELLO'

    @app.route('/i-p/<code>')
    def serve(code):

        rv = cache.get(code)

        try:
            url = base64.b64decode(code).decode('utf-8')
        except BaseException:
            abort(404)
            return

        if not url.startswith('https://gaia.blockstack.org/hub/'):
            abort(404)
            return

        if rv is None:
            resp = requests.get(url)
            rv = resp.content
            cache.set(code, rv)

        response = make_response(rv)
        response.set_etag(code)

        mime_type = magic.from_buffer(rv, mime=True)

        response.headers.set('Content-Type', mime_type)
        response.headers.set("can't-be-evil", 'true')

        return response


def __run_dev_server():
    global app

    app.config['DEVELOPMENT'] = True
    app.config['DEBUG'] = True

    app.run(host='127.0.0.1', port=8088)


__flask_setup()


def main():
    __run_dev_server()
