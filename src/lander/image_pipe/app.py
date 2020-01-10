import base64
import os
import tempfile
from io import BytesIO

import magic
import requests
from PIL import Image
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
                    'CACHE_DIR': os.path.join(tempfile.gettempdir(), 'i-p')}
    cache = Cache(with_jinja2_ext=False, config=cache_config)
    cache.init_app(app)

    @app.route('/i-p-s')
    def index():
        return 'HELLO'

    @app.route('/i-p/<code>')
    @app.route('/i-p/<code>/<size>')
    def serve(code, size=None):

        cache_key = code

        if size is not None:
            try:
                width, height = [int(x) for x in size.split('x')]
                assert 20 <= width <= 1000
                assert 20 <= height <= 1000
                cache_key = '{}/{}/{}'.format(cache_key, width, height)
            except BaseException:
                abort(406)

        rv = cache.get(cache_key)

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

            if size:
                im_io = BytesIO()
                im = Image.open(BytesIO(rv))
                im.thumbnail((width, height))
                im.save(im_io, 'JPEG', quality=96)
                im_io.seek(0)
                rv = im_io.read()

            cache.set(cache_key, rv)

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
