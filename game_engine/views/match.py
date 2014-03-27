from pyramid.view import view_config
from pyramid.response import Response
import time
from pyramid.httpexceptions import HTTPFound, HTTPClientError
import transaction
import json
from game_engine.model import DBSession, Player, Match, GameBoard, UP, DOWN, LEFT, RIGHT
import threading
import Queue
import logging

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

logger = logging.getLogger('game_engine')


logger.addHandler(console_handler)

queue = Queue.Queue(0)

directions = {'up': UP,
              'down': DOWN,
              'left': LEFT,
              'right': RIGHT}

import requests


@view_config(renderer="game_engine:templates/match_view.html", route_name="match_view", http_cache=0)
def match_view(request):
  match_id = request.matchdict['match_id']
  match = DBSession.query(Match).get(match_id)
  return dict(match=match)


@view_config(renderer="game_engine:templates/new_match.html", route_name="new_match", http_cache=0)
def new_match(request):
  board_size = int(request.registry.settings.get('board_size', 20))

  if request.POST:
    player_1 = int(request.POST['player_1'])
    player_2 = int(request.POST['player_2'])
    match = MatchWorker(queue, player_1, player_2, [board_size, board_size], 21)
    match.start()

    raise HTTPFound(request.route_path('match_view', match_id=match.match_id))

  else:
    players = DBSession.query(Player).all()
    return dict(players=players)


class MatchWorker(threading.Thread):

  def __init__(self, queue, player1_id, player2_id, board_size, num_stars):
    self.player1_id = player1_id
    self.player2_id = player2_id
    self.board_size = board_size
    self.num_stars = num_stars

    self.__queue = queue
    threading.Thread.__init__(self)

    # Create the match in the databse
    match = Match(self.player1_id, self.player2_id, self.board_size, self.num_stars)
    with transaction.manager:
      DBSession.add(match)
      DBSession.flush()
      self.match_id = match.match_id

  def run(self):

    match = DBSession.query(Match).get(self.match_id)
    while match.state not in ['COMPLETE', 'FAILED']:
      current_player = DBSession.query(Player).get(match.player_to_move_id)  
      payload = {'board': match.to_json()}

      try:
        response = requests.get(current_player.url, params=payload, timeout=30)
      except requests.ConnectionError as e:
        match.state = 'FALIED'
        logger.error('Connecting to player failed: %s' % str(e))
        break

      start = time.time()
      move = json.loads(response.content)['move']
      elapsed = int((time.time() - start) * 1000000)
      direction = directions[move]
      match.move(direction, elapsed)
    transaction.commit()
    DBSession.close()
    return self.__queue.put(match)
