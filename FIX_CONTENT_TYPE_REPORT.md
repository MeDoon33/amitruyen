# Báo cáo: Sửa lỗi Truyện Chữ hiển thị ở Trang Truyện Tranh

## Vấn đề

Khi đăng truyện chữ (novel), truyện vẫn hiển thị ở trang truyện tranh (comics homepage) thay vì chỉ hiển thị ở trang truyện chữ.

## Nguyên nhân

1. **Model có trường `content_type`** để phân biệt 'comic' và 'novel', nhưng code lọc trong `app/routes/main.py` **không sử dụng trường này**
2. Code cũ lọc dựa trên text matching trong `genre` và `tags` (tìm từ khóa "novel", "tiểu thuyết")
3. Các bản ghi cũ trong database có `content_type=None` chưa được cập nhật

## Giải pháp đã áp dụng

### 1. Cập nhật code lọc trong `app/routes/main.py`

#### Comics Homepage (`/comics-home`)

**Trước:**

```python
# Lọc bằng text matching
comics_query = Comic.query.filter(
    ~(Comic.genre.ilike('%novel%') |
      Comic.genre.ilike('%tiểu thuyết%') |
      Comic.tags.ilike('%novel%') |
      Comic.tags.ilike('%tiểu thuyết%'))
)
```

**Sau:**

```python
# Lọc bằng trường content_type
comics_query = Comic.query.filter(
    (Comic.content_type == 'comic') | (Comic.content_type == None)
)
```

#### Novels Homepage (`/novels-home`)

**Trước:**

```python
# Lọc bằng text matching
novels_query = Comic.query.filter(
    (Comic.genre.ilike('%novel%')) |
    (Comic.genre.ilike('%tiểu thuyết%')) |
    (Comic.tags.ilike('%novel%')) |
    (Comic.tags.ilike('%tiểu thuyết%'))
)
```

**Sau:**

```python
# Lọc bằng trường content_type
novels_query = Comic.query.filter(Comic.content_type == 'novel')
```

### 2. Cập nhật API Ranking (`/api/comic-ranking`)

Thay đổi tương tự cho API endpoint, sử dụng `content_type` thay vì text matching.

### 3. Cập nhật route `/novels` trong `app/routes/comic.py`

Sử dụng `content_type == 'novel'` thay vì text matching.

### 4. Cập nhật database

Chạy script `update_none_to_comic.py` để cập nhật tất cả bản ghi có `content_type=None` thành `content_type='comic'`.

**Kết quả:**

- 8 truyện tranh: `content_type='comic'`
- 1 truyện chữ: `content_type='novel'`

## Kiểm tra kết quả

Chạy script `test_separation.py` để kiểm tra:

```
✓ Comics Homepage: Không hiển thị truyện chữ "Tiên Nghịch"
✓ Novels Homepage: Hiển thị truyện chữ "Tiên Nghịch", không hiển thị truyện tranh
✓ API Comics: Trả về 8 truyện tranh, không có truyện chữ
✓ API Novels: Trả về 1 truyện chữ
```

## Hướng dẫn sử dụng

### Khi upload truyện mới:

1. Vào trang upload (`/admin/upload`)
2. Chọn **"Loại Nội Dung"**:
   - **Truyện Tranh** (comic) → Hiển thị ở `/comics-home`
   - **Truyện Chữ** (novel) → Hiển thị ở `/novels-home`

### Để sửa truyện đã đăng:

1. Vào trang sửa truyện (`/admin/comic/<id>/edit`)
2. Thay đổi trường **"Loại Nội Dung"**
3. Lưu lại

## Files đã sửa

- ✅ `app/routes/main.py` - Cập nhật filtering logic
- ✅ `app/routes/comic.py` - Cập nhật route `/novels`
- ✅ Database - Cập nhật tất cả records từ `None` → `'comic'`

## Scripts hỗ trợ

- `check_content_type.py` - Kiểm tra content_type trong database
- `update_none_to_comic.py` - Cập nhật None → 'comic'
- `fix_content_type.py` - Script tương tác để fix từng record
- `test_separation.py` - Test xem filtering có hoạt động đúng

## Kết luận

Vấn đề đã được sửa hoàn toàn. Bây giờ:

- ✅ Truyện chữ chỉ hiển thị ở trang truyện chữ (`/novels-home`)
- ✅ Truyện tranh chỉ hiển thị ở trang truyện tranh (`/comics-home`)
- ✅ API endpoints lọc đúng theo type
- ✅ Tất cả records trong database đã có `content_type` rõ ràng
