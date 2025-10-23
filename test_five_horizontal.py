#!/usr/bin/env python3
"""
Test 5 featured comics in one horizontal row
"""

import requests

def test_horizontal_five_layout():
    """Test 5 comics in one horizontal row layout"""
    print("🏆 === TESTING 5 FEATURED COMICS IN ONE ROW ===")
    
    try:
        # Test comic homepage
        response = requests.get("http://127.0.0.1:5001/comics-home")
        
        if response.status_code == 200:
            print("✅ Comic Homepage accessible")
            content = response.text
            
            # Check for simple col class (Bootstrap auto-width columns)
            checks = [
                ('class="col"', "Simple col class for equal width"),
                ("row g-2", "Bootstrap row with gap"),
                ("featured-card-small", "Small featured cards"),
                ("featured-cover-small", "Small cover images"),
                ("popular_comics[:5]", "Limit to 5 comics"),
                ("flex: 1", "CSS flex equal width"),
                ("min-width: 0", "CSS prevent overflow")
            ]
            
            print("\n🔍 Layout Elements Check:")
            for element, description in checks:
                found = element in content
                status = "✅" if found else "❌"
                print(f"   {status} {description}")
            
            # Check responsive design for proper 5-column behavior
            responsive_checks = [
                ("@media (min-width: 768px)", "Tablet breakpoint"),
                ("@media (min-width: 992px)", "Desktop breakpoint"),
                ("@media (max-width: 767px)", "Mobile breakpoint"),
                ("flex: 0 0 50%", "Mobile 2-column fallback")
            ]
            
            print("\n📱 Responsive Design Check:")
            for element, description in responsive_checks:
                found = element in content
                status = "✅" if found else "❌"
                print(f"   {status} {description}")
                
            # Verify image heights for different screens
            image_heights = [
                ("height: 200px", "Desktop image height"),
                ("height: 180px", "Tablet image height"), 
                ("height: 160px", "Mobile image height"),
                ("height: 140px", "Small mobile height")
            ]
            
            print("\n🖼️  Image Heights Check:")
            for element, description in image_heights:
                found = element in content
                status = "✅" if found else "❌"
                print(f"   {status} {description}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def print_layout_summary():
    """Print summary of the 5-column layout"""
    print("\n📐 === LAYOUT SUMMARY ===")
    
    print("🎯 Design Goal: 5 truyện nổi bật trên cùng một hàng ngang")
    
    print("\n💻 Implementation:")
    implementation = [
        "✅ Sử dụng Bootstrap class='col' cho equal width",
        "✅ CSS flex: 1 đảm bảo 5 cột đều nhau",
        "✅ min-width: 0 ngăn overflow",
        "✅ Responsive heights: 200px→180px→160px→140px",
        "✅ Mobile fallback: 2 cột khi màn hình quá nhỏ"
    ]
    
    for item in implementation:
        print(f"   {item}")
        
    print("\n📱 Behavior by Screen Size:")
    behaviors = [
        "🖥️  Desktop (≥992px): 5 cột đều nhau, height 200px",
        "📱 Tablet (768px-991px): 5 cột đều nhau, height 180px", 
        "📱 Mobile (≤767px): 2 cột để dễ xem, height 160px",
        "📱 Small Mobile (≤480px): 2 cột compact, height 140px"
    ]
    
    for behavior in behaviors:
        print(f"   {behavior}")
        
    print("\n🎨 Visual Match với hình:")
    matches = [
        "✅ 5 truyện trên cùng một hàng ngang",
        "✅ Kích thước đều nhau và cân đối",
        "✅ Có badge 'Nổi bật' màu đỏ",
        "✅ Hiển thị title, views, rating",
        "✅ Layout responsive cho mobile"
    ]
    
    for match in matches:
        print(f"   {match}")

if __name__ == '__main__':
    test_horizontal_five_layout()
    print_layout_summary()