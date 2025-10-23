# Tạm Tắt Chức Năng Thăng Cấp / Danh Hiệu / Huy Hiệu

Các cờ (feature flags) đã được thêm vào `app/__init__.py`:

```python
app.config['PROGRESSION_ENABLED'] = False  # Điểm, level, leaderboard, activities
app.config['RANK_TITLES_ENABLED'] = False  # Danh hiệu cấp bậc
app.config['BADGES_ENABLED'] = False       # Huy hiệu người dùng
```

## Ảnh hưởng khi tắt

- Trang `/progression/stats` hiển thị thông báo "Chức năng đang phát triển".
- Các API:
  - `/progression/api/user/stats` trả về `{ disabled: true, message: 'Chức năng đang phát triển' }` status 503.
  - `/progression/api/user/badges` trả về `{ disabled: true, message: 'Huy hiệu đang phát triển' }`.
  - `/progression/api/rank-titles` trả về `{ disabled: true, message: 'Danh hiệu đang phát triển' }`.
  - `/progression/api/user/activities` trả về `{ disabled: true, message: 'Hoạt động đang phát triển' }`.
  - `/progression/api/leaderboard` trả về `{ disabled: true, message: 'Bảng xếp hạng đang phát triển' }`.
  - `/progression/api/user/change-rank-type` trả về disabled nếu tắt `RANK_TITLES_ENABLED`.

## Bật lại

Sửa các giá trị trong `create_app()`:

```python
app.config['PROGRESSION_ENABLED'] = True
app.config['RANK_TITLES_ENABLED'] = True
app.config['BADGES_ENABLED'] = True
```

Restart server.

## Gợi ý nâng cấp trước khi bật lại

1. Thêm giới hạn hợp lý cho điểm theo ngày và chống spam.
2. Tối ưu truy vấn leaderboard theo thời gian (day/week/month) qua aggregate.
3. Thêm cache cho danh hiệu và huy hiệu.
4. Thêm test tự động kiểm tra logic lên cấp.

## TODO khi phát triển lại

- Viết migration thêm bảng tổng hợp điểm theo ngày.
- Thêm hàng đợi xử lý điểm (celery hoặc background job).
- Thiết kế lại màu danh hiệu và chuẩn hoá cấp.
- Thêm trang hướng dẫn (how it works).
