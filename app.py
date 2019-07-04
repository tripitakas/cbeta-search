#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 网站服务的主文件

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado.options import define, options
from search import build_db
import docker
import os
import signal

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

docker_client = docker.from_env()


def stop_es_container():
    for container in docker_client.containers.list():
        container.stop()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, stop_es_container)
    # First, start elasticsearch container
    docker_client.containers.run('chaopli/es-ik-tripitakas', detach=True)
    print('Building elasticsearch index from ocr files')
    build_db()

    # Then start tornado IO loop
    options.parse_command_line()
    app = make_app()
    print('Start the app on http://localhost:%d' % (options.port,))
    app.listen(options.port)
    IOLoop.current().start()
