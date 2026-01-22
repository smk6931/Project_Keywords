
import requests
from bs4 import BeautifulSoup
import time

def test_signal_bz():
    url = "https://www.signal.bz/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Testing Signal.bz connection to: {url}")
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=10)
        conn_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Connection Time: {conn_time:.2f}s")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Original Logic
            ranks = soup.select(".rank-text")
            print(f"Found {len(ranks)} items with class '.rank-text'")
            
            if ranks:
                print("--- Top 5 Keywords ---")
                for i, rank in enumerate(ranks[:5]):
                    print(f"{i+1}. {rank.text.strip()}")
            else:
                print("❌ No items found with '.rank-text'. Structure might have changed.")
                # Fallback check - print some html to debug
                print("--- HTML Snippet (First 500 chars) ---")
                print(soup.prettify()[:500])
                
                # Check for other potential classes just in case
                print("\nChecking alternatives...")
                candidates = soup.find_all(['span', 'div', 'a'], limit=50)
                for c in candidates:
                    if c.text.strip():
                        # print useful looking text nodes
                        pass
        else:
            print("❌ Failed to retrieve page.")

    except Exception as e:
        print(f"❌ Error during request: {e}")

if __name__ == "__main__":
    test_signal_bz()
