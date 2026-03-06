import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from Backend.backend import GameRoomManager, GameStatus

def test_start_grace_period_success():
    manager = GameRoomManager()
    room = manager.create_room(username="TestUser")
    room_id = room.room_id

    # Ensure initial state is WAITING
    assert room.status == GameStatus.WAITING
    assert room.game_state.game_phase == "waiting"
    assert room.grace_period_end is None

    # Mock datetime.now to ensure determinism
    fixed_now = datetime(2023, 10, 27, 12, 0, 0)
    with patch("Backend.backend.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        # Transition to grace period
        manager.start_grace_period(room_id)

    # Verify updates
    assert room.status == GameStatus.GRACE_PERIOD
    assert room.game_state.game_phase == "grace_period"
    assert room.grace_period_end is not None

    # Verify grace_period_end is exactly 10 seconds from fixed_now
    expected_end = fixed_now + timedelta(seconds=10)
    assert room.grace_period_end == expected_end

def test_start_grace_period_invalid_room():
    manager = GameRoomManager()
    # Call with non-existent room_id
    manager.start_grace_period("non-existent-id")
    # Should just return without error
    assert "non-existent-id" not in manager.rooms
