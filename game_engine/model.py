from pyramid.security import Allow, Everyone
import random
import json
import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    PickleType,
    DateTime,
    ForeignKey
    )

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class GameBoard(Base):
  '''
    The main game board engine model.  A match creates a game board and tells it which move
    each player makes.  The match keeps track of the score
  '''
  __tablename__ = 'game_board'
  game_board_id = Column(Integer(), primary_key=True, autoincrement=True)
  x_position = Column(PickleType)
  y_position = Column(PickleType)
  x_player_score = Column(Integer())
  y_player_score = Column(Integer())
  stars = relationship('Star')
  board_size = Column(PickleType)

  def __init__(self, board_size, num_stars):
    self.board_size = board_size
    self.x_position = (0,0)
    self.y_position = (board_size[0] - 1, board_size[1] - 1)
    self.board_size = board_size
    self.x_player_score = 0
    self.y_player_score = 0

    stars = self.random_stars(num_stars)
    for star in stars:
      self.stars.append(Star(*star))

  def random_stars(self, num_stars):
    stars = []
    for n in range(0, num_stars):
      x = -1
      y = -1
      while (x, y) not in stars:
        x = random.randint(0, self.board_size[0] - 1)
        y = random.randint(0, self.board_size[1] - 1)
        stars.append((x, y))
    return stars

  def move(self, player_number, direction):
    if player_number == 0: # Move player x
      new_position = self._new_position_from_direction(self.x_position, direction)
      if self.is_valid_position(new_position):
        self.x_position = new_position
        if self.x_position in map(Star.as_list, self.stars):
          self.x_player_score += 1
          for star in self.stars:
            if [star.x, star.y] == new_position:
              self.stars.pop(self.stars.index(star))
          print 'x ate a star'

    elif player_number == 1: # Move player y
      new_position = self._new_position_from_direction(self.y_position, direction)
      if self.is_valid_position(new_position):
        self.y_position = new_position
        if self.y_position in map(Star.as_list, self.stars):
          self.y_player_score += 1
          for star in self.stars:
            if [star.x, star.y] == new_position:
              self.stars.pop(self.stars.index(star))
          print 'y ate a star'


  def _new_position_from_direction(self, position, direction):
    new_position = list(position)
    if direction == UP:
      new_position[1] -= 1
    elif direction == DOWN:
      new_position[1] += 1
    elif direction == LEFT:
      new_position[0] -= 1
    elif direction == RIGHT:
      new_position[0] += 1
    else:
      raise Exception('Invalid direction.  Must be 0, 1, 2, or 3')

    return new_position


  def is_valid_position(self, position):
    if position in [self.x_position, self.y_position]:
      return False
    if (position[0] < 0 or position[0] >= self.board_size[0]):
      return False
    if (position[1] < 0 or position[1] >= self.board_size[1]):
      return False

    return True


class Star(Base):
  __tablename__ = 'star'
  star_id = Column(Integer(), primary_key=True, autoincrement=True)
  game_board_id = Column(Integer(), ForeignKey('game_board.game_board_id'))
  x = Column(Integer())
  y = Column(Integer())

  def __init__(self, x, y):
    self.x = x
    self.y = y

  def as_list(self):
    return [self.x, self.y]


