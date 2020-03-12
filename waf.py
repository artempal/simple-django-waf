import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waf.settings')
django.setup()
from tornado import web, ioloop
import requests
from analysis import Analysis
from setting import Setting


class MainHandler(web.RequestHandler):
    SUPPORTED_METHODS = ('GET', 'HEAD', 'POST')
    analysis = Analysis()

    def get(self):
        print('GET')
        self._go('GET')

    head = get

    def post(self):
        print('POST')
        self._go('POST')

    def _go(self, type):

        if self.analysis.process(self.request):  # если запрос должен быть заблокирован
            self.set_status(403)  # ставим код ошибки
            return  # выходим

        if type == 'POST':
            url = 'http://{}{}'.format(Setting.hostname, self.request.path)
        else:
            url = 'http://{}{}?{}'.format(Setting.hostname, self.request.path, self.request.query)
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
            if header not in Setting.ignore_headers:
                self.set_header(header, r_headers[header])
        for cookie in cookies:
            self.set_cookie(cookie, cookies[cookie])
        self.write(response.content)
        self.finish()


def parse_headers(headers):
    req_header = {}
    for (k, v) in sorted(headers.get_all()):
        if k not in Setting.ignore_headers:
            # print('%s: %s' % (k, v))
            req_header[k] = v
    return req_header


def make_app():
    return web.Application([
        (r".*", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(Setting.port)
    try:
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print('OK!')
