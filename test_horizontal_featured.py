#!/usr/bin/env python3
"""
Test horizontal featured comics layout
"""

import requests

def test_horizontal_featured():
    """Test horizontal featured comics section"""
    print("🎨 === TESTING HORIZONTAL FEATURED LAYOUT ===")
    
    try:
        # Test comic homepage
        response = requests.get("http://127.0.0.1:5001/comics-home")
        
        if response.status_code == 200:
            print("✅ Comic Homepage accessible")
            content = response.text
            
            # Check for new horizontal layout elements
            checks = [
                ("featured-carousel", "Horizontal carousel container"),
                ("featured-card-small", "Small featured cards"),
                ("featured-cover-small", "Small cover images"),
                ("badge-sm", "Small badges"),
                ("col", "Column layout for 5 items"),
                ("g-3", "Bootstrap gap spacing")
            ]
            
            print("\n🔍 Layout Elements Check:")
            for element, description in checks:
                found = element in content
                status = "✅" if found else "❌"
                print(f"   {status} {description}")
            
            # Check for flex-wrap: nowrap in CSS
            if "flex-wrap: nowrap" in content:
                print("✅ Horizontal scrolling CSS found")
            else:
                print("❌ Horizontal scrolling CSS missing")
                
            # Check for responsive design
            if "@media (max-width: 768px)" in content:
                print("✅ Mobile responsive CSS found")
            else:
                print("❌ Mobile responsive CSS missing")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
        # Test novel homepage too
        print("\n📚 Testing Novel Homepage:")
        response_novel = requests.get("http://127.0.0.1:5001/novels-home")
        
        if response_novel.status_code == 200:
            print("✅ Novel Homepage accessible")
            content_novel = response_novel.text
            
            if "featured-carousel" in content_novel:
                print("✅ Novel homepage has horizontal layout")
            else:
                print("❌ Novel homepage missing horizontal layout")
        else:
            print(f"❌ Novel homepage error: {response_novel.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_design_summary():
    """Print design summary"""
    print("\n📐 === DESIGN SUMMARY ===")
    
    design_features = [
        "✅ Horizontal row with 5 featured comics/novels",
        "✅ Smaller card size (200px width, 180px height covers)",
        "✅ Horizontal scrolling on mobile",
        "✅ Hover effects with red/green shadows",
        "✅ Small badges for better space utilization",
        "✅ Responsive design (150px on mobile)",
        "✅ Cards maintain aspect ratio",
        "✅ Smooth transitions and animations"
    ]
    
    for feature in design_features:
        print(f"   {feature}")
        
    print("\n🎯 Benefits:")
    benefits = [
        "More space efficient - 5 items in one row",
        "Better visual hierarchy - featured content stands out",
        "Mobile friendly with horizontal scroll",
        "Consistent design between comics and novels",
        "Easy scanning of featured content"
    ]
    
    for benefit in benefits:
        print(f"   📌 {benefit}")

if __name__ == '__main__':
    test_horizontal_featured()
    test_design_summary()