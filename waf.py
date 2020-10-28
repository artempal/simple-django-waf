import os
import signal
import ssl

import django
from tornado import web, ioloop
import requests
from tornado.httpserver import HTTPServer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waf.settings')
django.setup()

from analysis import Analysis
from main.models import Configs
from main.models import Proxy
from asgiref.sync import sync_to_async

ignore_headers = ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection', 'Pragma', 'Referer')
configs = Configs.objects.get(pk=1)
analysis = Analysis()


def handler_sigterm(signum, frame):
    try:
        Proxy.objects.filter(hostname=os.environ.get("PROXY_HOST")).delete()
    except Exception:
        pass


signal.signal(signal.SIGTERM, handler_sigterm)


class MainHandler(web.RequestHandler):
    SUPPORTED_METHODS = ('GET', 'HEAD', 'POST')

    async def get(self):
        print('GET')
        await self._go('GET')

    head = get

    async def post(self):
        if self.request.path == '/restart' and 'key' in self.request.arguments and \
                self.request.arguments['key'][0].decode('utf-8') == os.environ.get("SECRET_KEY"):
            exit(1)
        print('POST')
        await self._go('POST')

    async def _go(self, type):
        async_function = sync_to_async(analysis.process)
        if configs.signature_analysis:  # если запрос должен быть заблокирован
            result = await async_function(self.request)
            if result:
                self.set_status(403)  # ставим код ошибки
                return  # выходим

        if type == 'POST':
            url = 'http://{}{}'.format(configs.hostname, self.request.path)
        else:
            url = 'http://{}{}?{}'.format(configs.hostname, self.request.path, self.request.query)
        print(url)
        m_headers = parse_headers(self.request.headers)
        try:
            if type == 'POST':
                response = requests.post(url, headers=m_headers, data=self.request.body, verify=False,
                                         allow_redirects=False)
            else:
                response = requests.get(url, headers=m_headers, verify=False, allow_redirects=False)
        except Exception:
            print('Проблема соединения с сайтом ' + url)
            self.set_status(500)
            return
        print(response.status_code)
        self.set_status(response.status_code)
        r_headers = response.headers
        # print(r_headers)
        cookies = requests.utils.dict_from_cookiejar(response.cookies)
        # print(response.raw.headers.getlist('Set-Cookie'))

        for header in r_headers:
            # print(header + " "+ r_headers[header])
            if header not in ignore_headers:
                self.set_header(header, r_headers[header])
        if configs.hide_server:
            self.set_header("Server", "Protected")
        if configs.hide_x_powered_by:
            self.set_header("X-Powered-By", "Protected")
        if configs.x_frame_option:
            self.set_header("X-FRAME-OPTIONS", "DENY")
        if configs.xss_browser_protection:
            self.set_header("X-XSS-Protection", "1; mode=block")
        if configs.no_sniff:
            self.set_header("X-Content-Type-Options", "nosniff")
        if configs.content_security_policy_self:
            self.set_header("Content-Security-Policy", "default-src 'self';")
        if configs.https and configs.strict_transport_security:
            self.set_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        for cookie in cookies:
            self.set_cookie(cookie, cookies[cookie])
        self.write(response.content)
        await self.finish()


def parse_headers(headers):
    req_header = {}
    for (k, v) in sorted(headers.get_all()):
        if k not in ignore_headers:
            # print('%s: %s' % (k, v))
            req_header[k] = v
    return req_header


def make_app():
    return web.Application([
        (r".*", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    if configs.https:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(configs.cert_file, configs.key_file)
        server = HTTPServer(app, ssl_options=ssl_ctx)
        server.listen(configs.port)
    else:
        app.listen(configs.port)
    try:
        Proxy.objects.update_or_create(
            hostname=os.environ.get("PROXY_HOST"),
            port=os.environ.get("PROXY_PORT"),
        )
    except Exception:
        exit(1)
    try:
        ioloop.IOLoop.current().start()
    except Exception:
        exit(1)
