#!/usr/bin/env python3
"""
Test script to verify leaderboard frontend functionality
"""
import requests
import time

def test_leaderboard_page():
    """Test if leaderboard page loads correctly"""
    try:
        # Test main page
        response = requests.get('http://127.0.0.1:5001/progression/stats', timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # Check for new leaderboard elements
            checks = [
                ('switchTimePeriod', 'JavaScript function switchTimePeriod found'),
                ('switchContentType', 'JavaScript function switchContentType found'),
                ('Top Tháng', 'Top Tháng tab found'),
                ('Top Tuần', 'Top Tuần tab found'),
                ('Top Ngày', 'Top Ngày tab found'),
                ('Truyện Tranh', 'Truyện Tranh toggle found'),
                ('Truyện Chữ', 'Truyện Chữ toggle found'),
                ('leaderboard-content', 'Leaderboard content container found'),
                ('tab-pane fade show active', 'Active tab pane found')
            ]
            
            for check, message in checks:
                if check in content:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
            
            print(f"\n📄 Page length: {len(content)} characters")
            
        else:
            print(f"❌ Page failed to load: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing page: {e}")

def test_api_endpoints():
    """Test API endpoints"""
    endpoints = [
        ('month', 'comics'),
        ('week', 'comics'),
        ('day', 'comics'),
        ('month', 'novels'),
        ('week', 'novels'),
        ('day', 'novels')
    ]
    
    print("\n🔗 Testing API Endpoints:")
    for period, content_type in endpoints:
        try:
            url = f'http://127.0.0.1:5001/progression/api/leaderboard?period={period}&content_type={content_type}'
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    count = len(data.get('leaderboard', []))
                    print(f"✅ {period.title()} {content_type.title()}: {count} users")
                else:
                    print(f"❌ {period.title()} {content_type.title()}: API returned success=false")
            else:
                print(f"❌ {period.title()} {content_type.title()}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {period.title()} {content_type.title()}: {e}")

if __name__ == "__main__":
    print("🧪 Testing Leaderboard Frontend & API")
    print("=" * 50)
    
    test_leaderboard_page()
    test_api_endpoints()
    
    print("\n🎯 Test Complete!")