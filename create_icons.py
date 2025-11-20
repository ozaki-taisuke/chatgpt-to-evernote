"""
Chrome拡張機能用のアイコン画像を生成
"""

from PIL import Image, ImageDraw

def create_icon(size):
    """アイコン画像作成"""
    # 背景色（ティールグリーン）
    bg_color = (0, 150, 136)
    
    # 画像作成
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 白い正方形（ノートをイメージ）
    margin = size // 4
    draw.rectangle(
        [margin, margin, size - margin, size - margin],
        fill=(255, 255, 255)
    )
    
    # 横線（ノートの罫線をイメージ）
    line_count = 3
    line_spacing = (size - 2 * margin) // (line_count + 1)
    for i in range(1, line_count + 1):
        y = margin + line_spacing * i
        draw.line(
            [margin + 10, y, size - margin - 10, y],
            fill=bg_color,
            width=max(1, size // 64)
        )
    
    return img

# 各サイズのアイコン生成
sizes = [16, 48, 128]
for size in sizes:
    icon = create_icon(size)
    icon.save(f'chrome-extension/icons/icon{size}.png')
    print(f'✅ Created icon{size}.png')

print('🎉 All icons created!')
