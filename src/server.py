#!/usr/bin/env python

from __init__ import app, register_service
import os

from RDS import Util, LoginService, FileTransferMode, FileTransferArchive
service = LoginService(
    servicename="Datasafe",
    implements=["metadata"],
    fileTransferMode=FileTransferMode.passive,
    fileTransferArchive=FileTransferArchive.none,
    userId=False,
    password=False
)
Util.register_service(service)

# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
app.run(port=8080, server="gevent")
