# Hướng Dẫn Sử Dụng Form Upload Chapter Cho Truyện Chữ

## Tổng Quan

Đã tạo thành công hệ thống form riêng cho truyện chữ và truyện tranh:

- **Truyện Tranh** → Form với "Image URLs" (nhiều ảnh)
- **Truyện Chữ** → Form với "Nội Dung Chương" (textarea lớn)

## Files Đã Tạo/Cập Nhật

### 1. Template Mới: `app/templates/admin/add_novel_chapter.html`

- Form chuyên dụng cho truyện chữ
- Có textarea "Nội Dung Chương" với 20 dòng
- Auto-save draft sau 30 giây (lưu vào localStorage)
- Cảnh báo khi rời trang nếu chưa lưu
- Styling chuyên nghiệp cho văn bản

### 2. Route Cập Nhật: `app/routes/admin.py`

Hàm `add_chapter()` đã được cập nhật:

```python
if comic.content_type == 'novel':
    # Xử lý truyện chữ - lấy content
    content = request.form.get('content')
    chapter = Chapter(
        comic_id=comic_id,
        chapter_number=float(chapter_number),
        title=title,
        content=content.strip(),
        image_urls=None
    )
else:
    # Xử lý truyện tranh - lấy image_urls
    image_urls_text = request.form.get('image_urls')
    image_urls = [url.strip() for url in image_urls_text.split('\n') if url.strip()]
    chapter = Chapter(
        comic_id=comic_id,
        chapter_number=float(chapter_number),
        title=title,
        image_urls=json.dumps(image_urls)
    )
```

### 3. Template Đọc: `app/templates/comic/read_novel.html`

- Đã có sẵn template đẹp để đọc truyện chữ
- Font chữ đẹp (Noto Serif)
- Khoảng cách dòng thoải mái (1.8)
- Tự động chia đoạn văn
- Navigation (chương trước/sau)

## Cách Sử Dụng

### Bước 1: Đăng nhập

- Đăng nhập với tài khoản admin hoặc uploader

### Bước 2: Truy cập form thêm chapter

- Vào trang chi tiết truyện chữ
- Click nút "Thêm Chương" hoặc truy cập trực tiếp:
  ```
  http://127.0.0.1:5001/admin/comic/11/add_chapter
  ```
  (Thay 11 bằng ID truyện chữ của bạn)

### Bước 3: Điền thông tin

- **Số Chương**: 1, 2, 3... hoặc 1.5 (cho chương phụ)
- **Tiêu Đề Chương**: (Tùy chọn) Ví dụ: "Ly Hương", "Khởi Đầu Hành Trình"
- **Nội Dung Chương**: Copy/paste toàn bộ nội dung chương

### Bước 4: Submit

- Click "Thêm Chương"
- Hệ thống sẽ tự động lưu và redirect về trang chi tiết truyện

### Bước 5: Đọc Chapter

- URL format: `/comic/<comic_id>/chapter/<chapter_number>`
- Ví dụ: `http://127.0.0.1:5001/comic/11/chapter/1`

## Tính Năng Đặc Biệt

### Auto-Save Draft (Tự Động Lưu Nháp)

- Form sẽ tự động lưu nháp sau mỗi 30 giây vào localStorage
- Khi quay lại trang, sẽ hỏi có muốn khôi phục nháp không
- Nháp sẽ tự động xóa sau khi submit thành công

### Cảnh Báo Rời Trang

- Nếu có nội dung chưa lưu, trình duyệt sẽ cảnh báo khi bạn rời trang

### Responsive Design

- Form hoạt động tốt trên cả desktop và mobile

## Database

### Cấu trúc Chapter

```python
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'))
    chapter_number = db.Column(db.Float)
    title = db.Column(db.String(200))

    # Truyện chữ: content có giá trị, image_urls = None
    content = db.Column(db.Text)

    # Truyện tranh: image_urls có giá trị (JSON), content = None
    image_urls = db.Column(db.Text)
```

### Kiểm Tra Content Type

```python
from app.models.comic import Comic

novel = Comic.query.get(11)
if novel.content_type == 'novel':
    print("Đây là truyện chữ")
```

## Test Data

Đã tạo chapter test:

- **ID**: 13
- **Comic ID**: 11 (Tiên Nghịch)
- **Chapter Number**: 1.0
- **Title**: "Chương Test - Khởi Đầu"
- **Content**: 373 ký tự

Và có chapter thật:

- **ID**: 14
- **Comic ID**: 11
- **Chapter Number**: 1.0
- **Title**: "Ly hương"
- **Content**: 20,248 ký tự

## Lưu Ý

1. **Chapter Number Trùng**: Nếu có 2 chapters cùng số (như test), query `.first()` sẽ lấy cái đầu tiên. Nên xóa chapter test hoặc đổi số.

2. **Content Type**: Luôn đảm bảo truyện có `content_type='novel'` trong database để form hiển thị đúng.

3. **Đoạn Văn**: Trong content, các đoạn văn nên cách nhau 1 dòng trống để hiển thị đẹp.

## Troubleshooting

### Form vẫn hiển thị "Image URLs"?

- Kiểm tra `content_type` của truyện:
  ```python
  novel = Comic.query.get(id)
  print(novel.content_type)  # Phải là 'novel'
  ```

### Chapter không hiển thị?

- Kiểm tra chapter đã được lưu vào database chưa
- Kiểm tra `chapter_number` có đúng format không (float)

### 404 Error khi đọc chapter?

- Restart Flask server
- Kiểm tra URL format đúng: `/comic/<id>/chapter/<number>`

## Kết Luận

✅ Form upload chapter cho truyện chữ đã hoàn thành
✅ Tự động phân biệt truyện tranh vs truyện chữ
✅ Auto-save draft và cảnh báo rời trang
✅ Template đọc truyện chữ đẹp và chuyên nghiệp

Bây giờ bạn có thể upload truyện chữ một cách dễ dàng! 🎉
