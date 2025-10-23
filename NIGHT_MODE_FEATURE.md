# Chế Độ Đọc Ban Đêm Cho Truyện Chữ

## Tổng Quan

Tính năng cho phép người dùng chuyển đổi giữa chế độ đọc _Ban ngày_ và _Ban đêm_ khi xem chương truyện chữ (`read_novel.html`). Mục tiêu: giảm mỏi mắt và cải thiện trải nghiệm đọc ở môi trường ánh sáng yếu.

## Cách Sử Dụng

Khi mở một chương truyện chữ, phía trên nội dung sẽ có nhóm nút:

- Ban ngày (mặc định)
- Ban đêm

Nhấn để chuyển đổi ngay lập tức. Trạng thái được lưu vào `localStorage` với key `novelReadingMode` để tự động áp dụng cho các lần đọc sau.

## Kỹ Thuật

- Template: `app/templates/comic/read_novel.html`
- Thêm lớp `night-mode` vào thẻ `<html>` (documentElement) khi kích hoạt.
- CSS chuyển nền `#121212`, chữ `#e0e0e0`, giảm độ chói.
- Chuyển đổi mượt mà qua `transition`.

## Mở Rộng Trong Tương Lai

- Thanh trượt thay đổi cỡ chữ.
- Tùy chọn font (Serif / Sans-Serif / Mono).
- Nhiều chủ đề: Sepia, Solarized Dark.
- Đồng bộ lựa chọn qua backend (lưu vào user settings khi đăng nhập).

## Ghi Chú

Nếu muốn tắt tính năng tạm thời, có thể ẩn khối `.reading-controls` trong template hoặc thêm flag cấu hình.
