[app]

# 应用标题
title = 成就殿堂

# 包名
package.name = achievementhall

# 包域名
package.domain = org.petai

# 源代码目录
source.dir = .

# 源代码包含的文件扩展名
source.include_exts = py,png,jpg,kv,atlas,json,txt

# 版本号
version = 1.0.0

# 应用依赖
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,cryptography,pillow,sqlite3

# 排除不必要的文件
source.exclude_exts = spec,md
source.exclude_dirs = tests,bin,.buildozer

# 应用图标（可选）
#icon.filename = %(source.dir)s/assets/icon.png

# 启动画面（可选）
#presplash.filename = %(source.dir)s/assets/presplash.png

# Android 启动模式
android.presplash_color = #FFFFFF

# Android 特定配置
[app:android]

# Android API 版本
android.api = 33

# 最小 API 版本
android.minapi = 21

# Android NDK 版本
android.ndk = 25b

# Android SDK 版本
android.sdk = 33

# 应用权限
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 应用方向
orientation = portrait

# 全屏模式
fullscreen = 0

# Android 架构
android.archs = arm64-v8a,armeabi-v7a

# 是否接受 Android SDK 许可
android.accept_sdk_license = True

[buildozer]

# 日志级别
log_level = 2

# 警告级别
warn_on_root = 1
