"""全局配置"""
import os

# 应用信息
APP_NAME = "成就殿堂"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Pet AI Tracker"

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'achievement.db')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# 确保数据目录存在
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)

# 默认配置
DEFAULT_DAILY_TARGET = 20  # 默认每日目标
DEFAULT_TOTAL_TARGET = 10000  # 默认总目标
AVG_TIME_PER_QUESTION = 3  # 平均每题时长（分钟）

# AI配置
AI_REQUEST_TIMEOUT = 30  # API请求超时（秒）增加到30秒
AI_MIN_INTERVAL = 300  # 最小请求间隔（秒）
AI_MAX_TOKENS = 1500  # 最大生成token数（报告需要更多token）
AI_TEMPERATURE = 0.8  # 温度参数

# UI配置
ANIMATION_DURATION = 0.3  # 动画时长（秒）
PARTICLE_COUNT = 30  # 粒子数量
COMBO_THRESHOLD = 1.0  # Combo触发间隔（秒）
