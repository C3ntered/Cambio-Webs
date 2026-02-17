from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load local index.html
        cwd = os.getcwd()
        file_path = f"file://{cwd}/Frontend/index.html"
        page.goto(file_path)

        # Inject CSS to make game board visible
        page.add_style_tag(content="#game-board { display: block !important; }")

        # Inject HTML for Opponent Cards (Testing CSS styles)
        # We create a button that mimics an opponent card
        opponent_html = """
        <div class="opponent-cards" style="display: flex; gap: 10px; padding: 20px;">
            <!-- Face Down Card -->
            <button class="card-back" style="margin: 5px;">🂠</button>

            <!-- Face Up Card (Ace of Spades) -->
            <button style="margin: 5px;">
                <div class="card-corner-top" style="font-size: 20px;">
                    <span>A</span><span>♠</span>
                </div>
                <div class="card-center" style="font-size: 48px;">♠</div>
            </button>
        </div>
        """
        page.evaluate(f"document.getElementById('opponents-container').innerHTML = '{opponent_html.replace(chr(10), "")}'")

        # Inject HTML for Discard Pile (Testing JS-like inline styles)
        # We simulate what bridge.js produces
        discard_html = """
        <div class="card-display" style="width: 100px; height: 140px; border: 2px solid #333; border-radius: 8px; background-color: white; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 5px; font-weight: bold; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); position: relative;">
            <div class="card-corner-top" style="font-size: 20px;">
                <span>K</span><span>♥</span>
            </div>
            <div class="card-center" style="font-size: 48px;">♥</div>
        </div>
        """
        page.evaluate(f"document.getElementById('top-card').innerHTML = '{discard_html.replace(chr(10), "")}'")

        # Take screenshot
        page.screenshot(path="verification/cards_test.png")
        print("Screenshot saved to verification/cards_test.png")

        browser.close()

if __name__ == "__main__":
    run()
