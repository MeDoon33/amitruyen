import requests
import time

# Wait for server to start
time.sleep(1)

print("\n=== Testing Novel Chapter Reading ===\n")

# Test different URL formats
test_urls = [
    'http://127.0.0.1:5001/comics/11/chapter/1.0',
    'http://127.0.0.1:5001/comics/11/chapter/1',
    'http://127.0.0.1:5001/comic/11/chapter/1.0',
    'http://127.0.0.1:5001/comic/11/chapter/1',
]

for url in test_urls:
    try:
        response = requests.get(url, timeout=5)
        print(f"{url}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✓ SUCCESS!")
            if 'chapter-content' in response.text:
                print("  ✓ Novel content styling found")
            if 'Ly hương' in response.text or 'Chương Test' in response.text:
                print("  ✓ Chapter title found")
            break
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
