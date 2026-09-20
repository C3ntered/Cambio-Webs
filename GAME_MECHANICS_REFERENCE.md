# Cambio Game Mechanics Reference

This document summarizes the gameplay rules and implementation choices used by
the current codebase. It is meant as a companion to the backend docstrings and
the player-facing instructions page, and as a map for code review: each rule
below names the backend method (and, where relevant, the frontend function)
that implements it.

Author: Kai Holland

AI assistance and co-authoring:

- OpenAI ChatGPT/Codex: code generation, optimization, documentation, and
  implementation assistance.
- Anthropic Claude: game-logic bug fixes, reconnection support, bot AI,
  code cleanup, and documentation.
- Google Jules: substantial authorship of `Frontend/bridge.js`.

Last updated: 2026-09-19

## Room Lifecycle

Rooms are created through `POST /api/rooms` or the browser lobby
(`GameRoomManager.create_room`). A room starts in `WAITING`, moves to
`PLAYING` after the host starts the game (`GameRoomManager.start_game`),
enters `GRACE_PERIOD` after the final round following a Cambio call
(`start_grace_period`), optionally enters `TIEBREAK` for unresolved score ties
(`tally_scores`), and ends as `FINISHED` after a winner is determined
(`end_game`). These statuses live on the `GameStatus` enum.

Rooms are stored in memory only - there is no database, so a server restart
loses all active games. Cleanup runs once per minute
(`GameRoomManager.cleanup_stale_rooms`):

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

The room can use one or two decks. `GameRoomManager.start_game` automatically
switches to two decks when the configured deal would consume too much of one
deck (more than two-thirds, or when the deal physically needs more cards than
one deck holds).

## Card Values

Scoring is handled by `get_card_value` in `Backend/backend.py`:

- Ace: 1
- 2 through 10: face value
- Jack, Queen, black King: 10
- Red King: -2 with one deck, -1 with two decks
- Joker: 0

Lowest score wins. Ties are resolved by fewer remaining cards, then by whether
the tied player called Cambio. If multiple players remain tied, each tied
player reveals a draw from the deck (`draw_tiebreak_card`). Only players tied
for the lowest drawn value continue to another revealed draw, repeating until
one winner remains. Normal card values apply to every draw, including Jokers
and red Kings.

## Card Abilities

Discarding a card drawn from the *deck* (never a discard-pile draw, and never
a card swapped into hand instead of discarded) creates an optional ability,
mapped by rank in `get_card_ability`:

