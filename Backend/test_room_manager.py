import pytest
import asyncio
from datetime import datetime, timedelta, timezone
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
    assert room.game_state.turn_started_at.tzinfo is not None


def test_bot_takes_low_discard_over_high_hand_card():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1", play_with_bot=True)
    bot = next(player for player in room.players if player.is_bot)
    bot.hand = [
        Card(suit="Clubs", rank="Queen"),
        Card(suit="Spades", rank="9"),
        Card(suit="Hearts", rank="5"),
        Card(suit="Diamonds", rank="2"),
    ]
    room.game_state.discard_pile = [Card(suit="Clubs", rank="Ace")]

    assert manager._bot_should_take_discard(room, bot) is True


def test_bot_ignores_bad_discard_when_hand_is_better():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1", play_with_bot=True)
    bot = next(player for player in room.players if player.is_bot)
    bot.hand = [
        Card(suit="Clubs", rank="Ace"),
        Card(suit="Spades", rank="2"),
        Card(suit="Hearts", rank="3"),
        Card(suit="Diamonds", rank="4"),
    ]
    room.game_state.discard_pile = [Card(suit="Clubs", rank="Queen")]

    assert manager._bot_should_take_discard(room, bot) is False


def test_bot_swaps_drawn_card_only_when_it_improves_hand():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1", play_with_bot=True)
    bot = next(player for player in room.players if player.is_bot)
    bot.hand = [
        Card(suit="Clubs", rank="Queen"),
        Card(suit="Spades", rank="9"),
        Card(suit="Hearts", rank="5"),
        Card(suit="Diamonds", rank="2"),
    ]

    assert manager._bot_should_swap_drawn_card(room, bot, Card(suit="Clubs", rank="3")) is True

    bot.hand = [
        Card(suit="Clubs", rank="Ace"),
        Card(suit="Spades", rank="2"),
        Card(suit="Hearts", rank="3"),
        Card(suit="Diamonds", rank="4"),
    ]
    assert manager._bot_should_swap_drawn_card(room, bot, Card(suit="Clubs", rank="Queen")) is False


def test_bot_targets_highest_value_card_for_swap():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1", play_with_bot=True)
    bot = next(player for player in room.players if player.is_bot)
    bot.hand = [
        Card(suit="Clubs", rank="Ace"),
        Card(suit="Spades", rank="Queen"),
        Card(suit="Hearts", rank="8"),
        Card(suit="Diamonds", rank="2"),
    ]

    assert manager._bot_worst_card_index(room, bot) == 1


def test_cleanup_removes_abandoned_bot_room_after_five_minutes():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1", play_with_bot=True)
    human = next(player for player in room.players if not player.is_bot)
    human.is_connected = False
    room.last_activity = datetime.now() - timedelta(minutes=6)

    asyncio.run(manager.cleanup_stale_rooms())

    assert room.room_id not in manager.rooms


def test_cleanup_keeps_bot_room_with_connected_human_before_active_timeout():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1", play_with_bot=True)
    room.last_activity = datetime.now() - timedelta(minutes=6)

    asyncio.run(manager.cleanup_stale_rooms())

    assert room.room_id in manager.rooms


def test_cleanup_removes_active_waiting_lobby_after_shorter_timeout():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1")
    room.last_activity = datetime.now() - timedelta(minutes=46)

    asyncio.run(manager.cleanup_stale_rooms())

    assert room.room_id not in manager.rooms


def test_cleanup_removes_abandoned_human_game_after_ten_minutes():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1")
    manager.join_room(room.room_id, "Player2")
    for player in room.players:
        player.is_connected = False
    room.status = GameStatus.PLAYING
    room.last_activity = datetime.now() - timedelta(minutes=11)

    asyncio.run(manager.cleanup_stale_rooms())

    assert room.room_id not in manager.rooms


def test_turn_timer_accepts_timezone_aware_timestamp():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1", play_with_bot=True, turn_timer_enabled=True)
    room.status = GameStatus.PLAYING
    room.game_state.game_phase = "playing"
    room.game_state.current_turn = room.players[0].player_id
    room.game_state.turn_started_at = datetime.now(timezone.utc) - timedelta(seconds=61)

    assert manager.should_auto_advance_turn(room, datetime.now(timezone.utc)) is True


def test_empty_hand_does_not_end_round_before_cambio():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1")
    manager.join_room(room.room_id, "Player2")
    manager.start_game(room.room_id)
    room.game_state.viewing_phase = False
    room.game_state.game_phase = "playing"
    empty_hand_player = room.players[0]
    empty_hand_player.hand = [None] * len(empty_hand_player.hand)
    room.game_state.current_turn = empty_hand_player.player_id

    asyncio.run(manager.end_turn(room.room_id, check_win=True))

    assert room.status == GameStatus.PLAYING
    assert room.game_state.game_phase == "playing"
    assert room.game_state.current_turn == room.players[1].player_id


def test_cambio_starts_scoring_only_after_every_other_player_turn():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1")
    manager.join_room(room.room_id, "Player2")
    manager.join_room(room.room_id, "Player3")
    manager.start_game(room.room_id)
    caller = room.players[0]
    room.game_state.current_turn = caller.player_id
    room.game_state.cambio_called = True
    room.game_state.cambio_caller = caller.player_id

    assert manager.next_turn(room.room_id) is None
    assert room.game_state.final_round_turns == 2
    assert manager.next_turn(room.room_id) is None
    assert room.status == GameStatus.PLAYING
    assert manager.next_turn(room.room_id) == "GRACE_PERIOD"
    assert room.status == GameStatus.GRACE_PERIOD


def test_disconnect_removes_player_and_advances_current_turn():
    manager = GameRoomManager()
    room = manager.create_room(username="Player1")
    _, player2_id = manager.join_room(room.room_id, "Player2")
    manager.start_game(room.room_id)
    room.game_state.viewing_phase = False
    room.game_state.game_phase = "playing"
    room.game_state.current_turn = player2_id

    updated_room, removed_player, deleted_room = manager.disconnect_player_from_room(room.room_id, player2_id)

    assert deleted_room is False
    assert removed_player.player_id == player2_id
    assert all(player.player_id != player2_id for player in updated_room.players)
    assert updated_room.game_state.current_turn == updated_room.players[0].player_id
