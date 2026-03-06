import pytest
from Backend.backend import GameRoomManager, Card, SUITS, RANKS

def test_create_deck_length():
    manager = GameRoomManager()

    # 1 deck: 52 + 2 = 54 cards
    deck1 = manager.create_deck(num_decks=1)
    assert len(deck1) == 54

    # 2 decks: 54 * 2 = 108 cards
    deck2 = manager.create_deck(num_decks=2)
    assert len(deck2) == 108

def test_create_deck_composition():
    manager = GameRoomManager()
    deck = manager.create_deck(num_decks=1)

    # Check counts of each rank
    for rank in RANKS:
        rank_count = sum(1 for card in deck if card.rank == rank)
        assert rank_count == 4, f"Rank {rank} should appear 4 times, found {rank_count}"

    # Check counts of each suit
    for suit in SUITS:
        suit_count = sum(1 for card in deck if card.suit == suit)
        assert suit_count == 13, f"Suit {suit} should appear 13 times, found {suit_count}"

    # Check Jokers
    joker_count = sum(1 for card in deck if card.rank == "Joker" and card.suit == "Joker")
    assert joker_count == 2, f"Jokers should appear 2 times, found {joker_count}"

def test_create_deck_multiple_decks():
    manager = GameRoomManager()
    num_decks = 2
    deck = manager.create_deck(num_decks=num_decks)

    # Check counts of each rank
    for rank in RANKS:
        rank_count = sum(1 for card in deck if card.rank == rank)
        assert rank_count == 4 * num_decks, f"Rank {rank} should appear {4 * num_decks} times, found {rank_count}"

    # Check counts of each suit
    for suit in SUITS:
        suit_count = sum(1 for card in deck if card.suit == suit)
        assert suit_count == 13 * num_decks, f"Suit {suit} should appear {13 * num_decks} times, found {suit_count}"

    # Check Jokers
    joker_count = sum(1 for card in deck if card.rank == "Joker" and card.suit == "Joker")
    assert joker_count == 2 * num_decks, f"Jokers should appear {2 * num_decks} times, found {joker_count}"
