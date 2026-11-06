# Tra cứu mã số vùng trồng, cơ sở đóng gói xuất khẩu Trung Quốc

Trang tĩnh (GitHub Pages) để tra cứu mã vùng trồng và mã cơ sở đóng gói của Việt Nam xuất khẩu sang Trung Quốc (nhóm thực vật).

- Tìm theo mã nội địa, mã GACC (QVNM...), tên hoặc địa chỉ. Cách viết khác nhau (khoảng trắng, Đ/D, số 0 ở đầu, đuôi -CHN) vẫn tìm được.
- Lọc theo kết luận, loại mã, tỉnh/TP (địa giới mới), sản phẩm, độ tin cậy, hạn chế sản phẩm.
- Kiểm tra nhiều mã cùng lúc (dán danh sách).
- Xem chi tiết từng mã: các mã GACC, ngày hiệu lực, trạng thái, hạn chế theo sản phẩm, có trong nguồn nào, điểm cần kiểm tra.
- Liên kết trực tiếp tới một mã: `?ma=VN-TGOR-0085`.

## Mã PIN

Vào trang cần nhập mã PIN. Dữ liệu trong repo đã được mã hoá theo mã PIN (AES-GCM, khoá sinh bằng PBKDF2), nên không đọc được nếu không có PIN. Mã PIN không được lưu trong repo. Muốn đổi PIN thì chạy lại lệnh cập nhật dữ liệu với PIN mới.

## Lịch sử thao tác và trang quản lý

- Người dùng phải đồng ý lưu cookie và đặt tên trước khi dùng. Tên và mã thiết bị lưu trong cookie 1 năm.
- Trang ghi lại: vào trang, tìm kiếm (từ khoá, bộ lọc, số kết quả), xem chi tiết mã, kiểm tra nhiều mã, chuyển tab. Nhật ký lưu ở Supabase (dự án bvi-kiem-tra, bảng `tracuu_nhat_ky`); cấu hình kết nối trong `config.js`.
- Quyền công khai chỉ được ghi thêm nhật ký, không đọc được (RLS). Quản lý xem nhật ký tại `quan-ly.html` bằng mật khẩu; mật khẩu chỉ lưu dạng băm trong database, không có trong repo.
- SQL tạo bảng và cách đổi mật khẩu quản lý: `supabase/nhat_ky.sql`.

## Nguồn và nguyên tắc

| Nguồn | Ý nghĩa |
|---|---|
| Chinaport (scintl.chinaport.gov.cn) | Danh sách đăng ký kiểm dịch của GACC. Có trên đây = đã được Trung Quốc duyệt, có mã GACC. |
| txng.mae.gov.vn | Danh mục mã số vùng trồng trong nước. |
| ppd.gov.vn | Danh sách của Cục Trồng trọt và BVTV: GACC phê duyệt, đã gửi GACC, chờ duyệt. |

Mã chỉ có ở nguồn Việt Nam, không có trên Chinaport, được ghi là "Mới có mã nội địa".

## Cập nhật dữ liệu

1. Tải lại dữ liệu và làm file Excel tổng hợp (sheet "Tổng hợp mã", "Chinaport - đã duyệt GACC", "Đối chiếu ppd", "Đối chiếu txng.mae").
2. Chạy:

   ```
   pip install cryptography
   MA_PIN='<mã PIN>' python3 tools/xay_du_lieu.py Tong_hop_ma_so_vung_trong_dong_goi_Chinaport_txng_ppd.xlsx 2026-11-06
   ```

   Lệnh ghi lại `data/ma_so.enc.json` (đã mã hoá theo mã PIN). Tham số thứ hai là ngày tải dữ liệu, hiện ở đầu trang.
3. Commit file `data/ma_so.enc.json`.

Trang này không phải trang chính thức của cơ quan nhà nước. Trước khi khai báo xuất khẩu, nên kiểm tra lại trên Chinaport.
