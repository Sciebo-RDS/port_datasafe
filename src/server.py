#!/usr/bin/env python

from __init__ import app, register_service
import os

from RDS import Util, LoginService, FileTransferMode, FileTransferArchive
service = LoginService(
    servicename="port-datasafe",
    implements=["metadata"],
    fileTransferMode=FileTransferMode.passive,
    fileTransferArchive=FileTransferArchive.none,
    userId=False,
    password=False,
    description={"en": "datasafe is a service of WWU Münster for archiving research data. With the help of datasafe, you can enrich your research data with descriptive metadata and archive the resulting dataset for ten years on WWU servers.",
                 "de": "datasafe ist ein Service der WWU Münster zum Archivieren von Forschungsdaten. Mit Hilfe von datasafe können Sie ihre Forschungsdaten mit beschreibenden Metadaten anreichern und den resultierenden Datensatz für zehn Jahre auf Servern der WWU archivieren."},
    infoUrl="https://datasafe-dev.uni-muenster.de/",
    helpUrl="https://datasafe-dev.uni-muenster.de/datasafe/frequently_asked_questions",
    icon="./datasafe.svg",
    displayName="Datasafe",
)
Util.register_service(service)

# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
app.run(port=8080, server="gevent")
