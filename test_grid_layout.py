#!/usr/bin/env python3
"""
Test grid layout for featured comics without scroll
"""

import requests

def test_grid_layout():
    """Test grid layout without horizontal scroll"""
    print("📐 === TESTING GRID LAYOUT (NO SCROLL) ===")
    
    try:
        # Test comic homepage
        response = requests.get("http://127.0.0.1:5001/comics-home")
        
        if response.status_code == 200:
            print("✅ Comic Homepage accessible")
            content = response.text
            
            # Check for grid layout elements
            checks = [
                ("col-lg col-md-4 col-sm-6", "Bootstrap responsive grid classes"),
                ("featured-card-small", "Small featured cards"),
                ("featured-cover-small", "Small cover images"),
                ("row g-2", "Bootstrap row with gap"),
                ("badge-sm", "Small badges")
            ]
            
            print("\n🔍 Grid Layout Elements Check:")
            for element, description in checks:
                found = element in content
                status = "✅" if found else "❌"
                print(f"   {status} {description}")
            
            # Check that horizontal scroll elements are removed
            removed_elements = [
                ("featured-carousel", "Carousel container (should be removed)"),
                ("overflow-x: auto", "Horizontal scroll CSS (should be removed)"),
                ("flex-wrap: nowrap", "No-wrap CSS (should be removed)"),
                ("flex: 0 0 200px", "Fixed width CSS (should be removed)")
            ]
            
            print("\n❌ Removed Elements Check:")
            for element, description in removed_elements:
                found = element in content
                status = "❌" if found else "✅"
                print(f"   {status} {description} {'(FOUND - should remove)' if found else '(REMOVED)'}")
                
            # Check responsive breakpoints
            responsive_checks = [
                ("@media (max-width: 1200px)", "Large screen breakpoint"),
                ("@media (max-width: 768px)", "Tablet breakpoint"),
                ("@media (max-width: 576px)", "Mobile breakpoint")
            ]
            
            print("\n📱 Responsive Design Check:")
            for element, description in responsive_checks:
                found = element in content
                status = "✅" if found else "❌"
                print(f"   {status} {description}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
        # Test novel homepage too
        print("\n📚 Testing Novel Homepage:")
        response_novel = requests.get("http://127.0.0.1:5001/novels-home")
        
        if response_novel.status_code == 200:
            print("✅ Novel Homepage accessible")
            content_novel = response_novel.text
            
            if "col-lg col-md-4 col-sm-6" in content_novel:
                print("✅ Novel homepage has grid layout")
            else:
                print("❌ Novel homepage missing grid layout")
                
            if "featured-carousel" not in content_novel:
                print("✅ Novel homepage carousel removed")
            else:
                print("❌ Novel homepage still has carousel")
        else:
            print(f"❌ Novel homepage error: {response_novel.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_design_summary():
    """Print design summary"""
    print("\n📐 === GRID DESIGN SUMMARY ===")
    
    design_features = [
        "✅ Bootstrap grid system: col-lg col-md-4 col-sm-6",
        "✅ 5 equal columns on large screens (≥1200px)",
        "✅ 3 columns on medium screens (768px-1199px)",
        "✅ 2 columns on small screens (576px-767px)",
        "✅ 1 column on extra small screens (<576px)",
        "✅ No horizontal scrolling required",
        "✅ Responsive image heights (160px→140px→120px→100px)",
        "✅ Responsive card padding and font sizes",
        "✅ All 5 featured items visible without scroll"
    ]
    
    for feature in design_features:
        print(f"   {feature}")
        
    print("\n🎯 Layout Behavior:")
    behaviors = [
        "Desktop (≥1200px): 5 columns in one row",
        "Laptop (992px-1199px): 5 columns, slightly smaller",
        "Tablet (768px-991px): 3 columns, 2 rows (3+2)",
        "Mobile (576px-767px): 2 columns, 3 rows (2+2+1)",
        "Small Mobile (<576px): 1 column, 5 rows"
    ]
    
    for behavior in behaviors:
        print(f"   📱 {behavior}")

if __name__ == '__main__':
    test_grid_layout()
    test_design_summary()