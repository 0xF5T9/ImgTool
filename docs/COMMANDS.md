# ImgTool - All Commands Reference

## Setup Commands (Windows)

```cmd
setup.bat                    # Setup venv + install dependencies
run.bat                      # Run app in venv
create_test_images.bat       # Create test images
```

## CLI Commands

### Core Commands

| Command | Syntax | Description |
|---------|--------|-------------|
| `magic` | `magic <input> <output> <size> <colors> [tolerance]` | All-in-one: resize + remove colors + optimize |
| `process` | `process --input <path> --output <dir> [options]` | Advanced processing with full control |
| `resize` | `resize <input> <output> <size>` | Quick resize only |
| `remove-color` | `remove-color <input> <output> <hex>` | Quick remove color only |
| `preview` | `preview <pattern>` | Preview files before processing |

### Utility Commands

| Command | Description |
|---------|-------------|
| `help` | Show all commands |
| `examples` | Show usage examples |
| `clear` | Clear screen |
| `exit` / `quit` | Exit CLI |

---

## MAGIC Command (⭐ Khuyên dùng)

### Cú pháp

```bash
magic <input> <output> <size> <hex_colors> [tolerance]
```

### Tham số

- `<input>`: Pattern file đầu vào (vd: `./icons/*.png`)
- `<output>`: Thư mục xuất
- `<size>`: Kích thước vuông (vd: `64` → 64x64)
- `<hex_colors>`: Màu HEX cần xóa (phân tách bằng dấu phẩy)
- `[tolerance]`: Sai số màu 0-255 (optional, default: 10)

### Ví dụ

```bash
# Cơ bản: xóa trắng, resize 64
magic ./input/*.png ./output 64 #FFFFFF

# Với tolerance
magic ./input/*.png ./output 64 #FFFFFF 15

# Nhiều màu
magic ./icons/*.png ./clean 48 #FFFFFF,#000000,#F5F5F5 10

# Nested folders
magic ./assets/**/*.png ./output 128 #00FF00 5
```

### Features

- ✅ Auto resize về size x size
- ✅ Auto keep aspect ratio (giữ tỷ lệ)
- ✅ Xóa nhiều màu cùng lúc
- ✅ Tolerance-based color matching
- ✅ PNG optimization
- ✅ Auto overwrite

---

## PROCESS Command (Advanced)

### Cú pháp

```bash
process --input <pattern> --output <dir> [options]
```

