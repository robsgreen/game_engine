from pyramid.view import view_config
from game_engine.model import DBSession, Player, Match

@view_config(renderer="game_engine:templates/index.html", route_name="index", http_cache=0)
def index(request):

  players = DBSession.query(Player).order_by(Player.wins).all()
  matches = DBSession.query(Match).order_by(Match.date_created.desc())[0:5]
  return dict(
    players=players,
    matches=matches)
