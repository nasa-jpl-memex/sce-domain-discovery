import os
from pyArango.connection import *
from pyArango.theExceptions import DocumentNotFoundError
from flask import current_app as app


db = None
models = None
aurl = os.getenv('ARANGO_URL', 'https://single-server-int:8529')
conn = Connection(aurl, 'root', '',verify=False)
if not conn.hasDatabase("sce"):
    db = conn.createDatabase("sce")
else:
    db = conn["sce"]

if not db.hasCollection('models'):
    models = db.createCollection('Collection', name='models')
else:
    models = db.collections['models']

def set_sparkler_defaults(model):
    set_sparkler_options(model, {})

def set_sparkler_options(model, content):

    topn = 1000
    topgrp = 256
    sortby = "discover_depth asc, score asc"
    groupby = "group"
    serverdelay = 1000
    fetchheaders = '''User-Agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Sparkler/${project.version}"
          Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
          Accept-Language: "en-US,en"'''
    activeplugins = ["urlfilter-regex", "urlfilter-samehost"]
    plugins = {"urlfilter.regex": {"urlfilter.regex.file": "regex-urlfilter.txt"}, "fetcher.jbrowser":{"socket.timeout": 3000, "connect.timeout": 3000}}

    if "topn" in content:
        topn = content.topn
    if "topgrp" in content:
        topgrp = content.topgrp
    if "sortby" in content:
        sortby = content.sortby
    if "groupby" in content:
        groupby = content.groupby
    if "serverdelay" in content:
        serverdelay = content.serverdelay
    if "fetchheaders" in content:
        fetchheaders = content.fetchheaders
    if "activeplugins" in content:
        activeplugins = content.activeplugins
    if "plugins" in content:
        plugins = content.plugins
    content = {"crawldb.uri":"http://localhost:8983/solr/crawldb",
               "spark.master": "local[*]",
               "kafka.enable": "false",
               "kafka.listeners":"localhost:9092",
               "kafka.topic": "sparkler_%s",
               "generate.topn": topn,
               "generate.top.groups": topgrp,
               "generate.sortby": sortby,
               "generate.groupby": groupby,
               "fetcher.server.delay": serverdelay,
               "fetcher.headers": fetchheaders,
               "plugins.active": activeplugins,
               "plugins": plugins}
    try:
        m = models[model]
        m['sparkler_opts'] = content
        m.save()
    except DocumentNotFoundError as error:
        app.logger.info(error)
        raise

def get_sparkler_options(model):

    try:
        m = models[model]
        return m['sparkler_opts']
    except DocumentNotFoundError as error:
        app.logger.info(error)
        raise
