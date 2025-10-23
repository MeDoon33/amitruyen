#!/usr/bin/env python3
"""
Test script for both user and comic rankings
"""
import requests

def test_rankings():
    """Test both ranking systems"""
    session = requests.Session()
    
    # Login for user ranking test
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        # Test comic ranking (public)
        print("🎯 Testing Comic Ranking...")
        comic_response = session.get('http://127.0.0.1:5001/api/comic-ranking?period=all&type=all')
        if comic_response.status_code == 200:
            data = comic_response.json()
            if data.get('success'):
                print(f"✅ Comic ranking API: {len(data['comics'])} comics")
                if data['comics']:
                    print(f"   Top comic: {data['comics'][0]['title']} ({data['comics'][0]['views']} views)")
            else:
                print("❌ Comic ranking API returned error")
        else:
            print(f"❌ Comic ranking API failed: {comic_response.status_code}")
        
        # Test comic ranking page
        page_response = session.get('http://127.0.0.1:5001/ranking/comics')
        if page_response.status_code == 200:
            print("✅ Comic ranking page loads successfully")
        else:
            print(f"❌ Comic ranking page failed: {page_response.status_code}")
        
        print("\n👤 Testing User Ranking...")
        # Login
        login_response = session.post('http://127.0.0.1:5001/auth/login', data=login_data)
        if login_response.status_code == 200:
            print("✅ Login successful")
            
            # Test user ranking API
            user_response = session.get('http://127.0.0.1:5001/progression/api/leaderboard?period=month&content_type=comics')
            if user_response.status_code == 200:
                data = user_response.json()
                if data.get('success'):
                    print(f"✅ User ranking API: {len(data['leaderboard'])} users")
                    if data['leaderboard']:
                        print(f"   Top user: {data['leaderboard'][0]['username']} ({data['leaderboard'][0]['points']} points)")
                else:
                    print("❌ User ranking API returned error")
            else:
                print(f"❌ User ranking API failed: {user_response.status_code}")
            
            # Test user ranking page
            stats_response = session.get('http://127.0.0.1:5001/progression/stats')
            if stats_response.status_code == 200:
                print("✅ User ranking page loads successfully")
            else:
                print(f"❌ User ranking page failed: {stats_response.status_code}")
        else:
            print("❌ Login failed")
        
        print("\n🌐 Testing Navigation...")
        # Test main page with new dropdown
        main_response = session.get('http://127.0.0.1:5001/comics-home')
        if main_response.status_code == 200:
            content = main_response.text
            if 'Bảng Xếp Hạng' in content and 'dropdown-toggle' in content:
                print("✅ Navigation dropdown found")
            else:
                print("❌ Navigation dropdown missing")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Both Ranking Systems")
    print("=" * 50)
    test_rankings()
    print("\n🎯 Test Complete!")
    print("\n📋 Summary:")
    print("- Comic Ranking: /ranking/comics (public)")
    print("- User Ranking: /progression/stats (requires login)")
    print("- Both accessible via 'Bảng Xếp Hạng' dropdown in nav")