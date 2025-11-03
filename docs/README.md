# 🎨 ImgTool - Interactive Image Processor CLI

Tool xử lý ảnh hàng loạt với giao diện CLI đẹp mắt kiểu Claude Code + Gemini, hỗ trợ resize và xóa màu thành trong suốt.

## ⚡ Cài đặt nhanh

### Windows (khuyên dùng - siêu dễ!)

```cmd
setup.bat     # Chạy 1 lần để setup venv + install
run.bat       # Chạy app
```

👉 Xem chi tiết: [WINDOWS_SETUP.md](WINDOWS_SETUP.md)

### Linux/Mac hoặc Manual

```bash
# Tạo venv (khuyên dùng)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate.bat  # Windows

# Cài thư viện
pip install -r requirements.txt

# Chạy app
python app.py
```

### Test nhanh với sample images

```bash
python test_demo.py  # Tạo test images
python app.py        # Chạy CLI
```

## Tính năng

- **Interactive CLI**: Tab autocomplete, auto-suggestions (text mờ từ history), command history (↑↓)
- **Batch Processing**: Xử lý hàng loạt với wildcard patterns
- **Resize**: Thu nhỏ/phóng to ảnh, giữ tỷ lệ nếu cần
- **Remove Colors**: Xóa nhiều màu cùng lúc thành alpha transparent
- **Preview**: Xem trước file trước khi xử lý
- **Progress Bar**: Hiển thị tiến độ real-time

## Lệnh cơ bản

```bash
# Trong CLI, gõ:
help              # Xem tất cả lệnh
examples          # Xem ví dụ sử dụng
preview *.png     # Xem trước file

# ⭐ MAGIC - All-in-one (khuyên dùng!)
magic ./input/*.png ./output 64 #FFFFFF,#000000 10
# Làm hết: resize 64x64 + xóa trắng & đen + tolerance 10 + giữ tỷ lệ

# Quick commands
resize ./input/*.png ./output 48
remove-color ./input/*.png ./output #FFFFFF

# Advanced - Full control
process --input ./icons/*.png --output ./output --size 64 --remove-color #FF00FF,#000000 --tolerance 10 --keep-aspect --overwrite
```

## Lệnh MAGIC - All-in-One ⭐

Lệnh magic làm hết mọi thứ trong 1 dòng:

```bash
magic <input> <output> <size> <hex_colors> [tolerance]
```

**Ví dụ:**

```bash
# Resize 64x64, xóa trắng + đen, tolerance 10
magic ./icons/*.png ./output 64 #FFFFFF,#000000 10

# Resize 48x48, chỉ xóa trắng, tolerance 5
magic ./photos/*.jpg ./output 48 #FFFFFF 5

# Nhiều màu cùng lúc
magic ./raw/*.png ./output 128 #FF00FF,#000000,#FFFFFF 15
```

**Features:**

- ✅ Auto resize về size x size
- ✅ Auto giữ tỷ lệ (keep aspect ratio)
- ✅ Xóa nhiều màu cùng lúc (phân tách bằng dấu phẩy)
- ✅ Tolerance tự động (default: 10)
- ✅ PNG optimization
- ✅ Overwrite mode

```

## Flags

- `--input`: Pattern file đầu vào (vd: `./icons/**/*.png`)
- `--output`: Thư mục xuất
- `--size`: Kích thước đích (default: 48)
- `--remove-color`: Màu HEX cần xóa (vd: `#FFFFFF`)
- `--tolerance`: Sai số màu 0-255 (default: 0)
- `--keep-aspect`: Giữ tỷ lệ ảnh, padding transparent
- `--suffix`: Hậu tố tên file (vd: `_48`)
- `--overwrite`: Ghi đè file tồn tại
