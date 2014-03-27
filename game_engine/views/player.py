from pyramid.view import view_config
from game_engine.model import DBSession, Player
from pyramid.httpexceptions import HTTPFound, HTTPClientError
import transaction

@view_config(renderer="game_engine:templates/players.html", route_name="players", http_cache=0)
def player_list(request):

  players = DBSession.query(Player).order_by(Player.wins).all()
  return dict(
    players=players)


@view_config(renderer="game_engine:templates/new_player.html", route_name="new_player", http_cache=0)
def new_player(request):

  if request.method == 'POST':
    if 'submit' in request.POST:
      name = request.POST.get('playerName')
      url = request.POST.get('playerUrl')

      if not name or not url:
        return dict(error='Please fill out all fields.')


      new_player = Player(name, url)
      with transaction.manager:
        DBSession.add(new_player)

      raise HTTPFound(request.route_path('index'))
  return dict()