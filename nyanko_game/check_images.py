#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查圖片解析度的工具腳本
"""

import os
import sys
import pygame


def check_image_sizes():
    """檢查所有圖片檔案的大小"""

    # 初始化 pygame
    pygame.init()

    # 圖片目錄
    images_dir = "assets/images"

    print("檢查圖片解析度:")
    print("=" * 50)

    # 遍歷所有圖片檔案
    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                filepath = os.path.join(root, file)
                try:
                    img = pygame.image.load(filepath)
                    width, height = img.get_size()
                    relative_path = os.path.relpath(filepath, images_dir)
                    print(f"{relative_path}: {width}x{height}")
                except Exception as e:
                    print(f"錯誤讀取 {filepath}: {e}")

    pygame.quit()


if __name__ == "__main__":
    check_image_sizes()
