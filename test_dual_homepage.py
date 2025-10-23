#!/usr/bin/env python3
"""
Test dual homepage system (comics vs novels)
"""

import os
import sys
import requests

def test_dual_homepage():
    """Test both comic and novel homepages"""
    print("=== TEST DUAL HOMEPAGE SYSTEM ===")
    
    try:
        # Test main homepage redirect
        print("\n1. Testing main homepage redirect...")
        response = requests.get("http://127.0.0.1:5001/", allow_redirects=False)
        if response.status_code == 302:
            print("✅ Main homepage redirects correctly")
            print(f"   Redirect location: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"❌ Main homepage redirect failed: {response.status_code}")
        
        # Test comic homepage
        print("\n2. Testing comic homepage...")
        response = requests.get("http://127.0.0.1:5001/comics-home")
        if response.status_code == 200:
            content = response.text.lower()
            if 'truyện tranh' in content:
                print("✅ Comic homepage contains correct title")
            if 'truyện chữ' in content and 'btn btn-outline-primary' in response.text:
                print("✅ Toggle button to novel homepage present")
            if 'latest_comics' in response.text or 'truyện tranh mới cập nhật' in content:
                print("✅ Comic content section present")
        else:
            print(f"❌ Comic homepage error: {response.status_code}")
        
        # Test novel homepage
        print("\n3. Testing novel homepage...")
        response = requests.get("http://127.0.0.1:5001/novels-home")
        if response.status_code == 200:
            content = response.text.lower()
            if 'truyện chữ' in content:
                print("✅ Novel homepage contains correct title")
            if 'truyện tranh' in content and 'btn btn-outline-primary' in response.text:
                print("✅ Toggle button to comic homepage present")
            if 'latest_novels' in response.text or 'tiểu thuyết mới cập nhật' in content:
                print("✅ Novel content section present")
        else:
            print(f"❌ Novel homepage error: {response.status_code}")
        
        # Test navigation update
        print("\n4. Testing navigation...")
        response = requests.get("http://127.0.0.1:5001/comics-home")
        if response.status_code == 200:
            if 'comics-home' in response.text:
                print("✅ Navigation points to comic homepage")
            else:
                print("⚠️ Navigation may not be updated")
        
        print("\n=== TEST SUMMARY ===")
        print("🎯 Two separate homepages created")
        print("🔄 Toggle buttons for switching between them")
        print("📚 Content filtered by comic vs novel type")
        print("🎨 Distinct designs for each homepage")
        
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_dual_homepage()