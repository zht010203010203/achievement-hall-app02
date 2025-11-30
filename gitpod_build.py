#!/usr/bin/env python3
"""
成就殿堂 - GitPod云端一键打包脚本
专为GitPod环境优化，包含详细进度显示
"""

import os
import sys
import subprocess
import time
import shutil

def print_step(step_num, description):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"🔧 步骤 {step_num}: {description}")
    print(f"{'='*60}")

def run_command(cmd, description="", check_output=False):
    """运行命令并显示进度"""
    print(f"   📋 {description}")
    print(f"      执行: {cmd}")
    
    try:
        if check_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
        if result.returncode == 0:
            print("       ✅ 成功")
            if result.stdout:
                print(f"       输出: {result.stdout[:200]}...")
            return True, result.stdout
        else:
            print(f"       ❌ 失败: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print("       ⏰ 超时，继续下一个步骤")
        return False, "Timeout"
    except Exception as e:
        print(f"       ❌ 异常: {e}")
        return False, str(e)

def check_environment():
    """检查环境"""
    print_step(0, "环境检查")
    
    # 检查GitPod特定环境变量
    if os.environ.get('GITPOD_WORKSPACE_URL'):
        print("   🌐 检测到GitPod环境")
        print(f"   工作空间: {os.environ.get('GITPOD_WORKSPACE_URL')}")
    else:
        print("   ⚠️ 当前不是GitPod环境，但可以继续")
    
    # 检查基本工具
    tools = ["python3", "pip3", "git"]
    for tool in tools:
        success, _ = run_command(f"which {tool}", f"检查 {tool}", check_output=True)
        if not success:
            print(f"   ❌ {tool} 未找到，尝试安装...")
    
    return True

def install_dependencies():
    """安装依赖"""
    print_step(1, "安装必要依赖")
    
    # 更新pip
    run_command("pip3 install --upgrade pip", "更新pip")
    
    # 安装核心依赖
    dependencies = [
        ("buildozer", "Buildozer（打包工具）"),
        ("kivy", "Kivy（界面框架）"),
        ("kivymd", "KivyMD（Material Design）"),
        ("requests", "网络请求"),
        ("Pillow", "图片处理"),
        ("cryptography", "加密库")
    ]
    
    for package, description in dependencies:
        success, _ = run_command(f"pip3 install {package}", f"安装 {description}")
        if not success:
            print(f"   ⚠️ {description} 安装失败，尝试继续")
    
    return True

def setup_buildozer():
    """配置Buildozer"""
    print_step(2, "配置打包环境")
    
    # 检查buildozer.spec是否存在
    if os.path.exists("buildozer.spec"):
        print("   ✅ buildozer.spec 配置文件已存在")
        # 备份原配置
        shutil.copy("buildozer.spec", "buildozer.spec.backup")
        print("   📝 已备份原配置文件")
    else:
        # 初始化配置
        success, _ = run_command("buildozer init", "初始化Buildozer配置")
        if not success:
            return False
    
    # 检查并修复配置
    print("   🔧 检查配置文件...")
    
    # 读取当前配置
    with open("buildozer.spec", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 确保包含必要配置
    required_configs = [
        ("title = My Application", "title = 成就殿堂"),
        ("package.name = myapp", "package.name = achievementhall"),
        ("package.domain = org.test", "package.domain = com.achievement.hall")
    ]
    
    for old, new in required_configs:
        if old in content:
            content = content.replace(old, new)
            print(f"   ✅ 更新配置: {new}")
    
    # 写入更新后的配置
    with open("buildozer.spec", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("   ✅ 配置文件检查完成")
    return True

def build_apk():
    """构建APK"""
    print_step(3, "开始构建APK")
    
    print("   ⚠️ 重要提示：")
    print("   - 首次构建需要下载Android SDK/NDK")
    print("   - 这可能需要20-40分钟，请耐心等待")
    print("   - GitPod会自动保存进度，断线可恢复")
    print("   - 你可以在终端看到详细进度")
    
    start_time = time.time()
    
    # 清理之前的构建
    print("   🧹 清理构建缓存...")
    run_command("buildozer android clean", "清理缓存")
    
    # 开始构建
    print("   🔨 开始构建APK...")
    success, output = run_command("buildozer android debug", "构建APK文件")
    
    end_time = time.time()
    duration = int(end_time - start_time)
    
    if success:
        # 检查APK文件
        bin_dir = "bin"
        if os.path.exists(bin_dir):
            apk_files = [f for f in os.listdir(bin_dir) if f.endswith('.apk')]
            if apk_files:
                apk_path = os.path.join(bin_dir, apk_files[0])
                file_size = os.path.getsize(apk_path) // 1024
                
                print(f"\n{'🎉'*20}")
                print("🎉 打包成功！")
                print(f"{'🎉'*20}")
                print(f"📱 APK文件: {apk_path}")
                print(f"📦 文件大小: {file_size} KB")
                print(f"⏱️ 耗时: {duration} 秒 ({duration//60}分{duration%60}秒)")
                print()
                print("📲 下载说明:")
                print("   1. 在GitPod左侧文件管理器找到 'bin' 文件夹")
                print("   2. 右键点击APK文件 → 选择 'Download'")
                print("   3. 保存到电脑，然后传输到手机安装")
                print()
                print("💡 提示: 后续打包会更快，因为依赖已经缓存")
                return True
            else:
                print("❌ bin目录中没有找到APK文件")
                return False
        else:
            print("❌ bin目录不存在")
            return False
    else:
        print("❌ 构建失败")
        print("   错误信息:", output)
        return False

def main():
    """主函数"""
    print("🚀 成就殿堂 - GitPod云端一键打包")
    print("="*60)
    
    try:
        # 检查环境
        if not check_environment():
            return
        
        # 安装依赖
        if not install_dependencies():
            print("❌ 依赖安装失败")
            return
        
        # 配置Buildozer
        if not setup_buildozer():
            print("❌ 环境配置失败")
            return
        
        # 构建APK
        if not build_apk():
            print("❌ APK构建失败")
            return
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("💡 建议: 可以重新运行脚本，GitPod会自动恢复进度")

if __name__ == "__main__":
    main()