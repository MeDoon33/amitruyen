#!/usr/bin/env python3
"""
Test script with login session
"""
import requests

def test_with_login():
    """Test leaderboard with login session"""
    session = requests.Session()
    
    # Login first
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        # Attempt login
        login_response = session.post('http://127.0.0.1:5001/auth/login', data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # Test leaderboard page
            stats_response = session.get('http://127.0.0.1:5001/progression/stats')
            print(f"Stats page status: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                content = stats_response.text
                
                # Check for new elements
                checks = [
                    'switchTimePeriod',
                    'switchContentType', 
                    'Top Tháng',
                    'leaderboard-content',
                    'tab-btn active'
                ]
                
                for check in checks:
                    if check in content:
                        print(f"✅ Found: {check}")
                    else:
                        print(f"❌ Missing: {check}")
                        
                print(f"\nContent length: {len(content)} chars")
            else:
                print("❌ Failed to load stats page")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_login()