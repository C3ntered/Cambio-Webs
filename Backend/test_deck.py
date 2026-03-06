from Backend.backend import GameRoomManager, SUITS, RANKS

def test_create_single_deck():
    manager = GameRoomManager()
    deck = manager.create_deck(num_decks=1)
    assert len(deck) == 54

    # Check for 52 standard cards
    for suit in SUITS:
        for rank in RANKS:
            assert any(c.suit == suit and c.rank == rank for c in deck)

    # Check for 2 Jokers
    jokers = [c for c in deck if c.suit == "Joker" and c.rank == "Joker"]
    assert len(jokers) == 2

def test_create_multiple_decks():
    manager = GameRoomManager()
    deck = manager.create_deck(num_decks=2)
    assert len(deck) == 108

    # Check for 4 Jokers
    jokers = [c for c in deck if c.suit == "Joker" and c.rank == "Joker"]
    assert len(jokers) == 4

def test_create_zero_decks():
    manager = GameRoomManager()
    deck = manager.create_deck(num_decks=0)
    assert len(deck) == 0

def test_create_default_decks():
    manager = GameRoomManager()
    deck = manager.create_deck() # default should be 1
    assert len(deck) == 54
