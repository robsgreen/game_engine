from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.httpexceptions import HTTPClientError
import json
import datetime
import logging
from sqlalchemy import engine_from_config

from game_engine.model import *

from pyramid.events import NewRequest
from pyramid.events import subscriber

@subscriber(NewRequest)
def close_dbsession(event):
  '''
    Close the current session to ensure each request has a fresh session
  '''  
  DBSession.remove()


def make_pyramid_app(settings):

  engine = engine_from_config(settings, 'sqlalchemy.')
  DBSession.configure(bind=engine)
  Base.metadata.bind = engine
  config = Configurator(settings=settings)

  # Add genshi.  Use .html instead of .genshi for template extension
  import pyramid_genshi
  config.add_renderer('.html', pyramid_genshi.renderer_factory)

  config.add_route('index', '/')

  config.add_route('players', '/players')
  config.add_route('new_player', '/players/new')
  config.add_route('new_match', '/matches/new')
  config.add_route('match_view', '/matches/{match_id}')


  
  # Take into account all the @view_config decorators
  config.scan('game_engine')

  config.add_static_view(name='/static', path='game_engine:static/', cache_max_age=datetime.timedelta(days=365))

  app = config.make_wsgi_app()


  return app



if __name__ == '__main__':
  import sys
  import argparse
  from ConfigParser import SafeConfigParser
  
  cp = SafeConfigParser()
  
  parser = argparse.ArgumentParser(description='Game engine server.')
  
  parser.add_argument('-p', '--port', type=int, help='server port')
  parser.add_argument('-c', '--config', help='config file location')

  args = parser.parse_args()

  settings = {}
  
  if args.config:
    if not cp.read(args.config):
      print "Cannot read %s" % args.config
      sys.exit(1)

    settings = dict(cp.items("server:main"))

  if not args.port:
    port = int(settings.get('port', 8080))
  else:
    port = args.port

  host = settings.get('host', '0.0.0.0')
  
  app = make_pyramid_app(settings)
  server = make_server(host, port, app)
  app = make_pyramid_app(settings)
  print 'Running Game Engine server running on %s:%s' % (host, port)
  server.serve_forever()
