#!/usr/bin/env python3
"""
Test leaderboard API endpoint
"""

import os
import sys
import requests
import json

def test_leaderboard_api():
    """Test leaderboard API endpoint"""
    print("=== TEST LEADERBOARD API ===")
    
    try:
        response = requests.get("http://127.0.0.1:5001/progression/api/leaderboard")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response successful")
            print(f"Success: {data.get('success')}")
            
            leaderboard = data.get('leaderboard', [])
            print(f"Total users: {len(leaderboard)}")
            
            print("\n=== TOP 3 LEADERBOARD ===")
            for user in leaderboard[:3]:
                print(f"#{user['rank']} {user['username']}")
                print(f"   Display: {user['display_name']}")
                print(f"   Level {user['level']} - {user['points']} points")
                print(f"   Rank Type: {user['rank_type_display']}")
                print("")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_leaderboard_api()