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

        # Inject HTML for Opponent Cards
        opponent_html = """
        <div class="opponent-cards">
            <button id="opp-card-1">A♠</button>
        </div>
        """
        page.evaluate(f"document.getElementById('opponents-container').innerHTML = '{opponent_html.replace(chr(10), "")}'")

        # Get computed style
        card = page.locator("#opp-card-1")
        width = card.evaluate("el => window.getComputedStyle(el).width")
        height = card.evaluate("el => window.getComputedStyle(el).height")

        print(f"Opponent Card Width: {width}")
        print(f"Opponent Card Height: {height}")

        if width != "100px" or height != "140px":
            print("FAIL: Opponent card dimensions incorrect.")
            exit(1)

        print("PASS: Opponent card dimensions correct.")
        browser.close()

if __name__ == "__main__":
    run()
