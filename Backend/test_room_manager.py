import pytest
from Backend.backend import Card, GameRoomManager, Room, Player, GameStatus, GameState, get_card_value

def test_deck_auto_adjustment_below_threshold():
    manager = GameRoomManager()

    # Test Case 1: 4 players, 4 cards each (total 16). num_decks should remain 1.
    room = manager.create_room(username="Player1", max_players=4, num_decks=1, initial_hand_size=4)
    # Add 3 more players
    for i in range(2, 5):
        manager.join_room(room.room_id, f"Player{i}")

    manager.start_game(room.room_id)
    assert room.num_decks == 1
    assert len(room.game_state.deck) == 54 - (4 * 4) - 1 # 1 deck (54 cards) - 16 cards - 1 starter card

def test_deck_no_adjustment_at_boundary():
    manager = GameRoomManager()

    # Test Case: Exactly 36 cards drawn, two-thirds of a 54-card deck.
    # Logic: total_drawn > 36. So 36 should NOT trigger adjustment.
    room = manager.create_room(username="Player1", max_players=6, num_decks=1, initial_hand_size=6)
    for i in range(2, 7):
        manager.join_room(room.room_id, f"Player{i}")

    manager.start_game(room.room_id)
    assert room.num_decks == 1
    assert len(room.game_state.deck) == 54 - 36 - 1

def test_deck_auto_adjustment_above_threshold():
    manager = GameRoomManager()

    # Test Case 2: 7 players, 6 cards each (total 42). num_decks should auto-adjust to 2.
    room = manager.create_room(username="Player1", max_players=8, num_decks=1, initial_hand_size=6)
    for i in range(2, 8):
        manager.join_room(room.room_id, f"Player{i}")

    manager.start_game(room.room_id)
    assert room.num_decks == 2
    assert len(room.game_state.deck) == (2 * 54) - (7 * 6) - 1

def test_deck_auto_adjustment_safety_check():
    manager = GameRoomManager()

    # Test Case 3: 10 players, 5 cards each (total 50). num_decks should auto-adjust to 2.
    # Logic: total_drawn > 48.
    room = manager.create_room(username="Player1", max_players=10, num_decks=1, initial_hand_size=5)
    # Add 9 more players
    for i in range(2, 11):
        manager.join_room(room.room_id, f"Player{i}")

    manager.start_game(room.room_id)
    assert room.num_decks == 2
    assert len(room.game_state.deck) == (2 * 54) - (10 * 5) - 1

def test_deck_no_adjustment_if_already_two():
    manager = GameRoomManager()

    # Test Case 4: 2 players, 4 cards each, but num_decks manually set to 2. num_decks should remain 2.
    room = manager.create_room(username="Player1", max_players=4, num_decks=2, initial_hand_size=4)
    manager.join_room(room.room_id, "Player2")

    manager.start_game(room.room_id)
    assert room.num_decks == 2
    assert len(room.game_state.deck) == (2 * 54) - (2 * 4) - 1


def test_room_code_is_short_and_case_insensitive_for_joining():
    manager = GameRoomManager()

    room = manager.create_room(username="Player1")

    assert len(room.room_id) == 6

    joined_room, player_id = manager.join_room(room.room_id.lower(), "Player2")

    assert joined_room.room_id == room.room_id
    assert player_id
    assert len(joined_room.players) == 2


def test_red_king_value_depends_on_deck_count():
    red_king = Card(suit="Hearts", rank="King")

    assert get_card_value(red_king, num_decks=1) == -2
    assert get_card_value(red_king, num_decks=2) == -1


def test_can_update_settings_between_rounds():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1", num_decks=1, initial_hand_size=4)

    updated = manager.update_room_settings(room.room_id, num_decks=2, initial_hand_size=6)

    assert updated.num_decks == 2
    assert updated.initial_hand_size == 6


def test_join_finished_room_for_next_round():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1")
    room.status = GameStatus.FINISHED

    joined_room, player_id = manager.join_room(room.room_id, "Player2")

    assert player_id
    assert joined_room.status == GameStatus.FINISHED
    assert len(joined_room.players) == 2


def test_create_practice_room_adds_bot_player():
    manager = GameRoomManager()

    room = manager.create_room(username="Player1", play_with_bot=True)

    assert len(room.players) == 2
    assert any(player.is_bot for player in room.players)
    assert room.players[0].is_bot is False


def test_room_settings_can_toggle_turn_timer():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1")

    updated = manager.update_room_settings(room.room_id, turn_timer_enabled=True)

    assert updated.turn_timer_enabled is True


def test_start_game_records_turn_start_time():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1", play_with_bot=True)

    manager.start_game(room.room_id)

    assert room.game_state.turn_started_at is not None
