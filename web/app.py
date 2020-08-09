#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 网站服务的主文件

import docker
import signal
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado.options import define, options
from search import build_db, BM_PATH, TXT_PATH


define('port', default=8020, help='run port', type=int)
define('docker_indexer', default=False, 
       help='Whether start Elasticsearch in docker container')
define('run_kibana', default=False,
       help='Whether start kibana in a docker container')
define('BM_PATH', default=BM_PATH)


class MainHandler(RequestHandler):
    def get(self):
        self.render('index.html')


class SearchHandler(RequestHandler):
    def post(self):
        res = self.get_body_argument('ocr')
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
running_containers = []


def stop_es_container():
    for container in docker_client.containers.list():
        container.stop()


if __name__ == "__main__":
    options.parse_command_line()
    BM_PATH = options.BM_PATH
    # If running indexer in docker, otherwise assuming ES already started locally
    if options.docker_indexer:
        signal.signal(signal.SIGTERM, stop_es_container)
        # First try building the es-ik-tripitakas docker image
        print('Try building es-ik-tripitakas image')
        (image, obj) = docker_client.images.build(path='./es-ik')
        # Second, start elasticsearch container
        print('Try running es-ik-tripitakas image')
        running_containers.append(docker_client.containers.run(
            image, environment=['discovery.type=single-node'],
            ports={'9300/tcp': 9300, '9200/tcp': 9200},
            detach=True))
    if options.run_kibana:
        print('starting kibana docker container')
        running_containers.append(docker_client.containers.run(
            'docker.elastic.co/kibana/kibana:7.2.0', ports={'5601/tcp': 5601}, 
            detach=True))
    print('Building elasticsearch index from ocr files')
    build_db()

    # Then start tornado IO loop
    app = make_app()
    print('Start the app on http://localhost:%d' % (options.port,))
    app.listen(options.port)
    IOLoop.current().start()
