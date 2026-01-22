
import requests
from bs4 import BeautifulSoup
import time

def test_signal_bz():
    url = "https://www.signal.bz/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Testing Signal.bz connection to: {url}", flush=True)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            ranks = soup.select(".rank-text")
            print(f"Found {len(ranks)} items with class '.rank-text'", flush=True)
            
            with open("signal_dump.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Saved HTML to signal_dump.html", flush=True)
            
            if len(ranks) == 0:
                print("FAIL: No keywords found with .rank-text", flush=True)
            else:
                for r in ranks[:3]:
                    print(f"Keyword: {r.text.strip()}", flush=True)

        else:
            print("FAIL: Status Code not 200", flush=True)

    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    test_signal_bz()
