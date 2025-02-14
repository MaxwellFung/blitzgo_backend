import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from game import Game
from player import Player
from board import Board
from timer import Timer
import asyncio
import sys
import os
import threading
import time

cred = credentials.Certificate('blitzgowest-firebase-adminsdk-a0vzp-be4c05ae95.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
sessions_ref = db.collection('Users')
docs = sessions_ref.stream()

async def begin(session):
  games_ref = db.collection("Games")
  user_ref = db.collection("Users")
  user_doc = games_ref.document(session).get()
  game_doc = games_ref.document(session).get()




  players = user_doc.get("Players")
  player_1_uid = players[0]
  player_2_uid = players[1]
  boardSize = int(game_doc.get("boardSize"))
  games_data = {
    "code": str(session),
    "player1": player_1_uid,
    "player2": player_2_uid,
    "board" : [0 for i in range(boardSize**2)],
    "first_territory": 0,
    "second_territory": 0,
    "winner": 0, #0= no winner, 1=black, 2= white, 3=draw
    "sound_played": 0, #0=none, 1=stone placed, 2=capture, 3=victory
  }

  #Set up game. create game object
  game = Game(int(boardSize))
  P_1 = Player()
  P_2 = Player()
  game.addPlayer(P_1)
  game.addPlayer(P_2)

  player_1_data = {
    "your_turn" : P_1.isBlack,
    "is_black" : P_1.isBlack,
    "position": (-1, -1),
    "processed" : False,
    "valid_move": 2, #0 = Valid, #1= Dupe, #2 = Invalid
  }

  player_2_data = {
    "your_turn" : P_2.isBlack,
    "is_black" : P_2.isBlack,
    "position": (-1, -1),
    "processed" : False,
    "valid_move": 2, #0 = Valid, #1= Dupe, #2 = Invalid
  }

  user_ref.document(player_1_uid).set(player_1_data, merge=True)
  user_ref.document(player_2_uid).set(player_2_data, merge=True)
  games_ref.document(session).set(games_data, merge=True)

  def time_up():
    print('times up!')

  player_1_timer = Timer(601, time_up)
  player_2_timer = Timer(601, time_up)
  player_1_timer.start()
  player_1_timer.pause()
  player_2_timer.start()
  player_2_timer.pause()



  def on_snapshot_player_1(doc_snapshot, changes, read_time):
    json = doc_snapshot[0].to_dict()
    L = json.get("position")
    if L != ["resigned"]:
      if game.currPlayer() == P_1:
        position = (int(L[0]),int(L[1]))
        result = game.placeStone(position)
        if game.first_move:
          if result == 0:
            player_1_timer.pause()
          player_2_timer.resume()

        if(json.get("session") != session):
          print('ended: ' + session)
          os._exit(0)

        sound = 1

        territories = get_territory(P_1, P_2, game)
        black_territory = territories[0]
        white_territory = territories[1]

        if black_territory != 0:
          first_move = True
        else:
          first_move = False


        winner = game_over(black_territory, white_territory, game)
        games_ref.document(session).set({"board": game.board.flattenBoard(), "black_territory": black_territory, "white_territory": white_territory, "winner": winner, "your_turn_1": game.currPlayer() == P_1, "your_turn_2": game.currPlayer() == P_2, "valid_move": result, "sound_played": sound, "time_1": player_1_timer.get_remaining_time(), "time_2": player_2_timer.get_remaining_time(), "first_move": first_move}, merge=True)
        game.set_first()
    else:
      if P_1.getStoneCode() == 1:
        winner = 2
      else:
        winner = 1
      games_ref.document(session).set({"winner": winner}, merge=True)

  def on_snapshot_player_2(doc_snapshot, changes, read_time):
    json = doc_snapshot[0].to_dict()
    L = json.get("position")
    if L != ["resigned"]:
      if game.currPlayer() == P_2:
        position = (int(L[0]),int(L[1]))
        result = game.placeStone(position)
        if game.first_move:
          if result == 0:
            player_2_timer.pause()
          player_1_timer.resume()

        if(json.get("session") != session):
          print('ended: ' + session)
          os._exit(0)
          
        sound = 1

        territories = get_territory(P_1, P_2, game)
        black_territory = territories[0]
        white_territory = territories[1]

        if black_territory != 0:
          first_move = True
        else:
          first_move = False


        winner = game_over(black_territory, white_territory, game)
        games_ref.document(session).set({"board": game.board.flattenBoard(), "black_territory": black_territory, "white_territory": white_territory, "winner": winner, "your_turn_1": game.currPlayer() == P_1, "your_turn_2": game.currPlayer() == P_2, "valid_move": result, "sound_played": sound, "time_1": player_1_timer.get_remaining_time(), "time_2": player_2_timer.get_remaining_time(), "first_move": first_move}, merge=True)
        game.set_first()
    else:
      if P_1.getStoneCode() == 1:
        winner = 1
      else:
        winner = 2
      games_ref.document(session).set({"winner": winner}, merge=True)


  player_1_listener = db.collection("Users").document(player_1_uid).on_snapshot(on_snapshot_player_1)
  player_2_listener = db.collection("Users").document(player_2_uid).on_snapshot(on_snapshot_player_2)

  while not game.checkGameOver() and not player_1_timer.has_timed_out() and not player_2_timer.has_timed_out():
    await asyncio.sleep(1)
  else:
    player_1_timer.pause()
    player_2_timer.pause()
    if player_1_timer.has_timed_out() and P_1.getStoneCode() == 1:
      games_ref.document(session).set({"winner": 2, "time_1": player_1_timer.get_remaining_time(), "time_2": player_2_timer.get_remaining_time()}, merge=True)
    elif player_1_timer.has_timed_out() and P_1.getStoneCode() == 2:
      games_ref.document(session).set({"winner": 1, "time_1": player_1_timer.get_remaining_time(), "time_2": player_2_timer.get_remaining_time()}, merge=True)
    elif player_2_timer.has_timed_out() and P_2.getStoneCode() == 1:
      games_ref.document(session).set({"winner": 2, "time_1": player_1_timer.get_remaining_time(), "time_2": player_2_timer.get_remaining_time()}, merge=True)
    elif player_2_timer.has_timed_out() and P_2.getStoneCode() == 2:
      games_ref.document(session).set({"winner": 1, "time_1": player_1_timer.get_remaining_time(), "time_2": player_2_timer.get_remaining_time()}, merge=True)
    print('ended: ' + session)


def get_territory(P_1, P_2, game):
  if P_1.getStoneCode() == 1:
    return [game.getTerritoryCount(P_1), game.getTerritoryCount(P_2)]
  else:
    return [game.getTerritoryCount(P_2), game.getTerritoryCount(P_1)]


def game_over(black_territory, white_territory, game):
  if(game.checkGameOver()):
    if black_territory > white_territory:
      return 1
    elif black_territory < white_territory:
      return 2
    elif black_territory == white_territory:
      return 3
  else:
    return 0
  

def stop_program():
  print("3 hours have passed. Terminating the program: " + sys.argv[1])
  os._exit(0)

def run(code):
  timer = threading.Timer(10800, stop_program)
  timer.start()

  asyncio.set_event_loop(asyncio.new_event_loop())
  loop = asyncio.get_event_loop()
  loop.run_until_complete(begin(code))

run(sys.argv[1])