### Options

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--input` | string | **required** | Input pattern (e.g., `./icons/*.png`) |
| `--output` | string | **required** | Output directory |
| `--size` | int | `48` | Target size (e.g., 64 → 64x64) |
| `--remove-color` | string | - | HEX colors (comma-separated or repeat flag) |
| `--tolerance` | int | `0` | Color tolerance 0-255 |
| `--keep-aspect` | flag | `false` | Keep aspect ratio with transparent padding |
| `--suffix` | string | `""` | Filename suffix (e.g., `_48`) |
| `--overwrite` | flag | `false` | Overwrite existing files |

### Ví dụ

#### 1. Resize với keep aspect

```bash
process --input ./photos/*.jpg --output ./output --size 512 --keep-aspect
```

#### 2. Xóa nhiều màu (cách 1)

```bash
process --input ./icons/*.png --output ./output \
        --remove-color #FFFFFF,#000000,#F5F5F5 \
        --tolerance 10
```

#### 3. Xóa nhiều màu (cách 2 - repeat flag)

```bash
process --input ./icons/*.png --output ./output \
        --remove-color #FFFFFF \
        --remove-color #000000 \
        --tolerance 10
```

#### 4. Full options

```bash
process --input ./raw/*.png \
        --output ./output \
        --size 64 \
        --remove-color #FF00FF,#000000 \
        --tolerance 15 \
        --keep-aspect \
        --suffix _clean \
        --overwrite
```

---

## RESIZE Command (Quick)

### Cú pháp

```bash
resize <input> <output> <size>
```

### Ví dụ

```bash
resize ./icons/*.png ./output 48
resize ./photos/**/*.jpg ./resized 1024
```

### Features

- ✅ Quick resize to size x size
- ✅ No color removal
- ✅ Hard stretch (không giữ tỷ lệ)
- ✅ Auto overwrite

---

## REMOVE-COLOR Command (Quick)

### Cú pháp

```bash
remove-color <input> <output> <hex>
```

### Ví dụ

```bash
remove-color ./images/*.png ./output #FFFFFF
remove-color ./logos/*.png ./clean #000000
```

### Features

- ✅ Quick color removal
- ✅ No resize (giữ nguyên size)
- ✅ Tolerance = 0 (exact match)
- ✅ Auto overwrite

---

## PREVIEW Command

### Cú pháp

```bash
preview <pattern>
```

### Ví dụ

```bash
preview ./images/*.png
preview ./assets/**/*.jpg
preview ./**/*.{png,jpg}
```

### Output

- File name
- File size (KB)
- Image dimensions (WxH)

---

## Pattern Matching

### Wildcard patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `image.png` | Single file | `./photo.png` |
| `*.png` | All PNG in current dir | `./icons/*.png` |
| `**/*.png` | All PNG in all subdirs | `./assets/**/*.png` |
| `image*.png` | Prefix match | `./input/image*.png` |
| `*_icon.png` | Suffix match | `./icons/*_icon.png` |

### Ví dụ cụ thể

```bash
# Single file (lẻ 1 file)
magic ./photo.png ./output 512 #FFFFFF 10
resize ./logo.png ./output 256

# Multiple files with wildcard
magic ./icons/*.png ./output 64 #FFFFFF 10

# Recursive (tất cả subfolder)
magic ./assets/**/*.png ./output 128 #00FF00 5
```

### Multi-extension (shell dependent)

```bash
./**/*.{png,jpg,jpeg}     # May work in bash/zsh
```

---

## Use Cases & Recipes

### 1. Icon app/web (xóa nền trắng)

```bash
magic ./icons/*.png ./output 512 #FFFFFF 5
```

### 2. Logo (xóa nền đen)

```bash
magic ./logos/*.png ./output 256 #000000 10
```

### 3. Game sprite (green screen)

```bash
magic ./sprites/*.png ./output 128 #00FF00 5
```

### 4. Product photos (xóa nền trắng/xám)

```bash
magic ./products/*.jpg ./output 1024 #FFFFFF,#F5F5F5,#EEEEEE 20
```

### 5. Emoji/sticker

```bash
magic ./stickers/*.png ./output 128 #FFFFFF,#000000 10
```

### 6. Batch resize only (no color removal)

```bash
resize ./photos/**/*.jpg ./resized 1920
```

### 7. Just remove white (no resize)

```bash
remove-color ./images/*.png ./clean #FFFFFF
```

---

## Tolerance Guide

| Value | Effect | Use Case |
|-------|--------|----------|
| `0` | Exact match only | Pure solid colors |
| `5-10` | Near match | Recommended for most cases |
| `15-25` | Similar colors | Anti-aliased edges, gradients |
| `30-50` | Wide range | Very noisy backgrounds |
| `>50` | Very wide (careful!) | May remove unwanted colors |

---

## Tips & Tricks

### 1. Preview first

```bash
preview ./input/*.png
magic ./input/*.png ./output 64 #FFFFFF 10
```

### 2. Test with small tolerance

```bash
# Start small
magic ./test/*.png ./output 48 #FFFFFF 5

# If not clean enough, increase
magic ./test/*.png ./output 48 #FFFFFF 15
```

### 3. Multiple similar colors

```bash
# Instead of high tolerance:
magic ./img/*.png ./output 64 #FFFFFF 30

# Use specific colors:
magic ./img/*.png ./output 64 #FFFFFF,#FEFEFE,#F5F5F5,#EEEEEE 10
```

### 4. Keep aspect for photos

```bash
# For photos/rectangles - use process with --keep-aspect
process --input ./photos/*.jpg --output ./output --size 512 --keep-aspect

# For icons/squares - magic is fine
magic ./icons/*.png ./output 64 #FFFFFF
```

### 5. Batch with suffix

```bash
process --input ./originals/*.png \
        --output ./output \
        --size 48 \
        --suffix _48 \
        --remove-color #FFFFFF
# Creates: image_48.png in output folder
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Autocomplete commands/flags |
| `→` (Right Arrow) | Accept gray suggestion text |
| `↑` / `↓` | Navigate command history |
| `Ctrl+C` | Interrupt (shows warning) |
| `Ctrl+D` | EOF / Exit |

**Auto-suggestions:** Khi gõ lệnh, nếu đã dùng lệnh đó trước đây, CLI sẽ hiện text mờ mờ (gray) gợi ý. Nhấn **Right Arrow** để chấp nhận!

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (no files found, parse error, etc.) |

---

## Error Handling

### No files found

```
! No files found matching: ./wrong/*.png
```

**Fix:** Check path, use `preview` to test pattern

### Invalid HEX color

```
X Error: Invalid HEX color: #ZZZ
```

**Fix:** Use valid HEX like `#FFFFFF`, `#FF00FF`, `#000`

### Unknown command

```
X Unknown command: magik
Type help for available commands
```

**Fix:** Use `help` to see correct commands

---

Enjoy! 🎨
