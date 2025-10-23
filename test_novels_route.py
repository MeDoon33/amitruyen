#!/usr/bin/env python3
"""
Test novels route and navigation changes
"""

import os
import sys
import requests

def test_novels_route():
    """Test novels route functionality"""
    print("=== TEST NOVELS ROUTE ===")
    
    try:
        # Test novels route
        response = requests.get("http://127.0.0.1:5001/comics/novels")
        
        if response.status_code == 200:
            print("✅ Novels route accessible")
            
            # Check if response contains novel-related content
            content = response.text.lower()
            if 'tiểu thuyết' in content:
                print("✅ Novel page contains correct title")
            else:
                print("❌ Novel page missing title")
                
            if 'tìm kiếm tiểu thuyết' in content:
                print("✅ Search functionality present")
            else:
                print("⚠️ Search functionality may be missing")
                
        else:
            print(f"❌ Novels route error: {response.status_code}")
            
        # Test main page navigation
        response = requests.get("http://127.0.0.1:5001/")
        if response.status_code == 200:
            content = response.text
            if 'Tiểu Thuyết' in content:
                print("✅ Navigation bar contains 'Tiểu Thuyết' tab")
            else:
                print("❌ Navigation bar missing 'Tiểu Thuyết' tab")
                
            # Check if removed elements are gone
            if 'Fanpage' not in content:
                print("✅ Fanpage removed from navigation")
            else:
                print("❌ Fanpage still present in navigation")
                
            if 'Đăng Xuất' not in content and 'Cấp' not in content:
                print("✅ Level and logout elements removed")
            else:
                print("⚠️ Some elements may still be present (depends on login status)")
        
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_novels_route()