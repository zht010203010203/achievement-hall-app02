#!/bin/bash

# 成就殿堂 APK 打包脚本
# 使用说明：在 WSL2 Ubuntu 中运行此脚本

echo "======================================"
echo "  成就殿堂 - APK 自动打包脚本"
echo "======================================"
echo ""

# 检查是否在 WSL 环境
if grep -qi microsoft /proc/version; then
    echo "✅ 检测到 WSL 环境"
else
    echo "⚠️  警告：未检测到 WSL 环境"
    echo "   如果您在 Linux 上，请忽略此警告"
fi

# 检查 Python
echo ""
echo "检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ 未找到 Python3，请先安装"
    exit 1
fi

# 检查 pip
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 已安装"
else
    echo "❌ 未找到 pip3，请先安装"
    exit 1
fi

# 检查 Java
echo ""
echo "检查 Java 环境..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    echo "✅ $JAVA_VERSION"
else
    echo "❌ 未找到 Java，请先安装"
    echo "   运行: sudo apt install openjdk-17-jdk"
    exit 1
fi

# 询问用户操作
echo ""
echo "请选择操作："
echo "1) 安装依赖（首次打包必须）"
echo "2) 清理并重新打包"
echo "3) 快速打包（Debug 版本）"
echo "4) 打包正式版（Release 版本）"
echo "5) 退出"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "======================================"
        echo "  安装依赖"
        echo "======================================"

        # 安装系统依赖
        echo "安装系统依赖..."
        sudo apt update
        sudo apt install -y build-essential git zip unzip \
            openjdk-17-jdk autoconf libtool pkg-config \
            zlib1g-dev libncurses5-dev libncursesw5-dev \
            libtinfo5 cmake libffi-dev libssl-dev

        # 安装 Python 依赖
        echo "安装 Python 依赖..."
        pip3 install --upgrade pip
        pip3 install --upgrade cython==0.29.36
        pip3 install --upgrade buildozer

        echo "✅ 依赖安装完成！"
        ;;

    2)
        echo ""
        echo "======================================"
        echo "  清理并重新打包"
        echo "======================================"

        # 检查 buildozer
        if ! command -v buildozer &> /dev/null; then
            echo "❌ 未找到 Buildozer，请先安装（选项 1）"
            exit 1
        fi

        echo "清理构建缓存..."
        buildozer android clean

        echo "开始打包（这可能需要 30-60 分钟）..."
        buildozer -v android debug

        echo ""
        echo "✅ 打包完成！"
        echo "APK 位置: bin/achievementhall-1.0.0-arm64-v8a-debug.apk"
        ;;

    3)
        echo ""
        echo "======================================"
        echo "  快速打包 Debug 版本"
        echo "======================================"

        # 检查 buildozer
        if ! command -v buildozer &> /dev/null; then
            echo "❌ 未找到 Buildozer，请先安装（选项 1）"
            exit 1
        fi

        echo "开始打包..."
        buildozer -v android debug

        echo ""
        echo "✅ 打包完成！"
        echo "APK 位置: bin/achievementhall-1.0.0-arm64-v8a-debug.apk"

        # 询问是否安装到手机
        echo ""
        read -p "是否安装到已连接的手机？(y/n): " install
        if [ "$install" = "y" ]; then
            if command -v adb &> /dev/null; then
                echo "检测到的设备："
                adb devices
                echo ""
                adb install -r bin/achievementhall-1.0.0-arm64-v8a-debug.apk
            else
                echo "❌ 未找到 ADB，请手动传输 APK 到手机"
            fi
        fi
        ;;

    4)
        echo ""
        echo "======================================"
        echo "  打包 Release 版本"
        echo "======================================"

        # 检查 buildozer
        if ! command -v buildozer &> /dev/null; then
            echo "❌ 未找到 Buildozer，请先安装（选项 1）"
            exit 1
        fi

        echo "⚠️  注意：Release 版本需要签名配置"
        echo "如果没有配置签名，将生成未签名的 APK"
        echo ""
        read -p "继续？(y/n): " confirm

        if [ "$confirm" = "y" ]; then
            echo "开始打包..."
            buildozer -v android release

            echo ""
            echo "✅ 打包完成！"
            echo "APK 位置: bin/achievementhall-1.0.0-arm64-v8a-release-unsigned.apk"
        fi
        ;;

    5)
        echo "退出"
        exit 0
        ;;

    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "  完成！"
echo "======================================"
