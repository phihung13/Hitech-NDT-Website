#!/usr/bin/env python3
import os
import sys

# Add your project directory to the sys.path
sys.path.insert(0, os.path.dirname(__file__))

from site_hitech.wsgi import application

# This is the WSGI application
def app(environ, start_response):
    return application(environ, start_response)