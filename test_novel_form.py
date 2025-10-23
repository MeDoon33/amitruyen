"""
Test the novel chapter form rendering
"""
import requests

base_url = 'http://127.0.0.1:5001'

print("\n=== Testing Novel Chapter Form ===\n")

# Test 1: Check if the add chapter page uses the correct template for novels
print("1. Testing Add Novel Chapter Form")
try:
    # This requires authentication, but we can at least check if the route exists
    response = requests.get(f'{base_url}/admin/comic/11/add_chapter', timeout=5, allow_redirects=False)
    
    if response.status_code == 302:
        print(f"   ✓ Route exists (redirected to login as expected)")
        print(f"   Redirect to: {response.headers.get('Location')}")
    elif response.status_code == 200:
        print(f"   ✓ Page loaded successfully")
        # Check if it's the novel form (should have 'content' textarea)
        if 'name="content"' in response.text:
            print(f"   ✓ Novel form detected (has content textarea)")
        elif 'name="image_urls"' in response.text:
            print(f"   ❌ ERROR: Comic form detected (has image_urls)")
        else:
            print(f"   ⚠️  Unknown form type")
    else:
        print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Check the novel reading page
print("\n2. Testing Novel Chapter Reading Page")
try:
    response = requests.get(f'{base_url}/comic/11/chapter/1.0', timeout=5)
    
    if response.status_code == 200:
        print(f"   ✓ Chapter page loaded successfully")
        
        # Check if it's displaying as novel format
        page_text = response.text
        if 'Chương Test - Khởi Đầu' in page_text:
            print(f"   ✓ Chapter title found")
        if 'Chương này là chương test' in page_text:
            print(f"   ✓ Chapter content found")
        if 'chapter-content' in page_text:
            print(f"   ✓ Novel styling detected")
    else:
        print(f"   ❌ Error: Status code {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check comic detail page shows the chapter
print("\n3. Testing Novel Detail Page")
try:
    response = requests.get(f'{base_url}/comic/11', timeout=5)
    
    if response.status_code == 200:
        print(f"   ✓ Detail page loaded successfully")
        
        if 'Chương Test - Khởi Đầu' in response.text or 'Chương 1' in response.text:
            print(f"   ✓ Chapter appears in chapter list")
        else:
            print(f"   ⚠️  Chapter not found in list")
    else:
        print(f"   ❌ Error: Status code {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n=== Test Complete ===\n")
print("To test the form manually:")
print("1. Login as admin/uploader")
print("2. Go to: http://127.0.0.1:5001/admin/comic/11/add_chapter")
print("3. You should see a form with 'Nội Dung Chương' textarea (not 'Image URLs')")
