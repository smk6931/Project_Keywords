
import requests

def check_reddit_trends():
    url = "https://www.reddit.com/r/popular/top.json?limit=10&t=day"
    print(f"Checking {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'} 
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            posts = data['data']['children']
            print(f"Found {len(posts)} posts from Reddit Popular:")
            for post in posts[:3]:
                print(f"- {post['data']['title']}")
        else:
            print(f"Reddit Failed: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_reddit_trends()
