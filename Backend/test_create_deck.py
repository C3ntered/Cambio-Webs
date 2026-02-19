import pytest
from Backend.backend import GameRoomManager, Card

def test_create_deck_default_size():
    manager = GameRoomManager()
    deck = manager.create_deck()
    assert len(deck) == 54

def test_create_deck_custom_size():
    manager = GameRoomManager()
    deck = manager.create_deck(num_decks=2)
    assert len(deck) == 108

def test_create_deck_contents():
    manager = GameRoomManager()
    deck = manager.create_deck(num_decks=1)

    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

    # Check standard cards
    for suit in suits:
        for rank in ranks:
            count = sum(1 for card in deck if card.suit == suit and card.rank == rank)
            assert count == 1, f"Missing or duplicate card: {rank} of {suit}"

    # Check Jokers
    jokers = [card for card in deck if card.suit == "Joker" and card.rank == "Joker"]
    assert len(jokers) == 2

def test_create_deck_multi_deck_contents():
    manager = GameRoomManager()
    num_decks = 2
    deck = manager.create_deck(num_decks=num_decks)

    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

    # Check standard cards
    for suit in suits:
        for rank in ranks:
            count = sum(1 for card in deck if card.suit == suit and card.rank == rank)
            assert count == num_decks

    # Check Jokers
    jokers = [card for card in deck if card.suit == "Joker" and card.rank == "Joker"]
    assert len(jokers) == 2 * num_decks

def test_create_deck_zero_decks():
    manager = GameRoomManager()
    deck = manager.create_deck(num_decks=0)
    assert len(deck) == 0

def test_create_deck_negative_decks():
    manager = GameRoomManager()
    deck = manager.create_deck(num_decks=-1)
    assert len(deck) == 0
