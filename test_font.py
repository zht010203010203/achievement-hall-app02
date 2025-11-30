"""测试字体注册"""
import os
from kivy.core.text import LabelBase

FONT_PATH = "C:/Windows/Fonts/"

# 检查字体文件是否存在
fonts_to_check = [
    'msyh.ttc',
    'msyhbd.ttc',
    'simsun.ttc',
    'simhei.ttf'
]

print("=" * 50)
print("检查Windows字体文件：")
for font in fonts_to_check:
    path = FONT_PATH + font
    exists = os.path.exists(path)
    print(f"  {font}: {'✓ 存在' if exists else '✗ 不存在'}")

print("\n" + "=" * 50)
print("尝试注册中文字体：")

# 尝试注册微软雅黑
try:
    LabelBase.register(
        name='TestFont',
        fn_regular=FONT_PATH + 'msyh.ttc'
    )
    print("✓ 微软雅黑注册成功")
except Exception as e:
    print(f"✗ 微软雅黑注册失败: {e}")

# 尝试注册宋体
try:
    LabelBase.register(
        name='TestFont2',
        fn_regular=FONT_PATH + 'simsun.ttc'
    )
    print("✓ 宋体注册成功")
except Exception as e:
    print(f"✗ 宋体注册失败: {e}")

print("=" * 50)
