#!/usr/bin/env python3
"""
Test 5-column horizontal layout for featured comics
"""

import requests

def test_five_column_layout():
    """Test 5-column layout on same row"""
    print("🏠 === TESTING 5-COLUMN HORIZONTAL LAYOUT ===")
    
    try:
        # Test comic homepage
        response = requests.get("http://127.0.0.1:5001/comics-home")
        
        if response.status_code == 200:
            print("✅ Comic Homepage accessible")
            content = response.text
            
            # Check for 5-column grid classes
            checks = [
                ("col-xl col-lg col-md col-sm-6 col-6", "5-column responsive grid"),
                ("row g-2", "Bootstrap row with gap"),
                ("featured-card-small", "Small featured cards"),
                ("featured-cover-small", "Small cover images")
            ]
            
            print("\n🔍 Grid Layout Elements Check:")
            for element, description in checks:
                found = element in content
                status = "✅" if found else "❌"
                print(f"   {status} {description}")
            
            # Check responsive CSS breakpoints for 5 columns
            responsive_checks = [
                ("@media (min-width: 992px)", "Large screen (5 cols)"),
                ("@media (max-width: 991px)", "Medium screen (5 cols)"),
                ("@media (max-width: 768px)", "Small screen (5 cols compact)"),
                ("@media (max-width: 576px)", "Extra small screen (2-3 cols)")
            ]
            
            print("\n📱 Responsive Design Check:")
            for element, description in responsive_checks:
                found = element in content
                status = "✅" if found else "❌"
                print(f"   {status} {description}")
                
            # Check that old problematic classes are removed
            old_classes = [
                ("col-md-4", "Old 3-column class (should be removed)"),
                ("col-lg col-md-4", "Mixed 3/5 column classes (should be removed)")
            ]
            
            print("\n❌ Old Classes Check:")
            for element, description in old_classes:
                found = element in content
                status = "❌ FOUND" if found else "✅ REMOVED"
                print(f"   {status} {description}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
        # Test novel homepage too
        print("\n📚 Testing Novel Homepage:")
        response_novel = requests.get("http://127.0.0.1:5001/novels-home")
        
        if response_novel.status_code == 200:
            print("✅ Novel Homepage accessible")
            content_novel = response_novel.text
            
            if "col-xl col-lg col-md col-sm-6 col-6" in content_novel:
                print("✅ Novel homepage has 5-column layout")
            else:
                print("❌ Novel homepage missing 5-column layout")
        else:
            print(f"❌ Novel homepage error: {response_novel.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_layout_explanation():
    """Explain the 5-column layout behavior"""
    print("\n📐 === 5-COLUMN LAYOUT EXPLANATION ===")
    
    layout_behavior = [
        "🖥️  Extra Large (≥1200px): col-xl → 5 equal columns",
        "💻 Large (992px-1199px): col-lg → 5 equal columns", 
        "📱 Medium (768px-991px): col-md → 5 equal columns",
        "📱 Small (576px-767px): col-sm-6 → 2 columns (5 items = 2+2+1)",
        "📱 Extra Small (<576px): col-6 → 2 columns (5 items = 2+2+1)"
    ]
    
    print("Grid Behavior by Screen Size:")
    for behavior in layout_behavior:
        print(f"   {behavior}")
        
    print("\nKey Features:")
    features = [
        "✅ 5 truyện hiển thị trên cùng một hàng từ tablet trở lên",
        "✅ Tự động responsive - không bao giờ break layout",
        "✅ Compact design với image heights tùy thuộc screen",
        "✅ Chỉ mobile mới hiển thị 2 cột (do không gian hạn chế)",
        "✅ Consistent design cho cả comics và novels"
    ]
    
    for feature in features:
        print(f"   {feature}")

if __name__ == '__main__':
    test_five_column_layout()
    test_layout_explanation()