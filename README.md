# Tra cứu mã số vùng trồng, cơ sở đóng gói xuất khẩu Trung Quốc

Trang tĩnh (GitHub Pages) để tra cứu mã vùng trồng và mã cơ sở đóng gói của Việt Nam xuất khẩu sang Trung Quốc (nhóm thực vật).

- Tìm theo mã nội địa, mã GACC (QVNM...), tên hoặc địa chỉ. Cách viết khác nhau (khoảng trắng, Đ/D, số 0 ở đầu, đuôi -CHN) vẫn tìm được.
- Lọc theo kết luận, loại mã, tỉnh/TP (địa giới mới), sản phẩm, độ tin cậy, hạn chế sản phẩm.
- Kiểm tra nhiều mã cùng lúc (dán danh sách) và tải kết quả CSV.
- Xem chi tiết từng mã: các mã GACC, ngày hiệu lực, trạng thái, hạn chế theo sản phẩm, có trong nguồn nào, điểm cần kiểm tra.
- Liên kết trực tiếp tới một mã: `?ma=VN-TGOR-0085`.

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
   python3 tools/xay_du_lieu.py Tong_hop_ma_so_vung_trong_dong_goi_Chinaport_txng_ppd.xlsx 2026-11-06
   ```

   Lệnh ghi lại `data/ma_so.json`. Tham số thứ hai là ngày tải dữ liệu, hiện ở đầu trang.
3. Commit file `data/ma_so.json`.

Trang này không phải trang chính thức của cơ quan nhà nước. Trước khi khai báo xuất khẩu, nên kiểm tra lại trên Chinaport.
