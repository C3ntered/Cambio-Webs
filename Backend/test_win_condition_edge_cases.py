import sys
from unittest.mock import MagicMock
from datetime import datetime

# --- MOCKING ---
# We use this mocking strategy because 'fastapi' and 'pydantic' are not
# installed in the current environment, preventing 'backend.py' from being imported directly.
class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def model_dump(self, **kwargs):
        return {}

mock_pydantic = MagicMock()
mock_pydantic.BaseModel = MockBaseModel
mock_pydantic.ConfigDict = MagicMock()
sys.modules["pydantic"] = mock_pydantic

mock_fastapi = MagicMock()
mock_fastapi.FastAPI = MagicMock()
mock_fastapi.WebSocket = MagicMock()
mock_fastapi.WebSocketDisconnect = Exception
mock_fastapi.HTTPException = Exception
sys.modules["fastapi"] = mock_fastapi
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()

# Import the actual classes after mocking
from Backend.backend import GameRoomManager, Room, Player, GameState, GameStatus

# --- TESTS ---

def test_check_win_condition_non_existent_room():
    """Verify that checking a non-existent room returns None."""
    manager = GameRoomManager()
    assert manager.check_win_condition("non_existent_room") is None

def test_check_win_condition_empty_players():
    """Verify that a room with zero players returns None for win condition."""
    manager = GameRoomManager()
    room_id = "test_room_empty"

    room = Room(
        room_id=room_id,
        players=[],
        game_state=GameState(),
        status=GameStatus.PLAYING,
        created_at=datetime.now()
    )
    manager.rooms[room_id] = room

    assert manager.check_win_condition(room_id) is None

def test_check_win_condition_no_winner_yet():
    """Verify that an active game with no winner returns None."""
    manager = GameRoomManager()
    room_id = "test_room_active"

    player1 = Player(player_id="p1", username="user1", hand=[MagicMock(), MagicMock()])
    player2 = Player(player_id="p2", username="user2", hand=[MagicMock(), MagicMock()])

    room = Room(
        room_id=room_id,
        players=[player1, player2],
        game_state=GameState(),
        status=GameStatus.PLAYING,
        created_at=datetime.now()
    )
    manager.rooms[room_id] = room

    assert manager.check_win_condition(room_id) is None

def test_check_win_condition_player_wins():
    """Verify that check_win_condition correctly identifies a winner with an empty hand."""
    manager = GameRoomManager()
    room_id = "test_room_winner"

    player1 = Player(player_id="p1", username="user1", hand=[MagicMock(), MagicMock()])
    player2 = Player(player_id="p2", username="user2", hand=[None, None]) # Empty hand

    room = Room(
        room_id=room_id,
        players=[player1, player2],
        game_state=GameState(),
        status=GameStatus.PLAYING,
        created_at=datetime.now()
    )
    manager.rooms[room_id] = room

    assert manager.check_win_condition(room_id) == "p2"
