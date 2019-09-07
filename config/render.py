#!/usr/bin/env python

'''
Render out some of the templates etc we want to use for a Django/Nginx deployment
'''

from jinja2 import Environment, PackageLoader, select_autoescape
import dotenv
from pathlib import Path
import os

dotenv.load_dotenv()

env = Environment(
    loader=PackageLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

global_settings = dict(os.environ)

# Set the django port and host, or just the django socket
try:
    assert ('django_port' in global_settings and 'django_host' in global_settings) or 'django_sock' in global_settings
except:
    print(dict(os.environ).keys())
    raise
uwsgi_settings = dict()
nginx_settings = dict(
    media_path = (Path('.') / 'media').absolute(),
    static_path = (Path('.') / 'static').absolute(),
    uwsgi_params_path = '/etc/nginx/uwsgi_params',
    
)

uwsgi_settings.update(**global_settings)
nginx_settings.update(**global_settings)

env.get_template('nginx.conf').stream(nginx_settings).dump('rendered/nginx.conf')
env.get_template('http-server.ini').stream(uwsgi_settings).dump('../http-server.ini')
