"""
Simple test to verify comics and novels are properly separated
"""
import requests

base_url = 'http://127.0.0.1:5001'

print("\n=== Testing Comic/Novel Separation ===\n")

# Test 1: Comics homepage
print("1. Testing Comics Homepage (/comics-home)")
try:
    response = requests.get(f'{base_url}/comics-home', timeout=5)
    if response.status_code == 200:
        print(f"   ✓ Page loaded successfully")
        
        # Check if "Tiên Nghịch" (the novel) is on the page
        page_text = response.text.lower()
        if 'tiên nghịch' in page_text:
            print("   ❌ ERROR: Novel 'Tiên Nghịch' found on comics homepage!")
        else:
            print("   ✓ Novel 'Tiên Nghịch' NOT found on comics homepage (correct)")
    else:
        print(f"   ❌ Error: Status code {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Novels homepage
print("\n2. Testing Novels Homepage (/novels-home)")
try:
    response = requests.get(f'{base_url}/novels-home', timeout=5)
    if response.status_code == 200:
        print(f"   ✓ Page loaded successfully")
        
        # Check if "Tiên Nghịch" (the novel) is on the page
        page_text = response.text
        if 'Tiên Nghịch' in page_text:
            print("   ✓ Novel 'Tiên Nghịch' found on novels homepage (correct)")
        else:
            print("   ⚠️  Novel 'Tiên Nghịch' NOT found on novels homepage")
        
        # Check if any comic titles are on the page
        comic_titles = ['Solo Leveling', 'Phản Diện', 'Ta Có Một Sơn Trại']
        found_comics = []
        for title in comic_titles:
            if title.lower() in page_text.lower():
                found_comics.append(title)
        
        if found_comics:
            print(f"   ❌ ERROR: Comics found on novels homepage: {', '.join(found_comics)}")
        else:
            print("   ✓ No comics found on novels homepage (correct)")
    else:
        print(f"   ❌ Error: Status code {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: API ranking - Comics only
print("\n3. Testing API Ranking - Comics Only")
try:
    response = requests.get(f'{base_url}/api/comic-ranking?type=comics&period=all', timeout=5)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            comics = data.get('comics', [])
            print(f"   ✓ API returned {len(comics)} comics")
            
            # Check if any novel is in the results
            novel_found = False
            for comic in comics:
                if comic['title'] == 'Tiên Nghịch':
                    novel_found = True
                    break
            
            if novel_found:
                print("   ❌ ERROR: Novel found in comics-only API results!")
            else:
                print("   ✓ No novels in comics-only API results (correct)")
        else:
            print(f"   ❌ API error: {data.get('error')}")
    else:
        print(f"   ❌ Error: Status code {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: API ranking - Novels only
print("\n4. Testing API Ranking - Novels Only")
try:
    response = requests.get(f'{base_url}/api/comic-ranking?type=novels&period=all', timeout=5)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            novels = data.get('comics', [])
            print(f"   ✓ API returned {len(novels)} novels")
            
            # Check if Tiên Nghịch is in the results
            novel_found = False
            for novel in novels:
                if novel['title'] == 'Tiên Nghịch':
                    novel_found = True
                    print(f"   ✓ Novel 'Tiên Nghịch' found in novels API (correct)")
                    break
            
            if not novel_found and len(novels) > 0:
                print("   ⚠️  'Tiên Nghịch' not found in results")
        else:
            print(f"   ❌ API error: {data.get('error')}")
    else:
        print(f"   ❌ Error: Status code {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n=== Test Complete ===\n")
