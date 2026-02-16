from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the file
        file_path = f"file://{os.getcwd()}/Frontend/index.html"
        print(f"Loading: {file_path}")
        page.goto(file_path)

        # 1. Verify Waiting Mode
        print("Verifying Waiting Mode...")
        page.evaluate("""
            const mockRoom = {
                room_id: 'TEST1',
                status: 'waiting',
                players: [
                    {player_id: 'p1', username: 'Player1', is_connected: true},
                    {player_id: 'p2', username: 'Player2', is_connected: true}
                ],
                max_players: 4,
                min_players: 2
            };
            renderBoard(mockRoom, 'p1');
        """)

        # Take screenshot of Waiting Mode
        page.wait_for_timeout(1000); page.screenshot(path="verification/waiting_mode.png")
        print("Screenshot saved: verification/waiting_mode.png")

        # 2. Verify Playing Mode
        print("Verifying Playing Mode...")
        page.evaluate("""
            const mockRoomPlaying = {
                room_id: 'TEST1',
                status: 'playing',
                players: [
                    {
                        player_id: 'p1',
                        username: 'Player1',
                        is_connected: true,
                        hand: [
                            {rank: 'A', suit: 'S', is_face_up: false},
                            {rank: 'K', suit: 'H', is_face_up: false},
                            {rank: 'Q', suit: 'D', is_face_up: false},
                            {rank: 'J', suit: 'C', is_face_up: false}
                        ]
                    },
                    {
                        player_id: 'p2',
                        username: 'Player2',
                        is_connected: true,
                        hand: [
                            {rank: '2', suit: 'S', is_face_up: false},
                            {rank: '3', suit: 'H', is_face_up: false},
                            {rank: '4', suit: 'D', is_face_up: false},
                            {rank: '5', suit: 'C', is_face_up: false}
                        ]
                    }
                ],
                game_state: {
                    turn_player_id: 'p1',
                    top_card: {rank: '5', suit: 'H'},
                    discard_pile: []
                }
            };
            renderBoard(mockRoomPlaying, 'p1');
        """)

        # Take screenshot of Playing Mode
        page.wait_for_timeout(1000); page.screenshot(path="verification/playing_mode.png")
        print("Screenshot saved: verification/playing_mode.png")

        browser.close()

if __name__ == "__main__":
    run()
