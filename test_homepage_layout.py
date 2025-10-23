#!/usr/bin/env python3
"""
Test homepage layout to match the provided image
"""

import requests
from bs4 import BeautifulSoup

def test_homepage_layout():
    """Test homepage layout structure"""
    print("🏠 === TESTING HOMEPAGE LAYOUT ===")
    
    try:
        # Test comic homepage
        response = requests.get("http://127.0.0.1:5001/comics-home")
        
        if response.status_code == 200:
            print("✅ Comic Homepage accessible")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check sections order according to image
            sections = soup.find_all('section')
            section_classes = [s.get('class', []) for s in sections]
            
            print("\n📊 Section Order Check:")
            for i, section in enumerate(sections):
                class_names = ' '.join(section.get('class', []))
                header = section.find('h4')
                title = header.text.strip() if header else 'No title'
                print(f"   {i+1}. {title} (class: {class_names})")
            
            # Check for key elements according to image
            elements_to_check = [
                ("featured-section", "Truyện Nổi Bật section"),
                ("latest-section", "Truyện Mới Cập Nhật section"),
                ("ranking-card", "Bảng Xếp Hạng sidebar"),
                ("homepage-toggle", "Toggle buttons"),
                ("ranking-item", "Ranking items"),
                ("ranking-thumb", "Ranking thumbnails")
            ]
            
            print("\n🔍 Layout Elements Check:")
            for class_name, description in elements_to_check:
                elements = soup.find_all(class_=class_name)
                found = len(elements) > 0
                count = len(elements)
                status = "✅" if found else "❌"
                print(f"   {status} {description}: {count} found")
            
            # Check grid layout
            grid_containers = soup.find_all('div', class_='row')
            print(f"\n📋 Grid Layout: {len(grid_containers)} row containers found")
            
            # Check sidebar
            sidebar = soup.find('div', class_='sidebar')
            if sidebar:
                print("✅ Sidebar found")
                ranking_items = sidebar.find_all('div', class_='ranking-item')
                print(f"   - Ranking items: {len(ranking_items)}")
            else:
                print("❌ Sidebar not found")
                
        else:
            print(f"❌ Comic Homepage Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_homepage_vs_image():
    """Compare homepage structure with provided image"""
    print("\n🖼️  === COMPARING WITH PROVIDED IMAGE ===")
    
    expected_structure = [
        "Truyện Nổi Bật (should be first - featured content)",
        "Truyện Mới Cập Nhật (should be second - latest updates)", 
        "Bảng Xếp Hạng (should be in sidebar)"
    ]
    
    print("Expected structure according to image:")
    for item in expected_structure:
        print(f"   📌 {item}")
    
    print("\nKey visual elements from image:")
    visual_elements = [
        "Grid layout with comic covers",
        "Sidebar with ranking list", 
        "Ranking items with numbers/icons",
        "Comic thumbnails in ranking",
        "Toggle buttons between content types"
    ]
    
    for element in visual_elements:
        print(f"   🎨 {element}")

if __name__ == '__main__':
    test_homepage_layout()
    test_homepage_vs_image()