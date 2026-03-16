# """
# WSGI config for chowbuddies project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
# """

import os

from django.core.wsgi import get_wsgi_application
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chowbuddies.settings')

application = get_wsgi_application()



# def application(environ, start_response):
#     status = '200 OK'
#     output = []
#     output.append(f"Python executable: {sys.executable}\n")
#     output.append(f"sys.path:\n" + "\n".join(sys.path) + "\n")
#     output.append("site-packages should be somewhere above\n")

#     response_headers = [('Content-type', 'text/plain'),
#                         ('Content-Length', str(len(''.join(output))))]
#     start_response(status, response_headers)
#     return [line.encode('utf-8') for line in output]