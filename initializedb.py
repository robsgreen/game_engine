import os
import sys

from sqlalchemy import engine_from_config

from game_engine.model import *
from ConfigParser import SafeConfigParser
  

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    cp = SafeConfigParser()    
    if not cp.read(config_uri):
      print "Cannot read %s" % config_uri
      sys.exit(1)

    settings = dict(cp.items("app:main"))
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()