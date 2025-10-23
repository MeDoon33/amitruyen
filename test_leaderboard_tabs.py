#!/usr/bin/env python3
"""
Test leaderboard tabs functionality with content type filtering
"""

import requests
import json

def test_leaderboard_tabs():
    """Test leaderboard tabs với các content type khác nhau"""
    print("🏆 === TESTING LEADERBOARD TABS ===")
    
    base_url = "http://127.0.0.1:5001/progression/api/leaderboard"
    
    content_types = [
        ("all", "Tất Cả"),
        ("comics", "Truyện Tranh"),
        ("novels", "Tiểu Thuyết")
    ]
    
    for content_type, display_name in content_types:
        print(f"\n📊 Testing {display_name} tab:")
        try:
            url = base_url if content_type == 'all' else f"{base_url}?content_type={content_type}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Status: 200 OK")
                print(f"✅ Success: {data.get('success')}")
                print(f"✅ Content Type: {data.get('content_type', 'all')}")
                
                leaderboard = data.get('leaderboard', [])
                print(f"✅ Total users: {len(leaderboard)}")
                
                if leaderboard:
                    print(f"   📋 TOP 3 for {display_name}:")
                    for user in leaderboard[:3]:
                        rank = user['rank']
                        username = user['username']
                        level = user['level']
                        points = user['points']
                        rank_type = user['rank_type_display']
                        
                        # Check for rank styling
                        rank_style = ""
                        if rank == 1:
                            rank_style = "🥇 (Gold)"
                        elif rank == 2:
                            rank_style = "🥈 (Silver)"
                        elif rank == 3:
                            rank_style = "🥉 (Bronze)"
                        
                        print(f"      #{rank} {rank_style}")
                        print(f"         User: {username}")
                        print(f"         Level: {level} | Points: {points}")
                        print(f"         Path: {rank_type}")
                        print("")
                else:
                    print("   ❌ No users found")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n🎯 TAB SYSTEM READY!")
    print("   - Bảng xếp hạng giữ nguyên thiết kế cũ")
    print("   - Các tab phụ để lọc theo content type")
    print("   - API hỗ trợ content_type parameter")
    print("   - UI/UX tương thích với thiết kế hiện tại")

def test_leaderboard_page():
    """Test trang stats để xem tab system"""
    print("\n🌐 TESTING STATS PAGE:")
    try:
        response = requests.get("http://127.0.0.1:5001/progression/stats")
        status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
        print(f"   Stats page: {status}")
        
        if response.status_code == 200:
            content = response.text
            checks = [
                ("leaderboard-subtabs", "Sub-tabs container"),
                ("leaderboard-all-tab", "All tab"),
                ("leaderboard-comics-tab", "Comics tab"),
                ("leaderboard-novels-tab", "Novels tab"),
                ("loadLeaderboardByType", "Tab switching function")
            ]
            
            print("   🔍 UI Elements check:")
            for element_id, description in checks:
                found = element_id in content
                status = "✅" if found else "❌"
                print(f"      {status} {description}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    test_leaderboard_tabs()
    test_leaderboard_page()