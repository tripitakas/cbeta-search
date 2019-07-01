#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 利用ES的全文检索技术，从CBETA全文检索库中检索与OCR文本相似的文本

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchException


def search(text):
    return '''相往來。白如是。　大姊僧聽！此某甲，某甲比丘
尼清淨，而以無根波羅夷法謗；今僧為作覆'''  # TODO: 根据text查找相似文本
