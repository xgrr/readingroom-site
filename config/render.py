#!/usr/bin/env python

'''
Render out some of the templates etc we want to use for a Django/Nginx deployment
'''

from jinja2 import Environment, PackageLoader, select_autoescape
import dotenv
from pathlib import Path

dotenv.load_dotenv()

env = Environment(
    loader=PackageLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

nginx_settings = dict(
    django_port=8001,
    nginx_port=8000,
    media_path = (Path('.') / 'media').absolute(),
    static_path = (Path('.') / 'static').absolute(),
    uwsgi_params_path = '/etc/nginx/uwsgi_params',
    server_name='localhost',
)

template = env.get_template('nginx.conf')
string = template.render(nginx_settings)

print(string)