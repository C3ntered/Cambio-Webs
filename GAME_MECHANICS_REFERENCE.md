# Game Mechanics Reference - What to Rewrite

This document outlines all the game mechanics sections in the codebase that need to be rewritten based on the actual Cambio rules.

## Key Rules to Implement:
1. **Initial Card Viewing**: Players can look at TWO cards at the beginning, then memorize them (cards face down)
2. **Drawing Cards**: When drawing, players can choose to:
   - Switch it out (swap with a card in hand)
   - Use its ability
3. **Card Abilities**: Some abilities allow looking at other players' cards
4. **Card Viewing Mechanics**: When a card is revealed, show it for 5 seconds, then flip back face down - players must memorize

---

## 1. Card Value & Ability Functions (Lines 95-120)
**File**: `backend.py`

```python
def get_card_value(card: Card) -> int:
    """Return the scoring value for a card according to Cambio rules."""
    # Currently: Returns point values for scoring
    # TO REWRITE: Update based on actual scoring rules

def get_card_ability(card: Card) -> Optional[str]:
    """Map a card rank to its special ability."""
    # Currently: Maps card ranks to ability names (peek_self, peek_other, blind_swap, look_and_swap)
    # TO REWRITE: Update ability system based on actual card abilities
```

---

## 2. Game Start Logic (Lines 186-222)
**File**: `backend.py` - `GameRoomManager.start_game()`

```python
def start_game(self, room_id: str):
    """Start the game in a room"""
    # Currently: 
    # - Deals 4 cards per player
    # - Flips first discard card
    # - Sets first player's turn immediately
    
    # TO REWRITE:
    # - Deal cards to players (face down)
    # - Allow players to look at TWO cards initially
    # - Implement viewing phase before game starts
    # - Cards should be face down after viewing period
```

---

## 3. Card Ability Resolution (Lines 381-474)
**File**: `backend.py` - `GameRoomManager.resolve_card_ability()`

```python
async def resolve_card_ability(self, room: Room, acting_player: Player, ability: str, payload: Dict) -> bool:
    """Execute the requested ability if the payload is valid."""
    # Currently handles:
    # - peek_self: Look at own card
    # - peek_other: Look at opponent's card
    # - blind_swap: Swap cards without looking
    # - look_and_swap: Look at two cards and optionally swap
    
    # TO REWRITE:
    # - Implement temporary card viewing (5 seconds)
    # - Send card reveal to player
    # - Auto-flip back after 5 seconds
    # - Update based on actual ability mechanics
```

---

## 4. Draw Card Handler (Lines 740-820)
**File**: `backend.py` - WebSocket handler for `draw_card`

```python
elif msg_type == "draw_card":
    # Currently:
    # - Draws card from deck
    # - Adds to hand immediately
    # - Moves to next turn automatically
    
    # TO REWRITE:
    # - Draw card but DON'T add to hand immediately
    # - Give player choice: swap with hand card OR use ability
    # - Only then move to next turn
```

---

## 5. Play Card Handler (Lines 626-738)
**File**: `backend.py` - WebSocket handler for `play_card`

```python
if msg_type == "play_card":
    # Currently:
    # - Plays card to discard pile
    # - Checks for abilities if card was just drawn
    # - Moves to next turn
    
    # TO REWRITE:
    # - This might need to be combined with draw logic
    # - Or separated into: swap_card, use_ability, discard_card
```

---

## 6. Reveal Card Handler (Lines 940-973)
**File**: `backend.py` - WebSocket handler for `reveal_card`

```python
elif msg_type == "reveal_card":
    # Currently:
    # - Permanently reveals card to all players
    # - Stores in revealed_cards dict
    
    # TO REWRITE:
    # - Temporarily reveal card to requesting player
    # - Show for 5 seconds with timer
    # - Auto-flip back to face down
    # - Only send reveal to the player viewing (not everyone)
```

---

## 7. Game State Model (Lines 53-69)
**File**: `backend.py` - `GameState` class

```python
class GameState(BaseModel):
    # Currently has:
    # - revealed_cards: Dict[str, List[Card]]  # Permanent reveals
    
    # TO ADD:
    # - viewing_phase: bool  # Are players in initial viewing phase?
    # - cards_viewed: Dict[str, List[int]]  # Which card indices each player has viewed
    # - temporary_reveals: Dict[str, Dict]  # Active temporary card reveals with timestamps
```

---

## 8. Player Model (Lines 44-51)
**File**: `backend.py` - `Player` class

```python
class Player(BaseModel):
    # Currently has:
    # - last_draw_source: Optional[str]
    # - last_drawn_card: Optional[Card]
    
    # MAY NEED TO ADD:
    # - pending_drawn_card: Optional[Card]  # Card drawn but not yet added to hand
    # - cards_memorized: Dict[int, Card]  # Cards they've seen and need to remember
```

---

## Frontend Changes Needed

### bridge.js - Card Display Logic
- **Card rendering**: Show cards face down by default
- **Card viewing**: Implement flip animation for temporary reveals
- **Timer**: Show 5-second countdown when viewing a card
- **Initial viewing phase**: UI to let players view their 2 cards at game start

### bridge.js - Draw/Play Logic
- **After drawing**: Show choice UI (swap with hand card OR use ability)
- **Card selection**: Allow selecting which card to swap with
- **Ability activation**: UI for using card abilities

---

## New WebSocket Message Types Needed

You may need to add:
- `view_initial_cards`: Request to view initial 2 cards
- `card_view_timeout`: Server notification that viewing time is up
- `swap_drawn_card`: Swap the drawn card with a hand card
- `use_card_ability`: Use the ability of the drawn card
- `view_card_temporary`: Request to temporarily view a card (5 seconds)

---

## Summary of Major Changes

1. **Initial Phase**: Add viewing phase at game start where players see 2 cards
2. **Drawing Mechanics**: Don't auto-add to hand - give player choice first
3. **Card Viewing**: Implement temporary reveals (5 seconds) instead of permanent
4. **Memory System**: All cards face down, players track what they've seen
5. **Ability System**: Rewrite based on actual Cambio card abilities
6. **Frontend**: Add flip animations, timers, choice UI after drawing