- 7 or 8: `peek_self` - peek at one of your own cards.
- 9 or 10: `peek_other` - peek at an opponent's card.
- Jack or Queen: `blind_swap` - swap any two valid cards (yours or anyone
  else's) without seeing either one.
- Black King: `look_and_swap` - look at two valid cards, then optionally swap
  them.

`GameRoomManager.resolve_card_ability` validates and executes all four
ability types from a single shared method. It is called from two places that
must stay in sync:

- The `use_ability` WebSocket message handler, for human players.
- `GameRoomManager._bot_use_pending_ability`, for the bot's own turn.

`look_and_swap` is two-phase: resolving it doesn't execute the swap, it
reveals both cards and sets `pending_ability = "swap_decision"`. The actual
swap-or-skip decision is a separate shared method,
`GameRoomManager.resolve_pending_swap_decision`, called from the
`resolve_swap_decision` message handler (human) and from
`_bot_use_pending_ability` (bot, immediately after "looking").

Ability reveal results are sent privately to the acting player
(`GameRoomManager.send_to_player`); other players receive a
`card_being_looked_at` broadcast so they see *that* a card is being
inspected, but not its face.

A drawn card's ability opportunity must never be silently lost just because
the turn ends some other way (a wrong-guess elimination penalty, for
example) - `GameRoomManager.discard_pending_drawn_card` is the shared path
that discards a still-pending drawn card and opens its ability, reused by
both the normal `resolve_draw` discard and the elimination-penalty flow.

## Round Start

When a game starts (`GameRoomManager.start_game`):

1. The backend shuffles the deck.
2. Each player receives the configured hand size.
3. One starter card is flipped to the discard pile.
4. The room enters the initial viewing phase (`game_phase = "viewing"`).
5. Players can see their bottom-row starting cards briefly, then the round
   begins.

## Turn Flow

On a normal turn, the active player can:

1. Draw from the deck (`draw_card` message).
2. Draw from the discard pile (`draw_from_discard` message).
3. Call Cambio before drawing (`call_cambio` message /
   `GameRoomManager.perform_cambio_call`).

Deck draws create a pending card (`player.pending_drawn_card`). The player
resolves it with `resolve_draw`, which can:

- Swap it with a card in hand, sending the replaced card to discard. This
  never triggers an ability, even if the replaced card had one.
- Discard the drawn card. If it has an ability, the player may use or skip
  it before the turn ends.

Discard-pile draws must be swapped into the player's hand - never discarded,
and never a source of an ability.

If a room has the optional turn timer enabled, `should_auto_advance_turn`
pauses the timer while the active player owes an elimination replacement
(`pending_replacement_target` is set) rather than letting the timer silently
void that obligation; `auto_advance_timed_out_turn` handles what happens when
the timer genuinely expires.

## Eliminations

Any player may attempt to eliminate any card - their own or an opponent's -
by matching the rank of the top discard, on any turn (not only their own),
via the `eliminate_card` message handler:

- Eliminating your own matching card just removes that card slot (sets it to
  `None`; slots are never re-packed, so eliminated cards leave a visible
  gap - see `_non_empty_card_indices`).
- Eliminating an opponent's matching card requires giving them one of your
  cards as a replacement (`give_replacement` message,
  `player.pending_replacement_target`). If the target leaves the room before
  the replacement is given, the obligation is cancelled
  (`release_replacement_debts_to`), not silently forgotten.
- A wrong elimination attempt draws a penalty card
  (`GameRoomManager.apply_penalty_draw`) and, if it was the guesser's own
  turn, ends it.
- Once a player calls Cambio, their hand is frozen: it can no longer be
  targeted by an elimination, a replacement, or a swap ability, for the rest
  of the round.

The backend validates card indices and ranks for every elimination attempt;
there is no attempt limit or turn restriction by design - deliberate,
off-turn eliminations are an intended and encouraged part of strategy.

## Cambio and Scoring

A player may call Cambio at the start of their turn, before drawing
(`GameRoomManager.perform_cambio_call`, shared by the human message handler
and the bot). After that:

1. The caller's hand becomes frozen and immune to swaps/eliminations for the
   rest of the round.
2. Every other player gets one final turn (`next_turn` counts down
   `final_round_turns = len(players) - 1`; the caller never gets another
   turn).
3. The room enters a short grace period for last eliminations
   (`start_grace_period`).
4. Scores are tallied (`tally_scores`) and the lowest score wins.
5. Equal scores use fewer remaining cards, then Cambio-caller priority.
6. Any unresolved tie enters an interactive revealed-card draw-off
   (`draw_tiebreak_card`).

## Reconnection

A dropped connection is not treated as leaving the game. When a player's
socket closes, `GameRoomManager.mark_player_disconnected` flags them
`is_connected = False` (broadcast as `player_disconnected`) and
`schedule_disconnect_grace` starts a `DISCONNECT_GRACE_PERIOD_SECONDS` (90s)
timer (`disconnect_grace_tasks`). Their `Player` row, hand, and all pending
state stay in `room.players` for the whole grace window.

- If the same `player_id` rejoins the room (the WebSocket join handshake
  re-attaches to the existing `Player` row instead of creating a new one)
  before the timer fires, `cancel_disconnect_grace` cancels it and a
  `player_reconnected` message is broadcast.
- If the timer expires first, `_expire_disconnect_grace` calls the same
  `remove_player_from_game` used by a deliberate "Leave Room" - the player is
  permanently removed, turn order and any owed replacements are cleaned up,
  and the room collapses/ends the game if only one player remains.

The frontend supports this with `sessionStorage` (`saveSession` /
`loadSession` / `clearSession` in `Frontend/bridge.js`) so a same-tab refresh
or a dropped connection can silently rejoin the same room and player without
the user re-entering anything; `scheduleReconnect` retries the WebSocket
connection with backoff. A deliberate "Leave Room" click sets
`intentionalDisconnect = true` and clears the saved session, so it is never
mistaken for a drop worth reconnecting from. A stale session pointing at a
room the server no longer has (e.g. after a restart) surfaces as a normal
`error` message and the client falls back to the lobby.

## Practice Bot

Practice mode adds one bot player to the room (`add_bot_to_room`). Bot turns
run in `GameRoomManager.run_bot_turn`, scheduled by `schedule_bot_turn`
whenever it becomes a bot's turn. The bot:

- Pauses between visible actions (`_bot_sleep`) so humans can react.
- Calls Cambio at the start of its turn when its hand total is low enough
  (`_bot_should_call_cambio`), via the same `perform_cambio_call` humans use.
- Takes a useful discard-pile card, or keeps a deck draw that improves its
  hand (`_bot_should_take_discard`, `_bot_should_swap_drawn_card`), always
  swapping out its own highest-value card (`_bot_worst_card_index`).
- Uses the ability of a card it discards instead of wasting it
  (`_bot_use_pending_ability`, sharing `resolve_card_ability` and
  `resolve_pending_swap_decision` with the human code paths): peeks to learn
  a card, remembers it, and only takes a blind/look-and-swap trade that is a
  confirmed or likely upgrade (`_bot_plan_swap`, `_bot_wants_swap`).
- Can eliminate its own matching card (`_bot_eliminate_own_matching_card`).

The bot's opponent-card knowledge is a best-effort memory
(`GameRoomManager.bot_opponent_memory`, keyed by `(room_id, bot_id)`) built
from what it has actually peeked at or looked at via its own ability uses -
not full visibility into other hands. A slot's memory is only ever trusted
if that slot is still occupied when read, so a card eliminated since being
memorized just drops out of consideration; a card *swapped* into that slot by
someone else can leave the bot's memory stale, the same imperfect recall a
human player would have. Memory is cleared on a fresh deal
(`start_game` calls `_clear_bot_memory_for_room`) and pruned when a player
leaves (`_forget_bot_memory_of_player`).

The bot does still read its own hand's true values directly rather than
tracking what it has "seen" of its own cards - it exists to give players a
reasonably competent opponent to learn against, not to model imperfect
self-recall.

## Client Responsibilities

`Frontend/bridge.js` owns browser-side behavior:

- Creating and joining rooms, including session persistence and automatic
  reconnection (see Reconnection above).
- Opening and maintaining the WebSocket connection (`setupWebSocket`) and
  routing every server message by `type` in `handleSocketMessage`.
- Rendering room state (`renderBoard` and friends).
- Handling draw, swap, ability, Cambio, and elimination interactions, and
  sending the matching message type via `sendMessage`.
- Showing animations, notifications, turn timers, and score results.
- Pre-filling direct join links such as `/join/ABC123`.

The backend remains authoritative for all game state and validation - the
frontend never decides whether a move is legal, it just reflects what the
server broadcasts back.

## Code Map (for review)

A quick index from "what the player does" to "what runs," for anyone
reviewing changes without wanting to grep the whole file first.

| Player action | WebSocket message type | Backend entry point |
| --- | --- | --- |
| Draw from deck | `draw_card` | inline handler in `websocket_endpoint` |
| Draw from discard | `draw_from_discard` | inline handler in `websocket_endpoint` |
| Swap/discard a pending draw | `resolve_draw` | inline handler; discard path calls `get_card_ability` |
| Use a discard ability | `use_ability` | `GameRoomManager.resolve_card_ability` |
| Resolve a look-and-swap decision | `resolve_swap_decision` | `GameRoomManager.resolve_pending_swap_decision` |
| Skip a pending ability | `skip_ability` | inline handler in `websocket_endpoint` |
| Attempt an elimination | `eliminate_card` | inline handler; wrong guess calls `apply_penalty_draw` |
| Give an elimination replacement | `give_replacement` | inline handler in `websocket_endpoint` |
| Call Cambio | `call_cambio` | `GameRoomManager.perform_cambio_call` |
| Leave the room | `leave_room` | `GameRoomManager.remove_player_from_game` |
| Socket drops (not a deliberate leave) | connection close | `GameRoomManager.mark_player_disconnected` + `schedule_disconnect_grace` |
| Advance to the next player | (internal) | `GameRoomManager.end_turn` -> `next_turn` |
| A bot's whole turn | (internal, scheduled) | `GameRoomManager.run_bot_turn` |

All of the above message types are dispatched from one large `if`/`elif`
chain inside `websocket_endpoint` in `Backend/backend.py` - start there when
tracing a new message type end to end. The frontend's mirror of that switch
is `handleSocketMessage` in `Frontend/bridge.js`, keyed the same way by
`type`.
