from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        file_path = f"file://{os.getcwd()}/Frontend/index.html"
        print(f"Loading: {file_path}")
        page.goto(file_path)

        # Inject mock room (Playing)
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

        # Check layout elements
        # Opponents Top
        opponents = page.locator('#opponents-hands')
        play_area = page.locator('#play-area')
        my_hand = page.locator('#my-hand')

        print(f"Opponents Visible: {opponents.is_visible()}")
        print(f"Play Area Visible: {play_area.is_visible()}")
        print(f"My Hand Visible: {my_hand.is_visible()}")

        # Check CSS flex direction
        direction = page.locator('#game-elements').evaluate("el => getComputedStyle(el).flexDirection")
        print(f"Flex Direction: {direction}")

        if direction != 'column':
            print("FAILED: Flex direction is not column")

        page.screenshot(path="verification/compact_layout.png")
        print("Screenshot saved")

        browser.close()

if __name__ == "__main__":
    run()
