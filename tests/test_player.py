import unittest
import transaction

from pyramid import testing


def _initTestingDB():
  from sqlalchemy import create_engine
  from tutorial.models import *

  engine = create_engine('sqlite://')
  Base.metadata.create_all(engine)
  DBSession.configure(bind=engine)
  with transaction.manager:
    rob = Player('Rob Green', 'http://robs-server.com:3001')
    pfb = Player('Pierre-Francoys Brousseau', 'http://pfb-server.com:3001')
    DBSession.add(rob)
    DBSession.add(pfb)
  return DBSession


class PlayerViewTests(unittest.TestCase):
  def setUp(self):
    self.session = _initTestingDB()
    self.config = testing.setUp()

  def tearDown(self):
    self.session.remove()
    testing.tearDown()

  def test_wiki_view(self):
    from views import player

    request = testing.DummyRequest()
    inst = WikiViews(request)
    response = inst.wiki_view()
    self.assertEqual(response['title'], 'Welcome to the Wiki')


class PlayerFunctionalTests(unittest.TestCase):
  def setUp(self):
    self.session = _initTestingDB()
    self.config = testing.setUp()
    from pyramid.paster import get_app
    app = get_app('development.ini')
    from webtest import TestApp
    self.testapp = TestApp(app)

  def tearDown(self):
    self.session.remove()
    testing.tearDown()

  def test_it(self):
    res = self.testapp.get('/', status=200)
    self.assertIn(b'Welcome', res.body)
    res = self.testapp.get('/add', status=200)
    self.assertIn(b'Log', res.body)