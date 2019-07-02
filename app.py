#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 网站服务的主文件

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado.options import define, options
from search import search

define('port', default=8020, help='run port', type=int)


class MainHandler(RequestHandler):
    def get(self):
        self.render('index.html')


class SearchHandler(RequestHandler):
    def post(self):
        res = search(self.get_body_argument('ocr'));
        self.write(res)


def make_app():
    settings = dict(
        template_path='views',
        static_path='views',
        compiled_template_cache=False
    )
    return Application([
        ('/', MainHandler),
        ('/search', SearchHandler),
    ], **settings)


if __name__ == "__main__":
    options.parse_command_line()
    app = make_app()
    print('Start the app on http://localhost:%d' % (options.port,))
    app.listen(options.port)
    IOLoop.current().start()
