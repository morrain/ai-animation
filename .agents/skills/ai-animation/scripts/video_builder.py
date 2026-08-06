#!/usr/bin/env python3
"""
video_builder.py
ai-animation Skill 关键帧图像处理、规格标准化与联系单 (Contact Sheet) 合成工具

依赖:
  pip install Pillow
"""

import sys
import os
import json

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("错误: 缺少 Pillow 依赖库。请运行: pip install Pillow")
    sys.exit(1)

TARGET_WIDTH = 1280
TARGET_HEIGHT = 720

def resize_and_crop(img_path, output_path, target_size=(TARGET_WIDTH, TARGET_HEIGHT), mode="pad"):
    """规整画面到 16:9 (1280x720)，默认采用无损底色延伸模式，严禁裁剪画面元素"""
    with Image.open(img_path).convert("RGB") as img:
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]

        if mode == "crop":
            # 强制裁剪模式
            if img_ratio > target_ratio:
                new_height = img.height
                new_width = int(new_height * target_ratio)
                left = (img.width - new_width) // 2
                top = 0
                right = left + new_width
                bottom = new_height
            else:
                new_width = img.width
                new_height = int(new_width / target_ratio)
                left = 0
                top = (img.height - new_height) // 2
                right = new_width
                bottom = top + new_height
            cropped = img.crop((left, top, right, bottom))
            resized = cropped.resize(target_size, Image.Resampling.LANCZOS)
        else:
            # 默认 pad 模式：等比缩放原图 + 智能提取边缘纸色填充两侧，100% 保留生成元素
            scale = min(target_size[0] / img.width, target_size[1] / img.height)
            scaled_w = int(img.width * scale)
            scaled_h = int(img.height * scale)
            img_resized = img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

            # 采样四个角落色彩作为无缝铺面底色
            corner_colors = [
                img.getpixel((0, 0)),
                img.getpixel((img.width - 1, 0)),
                img.getpixel((0, img.height - 1)),
                img.getpixel((img.width - 1, img.height - 1))
            ]
            bg_r = sum(c[0] for c in corner_colors) // 4
            bg_g = sum(c[1] for c in corner_colors) // 4
            bg_b = sum(c[2] for c in corner_colors) // 4
            bg_color = (bg_r, bg_g, bg_b)

            resized = Image.new("RGB", target_size, bg_color)
            paste_x = (target_size[0] - scaled_w) // 2
            paste_y = (target_size[1] - scaled_h) // 2
            resized.paste(img_resized, (paste_x, paste_y))

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        resized.save(output_path, "PNG")
        print(f"🖼️ 画面无损规整完成: {output_path} ({target_size[0]}x{target_size[1]}, mode={mode})")

def make_contact_sheet(image_paths, output_contact_sheet):
    """合成分镜网格预览图 (Contact Sheet)"""
    if not image_paths:
        print("未提供图片，无法制作联系单")
        return

    n = len(image_paths)
    cols = 2 if n <= 4 else 3
    rows = (n + cols - 1) // cols

    thumb_w, thumb_h = 400, 225
    margin = 20
    sheet_w = cols * thumb_w + (cols + 1) * margin
    sheet_h = rows * thumb_h + (rows + 1) * margin

    sheet = Image.new("RGB", (sheet_w, sheet_h), "#1E1E1E")
    
    for idx, path in enumerate(image_paths):
        if not os.path.exists(path):
            continue
        r = idx // cols
        c = idx % cols
        x = margin + c * (thumb_w + margin)
        y = margin + r * (thumb_h + margin)

        with Image.open(path) as img:
            thumb = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x, y))

    os.makedirs(os.path.dirname(os.path.abspath(output_contact_sheet)), exist_ok=True)
    sheet.save(output_contact_sheet, "JPEG")
    print(f"📋 联系单网格图合成完成: {output_contact_sheet}")

def main():
    if len(sys.argv) < 3:
        print("用法: python3 video_builder.py <command> <options>")
        print("命令: resize <input_img> <output_img>")
        print("命令: contact-sheet <output_sheet.jpg> <img1> <img2> ...")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "resize" and len(sys.argv) >= 4:
        resize_and_crop(sys.argv[2], sys.argv[3])
    elif cmd == "contact-sheet" and len(sys.argv) >= 4:
        out_sheet = sys.argv[2]
        imgs = sys.argv[3:]
        make_contact_sheet(imgs, out_sheet)
    else:
        print(f"未知或无效命令: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
