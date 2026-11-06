"""Tạo file dữ liệu cho trang tra cứu từ file Excel tổng hợp.

Cách dùng (cần thư viện cryptography: pip install cryptography):
    MA_PIN='<mã PIN>' python3 tools/xay_du_lieu.py Tong_hop_ma_so_vung_trong_dong_goi_Chinaport_txng_ppd.xlsx 2026-11-06

Dữ liệu được nén và mã hoá AES-GCM bằng khoá sinh từ mã PIN (PBKDF2-SHA256),
nên chỉ người có mã PIN mới đọc được. Không ghi mã PIN vào repo.

File Excel cần các sheet: "Tổng hợp mã", "Chinaport - đã duyệt GACC",
"Đối chiếu ppd", "Đối chiếu txng.mae". Kết quả ghi ra data/ma_so.enc.json.
"""
import json, sys, re, os, gzip, base64
from pathlib import Path
import pandas as pd

src, ngay = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else '')
out = Path(__file__).resolve().parent.parent / 'data' / 'ma_so.enc.json'
pin = os.environ.get('MA_PIN')
if not pin:
    sys.exit('Thiếu mã PIN: đặt biến môi trường MA_PIN')
x = pd.read_excel(src, sheet_name=None, dtype=str)
M = x['Tổng hợp mã'].fillna('')
C = x['Chinaport - đã duyệt GACC'].fillna('')
P = x['Đối chiếu ppd'].fillna('')
T = x['Đối chiếu txng.mae'].fillna('')

def d10(v):
    return str(v)[:10] if v and str(v) != 'NaT' else ''

def key(s):
    s = s.upper().replace('Đ', 'D')
    s = re.sub(r'(?<!\d)0+(?=\d)', '', s)
    return re.sub(r'CHN$', '', re.sub(r'[^A-Z0-9]', '', s))

# Chi tiết từng mã GACC
gacc = {}
for _, r in C.iterrows():
    gacc[r['Mã đăng ký phía Trung Quốc']] = [
        r['Mã đăng ký phía Việt Nam'], r['Tên cơ sở / doanh nghiệp'], r['Địa chỉ'],
        r['Loại hình'], r['Sản phẩm'], d10(r['Ngày hiệu lực']), d10(r['Ngày hết hạn']),
        r['Trạng thái'], r['Hạn chế theo sản phẩm'], r['Tên tiếng Việt'],
    ]
addr_p = {key(r['Mã (ppd)']): r['Địa chỉ (ppd)'] for _, r in P.iterrows() if r['Mã (ppd)']}
addr_t = {key(r['Mã nội địa (txng.mae)']): r['Địa chỉ (txng.mae)'] for _, r in T.iterrows() if r['Mã nội địa (txng.mae)']}
ppd_note = {}
for _, r in P.iterrows():
    ppd_note.setdefault(key(r['Mã (ppd)']), []).append(r['Danh sách ppd'] + (': ' + r['Đợt / ghi chú (ppd)'] if r['Đợt / ghi chú (ppd)'] else ''))

KL = ['Đã được Trung Quốc duyệt (có mã GACC)', 'Có mã GACC nhưng đang TẠM DỪNG', 'Mới có mã nội địa (chưa thấy trên Chinaport)']
dicts = {f: [] for f in ['p', 't', 'c']}
def idx(f, v):
    L = dicts[f]
    if v not in L: L.append(v)
    return L.index(v)

rows = []
for _, r in M.iterrows():
    code = r['Mã nội địa (theo Chinaport nếu có)']
    gs = [g for g in r['Mã GACC'].split('; ') if g]
    k = key(code) if code else ''
    addr = next((gacc[g][2] for g in gs if g in gacc and gacc[g][2]), '') or addr_p.get(k, '') or addr_t.get(k, '')
    src = ''.join(['C' if r['Có trên Chinaport'] == 'Có' else '', 'T' if r['Có trên txng.mae'] == 'Có' else '',
                   'A' if r['ppd: GACC duyệt 14/8/2026'] else '', 'B' if r['ppd: Đã gửi 22/7/2026'] else '',
                   'D' if r['ppd: Chờ duyệt 23/7/2026'] else ''])
    rows.append([code, gs, r['Tên cơ sở'], idx('p', r['Tỉnh/TP (mới)']), idx('t', r['Loại mã']), r['Sản phẩm'],
                 KL.index(r['Kết luận']), r['Hạn chế theo sản phẩm'], d10(r['Ngày hiệu lực GACC (sớm nhất)']), src,
                 r['Tình trạng hồ sơ phía VN'], idx('c', r['Độ tin cậy']), r['Vấn đề cần kiểm tra'], addr,
                 ppd_note.get(k, []) if k else []])

data = {'ngay': ngay, 'kl': KL, 'dicts': dicts,
        'cols': ['ma', 'gacc', 'ten', 'tinh', 'loai', 'sp', 'kl', 'hanche', 'ngay', 'nguon', 'hosovn', 'tincay', 'vande', 'diachi', 'ppd'],
        'rows': rows, 'gacc_cols': ['ma_vn', 'ten', 'diachi', 'loaihinh', 'sp', 'tu', 'den', 'trangthai', 'hanche', 'ten_vn'], 'gacc': gacc}
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
ITER = 250000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pin.encode('utf-8'))
plain = gzip.compress(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)
ct = AESGCM(key).encrypt(iv, plain, None)
b = lambda x: base64.b64encode(x).decode()
out.write_text(json.dumps({'v': 1, 'iter': ITER, 'salt': b(salt), 'iv': b(iv), 'ct': b(ct)}), encoding='utf-8')
print(f'Đã ghi {out} ({len(rows)} mã, {len(gacc)} mã GACC, {out.stat().st_size/1e6:.2f} MB, đã mã hoá)')
