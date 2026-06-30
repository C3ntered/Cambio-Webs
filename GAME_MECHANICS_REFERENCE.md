# Cambio Game Mechanics Reference

This document summarizes the gameplay rules and implementation choices used by
the current codebase. It is meant as a companion to the backend docstrings and
the player-facing instructions page.

Author: Kai Holland

AI assistance and co-authoring:

- OpenAI ChatGPT/Codex: code generation, optimization, documentation, and
  implementation assistance.
- Anthropic Claude: debugging assistance.
- Google Jules: substantial authorship of `Frontend/bridge.js`.

Last updated: 2026-06-30

## Room Lifecycle

Rooms are created through `POST /api/rooms` or the browser lobby. A room starts
in `waiting`, moves to `playing` after the host starts the game, enters
`grace_period` after the final round following a Cambio call, and ends as
`finished` after scores are tallied.

Rooms are stored in memory. Cleanup runs once per minute:

- Bot-only or abandoned bot rooms close after 5 minutes.
- Playing rooms with no connected human players close after 10 minutes.
- Playing rooms with connected humans close after 20 minutes of inactivity.
- Waiting rooms with no connected humans close after 15 minutes.
- Waiting rooms with connected humans close after 45 minutes.
- Finished rooms close after 10 minutes.

## Decks and Cards

Each deck contains 54 cards:

- 52 standard suited cards.
- 2 Jokers.

The room can use one or two decks. The backend automatically switches to two
decks when the configured deal would consume too much of one deck.

## Card Values

Scoring is handled by `get_card_value` in `Backend/backend.py`:

- Ace: 1
- 2 through 10: face value
- Jack, Queen, black King: 10
- Red King: -2 with one deck, -1 with two decks
- Joker: 0

Lowest score wins. Ties are resolved by fewer remaining cards, then by whether
the tied player called Cambio.

## Card Abilities

Discarding certain cards from a deck draw creates an optional ability:

- 7 or 8: peek at one of your own cards.
- 9 or 10: peek at an opponent's card.
- Jack or Queen: blind swap any two valid cards.
- Black King: look at two valid cards, then optionally swap them.

Ability reveal results are sent privately to the acting player. Other players
receive visual indicators that a card is being inspected, but not the card face.

## Round Start

When a game starts:

1. The backend shuffles the deck.
2. Each player receives the configured hand size.
3. One starter card is flipped to the discard pile.
4. The room enters the initial viewing phase.
5. Players can see their bottom-row starting cards briefly, then the round
   begins.

## Turn Flow

On a normal turn, the active player can:

1. Draw from the deck.
2. Draw from the discard pile.
3. Call Cambio before drawing.

Deck draws create a pending card. The player can either:

- Swap it with a card in hand, sending the replaced card to discard.
- Discard the drawn card. If it has an ability, the player may use or skip it.

Discard-pile draws must be swapped into the player's hand.

## Eliminations

Players may attempt to eliminate cards by matching the rank of the top discard.

- Eliminating your own matching card removes that card slot.
- Eliminating an opponent's matching card requires giving them one of your cards
  as a replacement.
- A wrong elimination attempt draws a penalty card.

The backend validates card indices and ranks for every elimination attempt.

## Cambio and Scoring

A player may call Cambio at the start of their turn before drawing. After that:

1. The caller becomes immune to swap targeting.
2. Every other player gets one final turn.
3. The room enters a short grace period for last eliminations.
4. Scores are tallied and the lowest score wins.

## Practice Bot

Practice mode adds one bot player to the room. The bot:

- Pauses between visible actions so humans can react.
- Takes useful discard-pile cards.
- Keeps low-value deck draws or cards that improve its hand.
- Swaps out its highest-value known card.
- Can eliminate its own cards when they match the discard rank.

The bot is intentionally simple; it exists to let players learn the game without
needing another human in the room.

## Client Responsibilities

`Frontend/bridge.js` owns browser-side behavior:

- Creating and joining rooms.
- Opening WebSocket connections.
- Rendering room state.
- Handling draw, swap, ability, Cambio, and elimination interactions.
- Showing animations, notifications, turn timers, and score results.
- Pre-filling direct join links such as `/join/ABC123`.

The backend remains authoritative for all game state and validation.
