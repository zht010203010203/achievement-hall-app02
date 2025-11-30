#!/usr/bin/env python3
"""
成就殿堂 - Replit云端一键打包脚本
使用方法：在Replit中直接运行此文件即可生成APK
"""

import os
import sys
import subprocess
import time

def run_command(cmd, description=""):
    """运行命令并显示进度"""
    print(f"🔧 {description}")
    print(f"   执行命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ 完成")
            return True
        else:
            print(f"   ❌ 失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def main():
    print("=" * 50)
    print("🎯 成就殿堂 - 云端一键打包")
    print("=" * 50)
    print()
    
    # 检查当前环境
    print("📋 环境检查:")
    print(f"   操作系统: {sys.platform}")
    print(f"   Python版本: {sys.version}")
    print(f"   当前目录: {os.getcwd()}")
    print()
    
    # 步骤1：安装必要依赖
    print("📥 步骤1: 安装依赖包")
    dependencies = [
        "buildozer",
        "kivy",
        "kivymd",
        "requests",
        "pillow",
        "cryptography"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"安装 {dep}"):
            print("❌ 依赖安装失败，请检查网络连接")
            return
    
    print()
    
    # 步骤2：初始化Buildozer配置
    print("⚙️ 步骤2: 配置打包环境")
    if os.path.exists("buildozer.spec"):
        print("   ✅ buildozer.spec 已存在")
    else:
        if not run_command("buildozer init", "初始化Buildozer配置"):
            print("❌ Buildozer初始化失败")
            return
    
    print()
    
    # 步骤3：开始打包
    print("🔨 步骤3: 开始打包APK")
    print("   注意：首次打包需要下载Android SDK/NDK")
    print("   这可能需要15-30分钟，请耐心等待...")
    print()
    
    start_time = time.time()
    
    # 使用非交互模式打包
    if run_command("buildozer android debug", "构建APK文件"):
        # 检查APK文件
        bin_dir = "bin"
        if os.path.exists(bin_dir):
            apk_files = [f for f in os.listdir(bin_dir) if f.endswith('.apk')]
            if apk_files:
                end_time = time.time()
                duration = int(end_time - start_time)
                
                print()
                print("🎉 打包成功！")
                print("=" * 50)
                print(f"📱 APK文件: {bin_dir}/{apk_files[0]}")
                print(f"⏱️ 耗时: {duration} 秒")
                print(f"📦 文件大小: {os.path.getsize(os.path.join(bin_dir, apk_files[0])) // 1024} KB")
                print()
                print("📲 安装说明:")
                print("   1. 在Replit文件管理器中找到bin文件夹")
                print("   2. 下载APK文件到电脑")
                print("   3. 传输到手机并安装")
                print("   4. 允许安装未知来源应用")
                print()
                print("💡 提示: 后续打包会更快，因为依赖已经缓存")
            else:
                print("❌ APK文件未生成，请检查错误日志")
        else:
            print("❌ bin目录不存在，打包可能失败")
    else:
        print("❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()