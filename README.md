# 🧩 Discord Quest
**File:** `discord.py`  
**Phiên bản:** 1.0

---

## ⚙️ Giới thiệu

Công cụ này giúp **kích hoạt DevTools** trong Discord Desktop, tự động khởi động lại Discord và mở **Console** (Ctrl+Shift+I) sẵn sàng để **dán script bypass Quest**.  
Phiên bản này được chỉnh sửa tối ưu cho người dùng Việt Nam, có giao diện thân thiện, hướng dẫn chi tiết, và tự động hóa hầu hết thao tác.

---

## 🚀 Tính năng chính

- ✅ **Tự động bật DevTools** trong `settings.json`.  
- ✅ **Tắt và mở lại Discord** để áp dụng thay đổi.  
- ✅ **Tự động mở Console (Ctrl+Shift+I)** sau khi Discord khởi động.  
- ✅ **Tự động Clear Console (Ctrl+L)** và gõ `allow pasting`.  
- ✅ **Nút Copy Script Bypass** ngay cạnh tiêu đề script.  
- ✅ **Log màu** hiển thị rõ trạng thái và tiến trình.  
- ✅ **Không yêu cầu quyền admin.**

---

## 📦 Yêu cầu

Cần cài các thư viện Python sau:

```bash
pip install psutil pyperclip pyautogui pygetwindow pypiwin32
```

> Nếu bạn chưa có Python: https://www.python.org/downloads/

---

## 🧭 Cách sử dụng

### 1️⃣ Chuẩn bị
- Đảm bảo bạn đã cài **Discord Desktop** (bản chính thức, Canary hoặc PTB đều được).
- Đăng nhập tài khoản và vào phần nhiệm vụ discord **nhấn “Chấp nhận nhiệm vụ” Quest** bạn muốn bypass.

---

### 2️⃣ Thực hiện trong Tool
1. Chạy file `discord.py`.
2. Nhấn **“1. Kích hoạt DevTools”** → Tool sẽ bật tính năng DevTools trong Discord.
3. Nhấn **“2. Bắt đầu/Tải lại Bypass”** → Tool sẽ tự tắt & mở lại Discord.
4. Sau khi Discord khởi động (khoảng **10 giây**), tool sẽ:
   - Focus cửa sổ Discord  
   - Mở DevTools (Ctrl+Shift+I)  
   - Clear console (Ctrl+L)  
   - Gõ lệnh `allow pasting` → Enter  

---

### 3️⃣ Copy Script & Dán vào Console
- Bấm **💾 Copy Script** (hoặc Ctrl+C trong ô Script).
- Trong Discord Console, **Ctrl+V → Enter** để chạy script.

> Nếu không dán được, hãy gõ `allow pasting` thủ công rồi dán lại.

---

### 4️⃣ Sau khi hoàn tất
- Console sẽ hiển thị log “Quest completed!” nếu thành công.  
- **Không đóng Tool** trong khi Discord đang chạy quest.

---

## 📁 Cấu trúc chính

| Thành phần | Mô tả |
|-------------|-------|
| `tim_duong_dan_settings()` | Tìm file `settings.json` trong các bản Discord |
| `bat_devtools_trong_settings()` | Ghi bật DevTools vào file cấu hình |
| `tat_tien_trinh_discord()` | Tắt mọi tiến trình Discord đang chạy |
| `mo_discord()` | Mở lại Discord qua `Update.exe` |
| `focus_discord_window_best_effort()` | Focus cửa sổ Discord (pygetwindow/win32) |
| `tu_dong_mo_console_va_allow_pasting()` | Mở DevTools, Clear Console, gõ `allow pasting` |
| `GiaoDienDiscord` | Lớp tạo giao diện chính bằng Tkinter |

---

## ⚠️ Lưu ý
- Tool này chỉ hoạt động với **Discord Desktop App**, **không hỗ trợ bản web**.
- Nên để tool **mở suốt quá trình bypass** để tránh Discord bị tự tắt.
- Nếu tự động focus thất bại, hãy click vào Discord rồi nhấn **Ctrl+Shift+I** thủ công.

---

## 🧑‍💻 Tác giả & Ghi chú
- **Tác giả gốc:** Dựa trên ý tưởng DevTools bypass của cộng đồng Discord.  
- **Chỉnh sửa & Việt hóa:** @Quý Phương.  
- Phiên bản tối ưu ổn định hơn, có thêm log màu, tự động focus Discord và hướng dẫn chi tiết.

---

## 🏁 Chạy chương trình

```bash
python discord.py
```

Khi giao diện mở ra, làm theo hướng dẫn hiển thị trên màn hình.

---

## 📜 Giấy phép

📝 Bản quyền & nguồn gốc

Nguồn gốc: “Complete Recent Discord Quest” — gist: https://gist.github.com/aamiaa/204cd9d42013ded9faf646fae7f89fbb

Tác giả: aamiaa

© Các điều khoản đề xuất

Mã nguồn gốc thuộc quyền tác giả aamiaa.

Bất cứ chỉnh sửa, phát hành lại hoặc sử dụng cần giữ ghi chú nguồn và tác giả.

Không khuyến khích sử dụng mã này cho mục đích vi phạm điều khoản dịch vụ của Discord hoặc nền tảng nào khác.

Mọi sửa đổi của bạn nên được gắn nhãn rõ “dựa trên mã gốc của aamiaa”, và nếu được chia sẻ cũng nên giữ liên kết tới gist gốc.