class Match(Base):
  '''
    Possible game states: 'UNPLAYED', 'IN_PROGRESS', 'WAITING_FOR_MOVE', 'COMPLETE'
  '''
  __tablename__ = 'match'
  match_id = Column(Integer(), primary_key=True, autoincrement=True)
  x_player_id = Column(Integer(), ForeignKey('player.player_id'))
  y_player_id = Column(Integer(), ForeignKey('player.player_id'))
  x_player_score = Column(Integer())
  y_player_score = Column(Integer())
  max_moves = Column(Integer())
  game_board_id = Column(Integer(), ForeignKey('game_board.game_board_id'))
  state = Column(String())
  player_to_move_id = Column(Integer(), ForeignKey('player.player_id'))

  date_created = Column(DateTime())

  initial_stars = Column(PickleType())
  x_player = relationship('Player', foreign_keys=[x_player_id])
  y_player = relationship('Player', foreign_keys=[y_player_id])
  player_to_move = relationship('Player', foreign_keys=[player_to_move_id])

  next_move_id = Column(Integer())

  moves = relationship('Move')
  game_board = relationship('GameBoard')

  @property 
  def winner(self):
    if self.x_player_score > self.y_player_score:
      return self.x_player
    elif self.y_player_score > self.x_player_score:
      return self.y_player
    else:
      return None

  def __init__(self, player1_id, player2_id, board_size, num_stars, copied_board_id=None):
    if not copied_board_id:
      self.game_board = GameBoard(board_size, num_stars)
      self.initial_stars = map(Star.as_list, self.game_board.stars)
      players = [player1_id, player2_id]
      random.shuffle(players)
      self.date_created = datetime.datetime.now()

      self.x_player_id, self.y_player_id = players

      self.player_to_move_id = self.x_player_id

      self.x_player_score = 0
      self.y_player_score = 0

      self.next_move_id = 1
      self.max_moves = board_size[0] * board_size[1] * 10

      self.state = 'UNPLAYED'

    else:
      raise NotImplemented()
      #TODO implement board replay

  def move(self, direction, time_taken):
    new_move = Move(self.next_move_id, self.player_to_move_id, direction, time_taken)
    self.moves.append(new_move)
    self.next_move_id += 1

    if self.player_to_move_id == self.x_player_id:
      player_number = 0
    elif self.player_to_move_id == self.y_player_id:
      player_number = 1
    else:
      raise Exception('Match.player_to_move is not valid, player_to_move: %s' % self.player_to_move_id)

    self.game_board.move(player_number, direction)
    self.x_player_score = self.game_board.x_player_score
    self.y_player_score = self.game_board.y_player_score

    self.state = 'IN_PROGRESS'
    if player_number == 0:
      self.player_to_move_id = self.y_player_id
    elif player_number == 1:
      self.player_to_move_id = self.x_player_id

    if len(self.game_board.stars) == 0 or self.next_move_id > self.max_moves:
      self.state = 'COMPLETE'
      if self.x_player_score > self.y_player_score:
        self.x_player.wins += 1
        self.y_player.losses += 1
      elif self.y_player_score > self.x_player_score:
        self.y_player.wins += 1
        self.x_player.losses += 1
      return

  def to_json(self):
    d = {}
    d['stars'] = []
    for star in self.game_board.stars:
      d['stars'].append(star.as_list())

    d['x_position'] = list(self.game_board.x_position)
    d['y_position'] = list(self.game_board.y_position)
    d['x_score'] = self.x_player_score
    d['y_score'] = self.y_player_score
    d['player_to_move'] = 'X' if self.player_to_move_id == self.x_player_id else 'Y'
    return json.dumps(d)


class Player(Base):
  __tablename__ = 'player'
  player_id = Column(Integer(), primary_key=True, autoincrement=True)
  name = Column(String())
  url = Column(String())
  image_url = Column(String())
  rating = Column(Integer())
  wins = Column(Integer())
  losses = Column(Integer())

  def __init__(self, name, url, image_url=None):
    self.name = name
    self.url = url
    self.image_url = image_url
    self.rating = 0
    self.wins = 0
    self.losses = 0



class Move(Base):
  __tablename__ = 'move'
  move_number = Column(Integer(), primary_key=True)
  match_id = Column(Integer(), ForeignKey('match.match_id'), primary_key=True)
  player_id = Column(Integer(), ForeignKey('player.player_id'))
  direction = Column(Integer())
  time_taken = Column(Integer())  # in seconds

  def __init__(self, move_number, player_id, direction, time_taken):
    self.move_number = move_number
    self.direction = direction
    self.time_taken = time_taken
    self.player_id = player_id
