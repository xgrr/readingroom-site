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

def paths():
    base_path = Path('.') / '..'
    env_path = base_path / 'env'
    return {
        'base': base_path.absolute(),
        'env': env_path.absolute()
        'media': (base_path / 'media').absolute(),
        'static':  (base_path / 'static').absolute(),
        'uwsgi': (env_path / 'bin' / 'uwsgi').absolute
    }

global_settings = dict(os.environ)
global_settings['paths'] = paths()
print (global_settings['paths'])
# Set the django port and host, or just the django socket
try:
    assert ('django_serve_port' in global_settings and 'django_server' in global_settings) or 'django_sock' in global_settings
except:
    print(dict(os.environ).keys())
    raise
uwsgi_settings = dict()
nginx_settings = dict(
    media_path = (Path('.') / '..' / 'media').absolute(),
    static_path = (Path('.') / '..' / 'static').absolute(),
    uwsgi_params_path = '/etc/nginx/uwsgi_params',
)

PATH_TO_UWSGI = (Path('.') / '..' / 'env' /'bin' /'uwsgi').absolute()

uwsgi_settings.update(**global_settings)
nginx_settings.update(**global_settings)

env.get_template('nginx.conf').stream(nginx_settings).dump('rendered/nginx.conf')
env.get_template('http-server.ini').stream(uwsgi_settings).dump('../http-server.ini')
