
import requests
from bs4 import BeautifulSoup

def check_nate_trends():
    url = "https://www.nate.com/js/data/jsonLiveKeywordDataV1.js?v=20250122" # Nate often uses JS/JSON for this
    # Or just main page scraping
    url_main = "https://www.nate.com/"
    print(f"Checking {url_main}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url_main, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Nate usually has a 'biz-rank' or 'isKeyword' section
            # Looking for class "isKeyword" or similar. 
            # Note: Nate structure changes, but let's try finding the logic.
            # In recent Nate, it's often in a script or specific div.
            
            # Try parsing metadata or known classes
            keywords = []
            # This selector is a guess based on typical structures, requires validation
            for item in soup.select('.isKeyword a'): 
                keywords.append(item.text.strip())
            
            if not keywords:
                # Fallback: check raw text for "실시간 이슈"
                print("CSS selector failed, dumping snippets...")
                print(res.text[:500])
            else:
                print(f"Found Nate Keywords: {keywords}")
        else:
            print("Failed to access Nate")
    except Exception as e:
        print(f"Error: {e}")

def check_zum_trends():
    url = "https://issue.zum.com/"
    print(f"Checking {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Zum Issue keywords
            keywords = []
            # Try finding rankings
            for item in soup.select('.ranking_list .cont a'):
                keywords.append(item.text.strip())
            
            if keywords:
                print(f"Found Zum Keywords: {keywords}")
            else:
                print("Zum selector failed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_nate_trends()
    check_zum_trends()
