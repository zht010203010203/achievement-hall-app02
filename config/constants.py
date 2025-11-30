"""常量定义"""

# 成就类型
ACHIEVEMENT_TYPES = {
    'QUANTITY': '数量型',
    'STREAK': '连续型',
    'SPEED': '速度型',
    'VERSATILE': '全能型'
}

# 成就稀有度
ACHIEVEMENT_RARITY = {
    'BRONZE': {'name': '青铜', 'color': '#CD7F32', 'icon': '🥉'},
    'SILVER': {'name': '白银', 'color': '#C0C0C0', 'icon': '🥈'},
    'GOLD': {'name': '黄金', 'color': '#FFD700', 'icon': '🥇'},
    'DIAMOND': {'name': '钻石', 'color': '#B9F2FF', 'icon': '💎'},
    'LEGEND': {'name': '传说', 'color': '#FF6B6B', 'icon': '👑'}
}

# 预设成就定义
PRESET_ACHIEVEMENTS = [
    # ========== 数量型成就（递进式）==========
    # 启程之路（1-100题）
    {
        'name': '破晓启程',
        'description': '完成第1道题目',
        'type': 'QUANTITY',
        'rarity': 'BRONZE',
        'condition': {'total_count': 1},
        'icon': '🌱',
        'repeatable': False
    },
    {
        'name': '初心不改',
        'description': '完成前10道题目',
        'type': 'QUANTITY',
        'rarity': 'BRONZE',
        'condition': {'total_count': 10},
        'icon': '🎯',
        'repeatable': False
    },
    {
        'name': '崭露头角',
        'description': '累计完成50道题目',
        'type': 'QUANTITY',
        'rarity': 'BRONZE',
        'condition': {'total_count': 50},
        'icon': '📚',
        'repeatable': False
    },
    {
        'name': '百炼成钢',
        'description': '累计完成100道题目',
        'type': 'QUANTITY',
        'rarity': 'SILVER',
        'condition': {'total_count': 100},
        'icon': '⭐',
        'repeatable': False
    },
    
    # 进阶征途（200-500题）
    {
        'name': '乘风破浪',
        'description': '累计完成200道题目',
        'type': 'QUANTITY',
        'rarity': 'SILVER',
        'condition': {'total_count': 200},
        'icon': '🎈',
        'repeatable': False
    },
    {
        'name': '披荆斩棘',
        'description': '累计完成300道题目',
        'type': 'QUANTITY',
        'rarity': 'SILVER',
        'condition': {'total_count': 300},
        'icon': '⚔️',
        'repeatable': False
    },
    {
        'name': '独步江湖',
        'description': '累计完成500道题目',
        'type': 'QUANTITY',
        'rarity': 'GOLD',
        'condition': {'total_count': 500},
        'icon': '🛡️',
        'repeatable': False
    },
    
    # 高手之路（700-1000题）
    {
        'name': '剑指天穹',
        'description': '累计完成700道题目',
        'type': 'QUANTITY',
        'rarity': 'GOLD',
        'condition': {'total_count': 700},
        'icon': '🌟',
        'repeatable': False
    },
    {
        'name': '千军破阵',
        'description': '累计完成1000道题目',
        'type': 'QUANTITY',
        'rarity': 'GOLD',
        'condition': {'total_count': 1000},
        'icon': '🔥',
        'repeatable': False
    },
    
    # 宗师境界（1500-3000题）
    {
        'name': '登峰造极',
        'description': '累计完成1500道题目',
        'type': 'QUANTITY',
        'rarity': 'GOLD',
        'condition': {'total_count': 1500},
        'icon': '🚀',
        'repeatable': False
    },
    {
        'name': '炉火纯青',
        'description': '累计完成2000道题目',
        'type': 'QUANTITY',
        'rarity': 'DIAMOND',
        'condition': {'total_count': 2000},
        'icon': '💫',
        'repeatable': False
    },
    {
        'name': '震古烁今',
        'description': '累计完成2500道题目',
        'type': 'QUANTITY',
        'rarity': 'DIAMOND',
        'condition': {'total_count': 2500},
        'icon': '🏅',
        'repeatable': False
    },
    {
        'name': '笑傲群雄',
        'description': '累计完成3000道题目',
        'type': 'QUANTITY',
        'rarity': 'DIAMOND',
        'condition': {'total_count': 3000},
        'icon': '💪',
        'repeatable': False
    },
    
    # 传奇征程（4000-7000题）
    {
        'name': '睥睨天下',
        'description': '累计完成4000道题目',
        'type': 'QUANTITY',
        'rarity': 'DIAMOND',
        'condition': {'total_count': 4000},
        'icon': '🦁',
        'repeatable': False
    },
    {
        'name': '横扫千军',
        'description': '累计完成5000道题目',
        'type': 'QUANTITY',
        'rarity': 'DIAMOND',
        'condition': {'total_count': 5000},
        'icon': '👊',
        'repeatable': False
    },
    {
        'name': '盖世无双',
        'description': '累计完成6000道题目',
        'type': 'QUANTITY',
        'rarity': 'DIAMOND',
        'condition': {'total_count': 6000},
        'icon': '🦸',
        'repeatable': False
    },
    {
        'name': '万古长青',
        'description': '累计完成7000道题目',
        'type': 'QUANTITY',
        'rarity': 'LEGEND',
        'condition': {'total_count': 7000},
        'icon': '⚡',
        'repeatable': False
    },
    
    # 神话永恒（8000-10000题）
    {
        'name': '开天辟地',
        'description': '累计完成8000道题目',
        'type': 'QUANTITY',
        'rarity': 'LEGEND',
        'condition': {'total_count': 8000},
        'icon': '🌠',
        'repeatable': False
    },
    {
        'name': '九天揽月',
        'description': '累计完成9000道题目',
        'type': 'QUANTITY',
        'rarity': 'LEGEND',
        'condition': {'total_count': 9000},
        'icon': '✨',
        'repeatable': False
    },
    {
        'name': '万法归宗',
        'description': '累计完成10000道题目',
        'type': 'QUANTITY',
        'rarity': 'LEGEND',
        'condition': {'total_count': 10000},
        'icon': '💎',
        'repeatable': False
    },
    
    # ========== 连续型成就（可重复）==========
    # 短期阶段（1-30天）
    {
        'name': '七日之约',
        'description': '连续打卡7天',
        'type': 'STREAK',
        'rarity': 'SILVER',
        'condition': {'streak_days': 7},
        'icon': '🌟',
        'repeatable': True
    },
    {
        'name': '星火燎原',
        'description': '连续打卡14天',
        'type': 'STREAK',
        'rarity': 'SILVER',
        'condition': {'streak_days': 14},
        'icon': '🔥',
        'repeatable': True
    },
    {
        'name': '日月同辉',
        'description': '连续打卡30天',
        'type': 'STREAK',
        'rarity': 'GOLD',
        'condition': {'streak_days': 30},
        'icon': '🏆',
        'repeatable': True
    },
    
    # 中期阶段（60-100天）
    {
        'name': '春华秋实',
        'description': '连续打卡60天',
        'type': 'STREAK',
        'rarity': 'GOLD',
        'condition': {'streak_days': 60},
        'icon': '⚔️',
        'repeatable': True
    },
    {
        'name': '百日筑基',
        'description': '连续打卡100天',
        'type': 'STREAK',
        'rarity': 'DIAMOND',
        'condition': {'streak_days': 100},
        'icon': '👑',
        'repeatable': True
    },
    
    # 长期阶段（150-365天）
    {
        'name': '五月凌云',
        'description': '连续打卡150天',
        'type': 'STREAK',
        'rarity': 'DIAMOND',
        'condition': {'streak_days': 150},
        'icon': '🛡️',
        'repeatable': True
    },
    {
        'name': '破茧成蝶',
        'description': '连续打卡200天',
        'type': 'STREAK',
        'rarity': 'DIAMOND',
        'condition': {'streak_days': 200},
        'icon': '💎',
        'repeatable': True
    },
    {
        'name': '涅槃重生',
        'description': '连续打卡300天',
        'type': 'STREAK',
        'rarity': 'LEGEND',
        'condition': {'streak_days': 300},
        'icon': '🌠',
        'repeatable': True
    },
    {
        'name': '年度传奇',
        'description': '连续打卡365天',
        'type': 'STREAK',
        'rarity': 'LEGEND',
        'condition': {'streak_days': 365},
        'icon': '⭐',
        'repeatable': True
    },
    
    # ========== 速度型成就（可重复）==========
    {
        'name': '疾风骤雨',
        'description': '单次提交超过20题',
        'type': 'SPEED',
        'rarity': 'BRONZE',
        'condition': {'single_submit': 20},
        'icon': '⚡',
        'repeatable': True
    },
    {
        'name': '御风而行',
        'description': '单次提交超过30题',
        'type': 'SPEED',
        'rarity': 'BRONZE',
        'condition': {'single_submit': 30},
        'icon': '🌪️',
        'repeatable': True
    },
    {
        'name': '风驰电掣',
        'description': '单次提交超过50题',
        'type': 'SPEED',
        'rarity': 'SILVER',
        'condition': {'single_submit': 50},
        'icon': '🚀',
        'repeatable': True
    },
    {
        'name': '迅雷不及',
        'description': '单次提交超过100题',
        'type': 'SPEED',
        'rarity': 'GOLD',
        'condition': {'single_submit': 100},
        'icon': '💨',
        'repeatable': True
    }
]

# AI平台配置
API_PLATFORMS = {
    'openrouter': {
        'name': 'OpenRouter',
        'base_url': 'https://openrouter.ai/api/v1',
        'auth_header': 'Authorization',
        'auth_prefix': 'Bearer',
        'models': [
            'anthropic/claude-3-sonnet',
            'openai/gpt-4-turbo',
            'meta-llama/llama-3-70b-instruct'
        ],
        'request_format': 'openai_compatible'
    },
    'deepseek': {
        'name': 'DeepSeek',
        'base_url': 'https://api.deepseek.com/v1',
        'auth_header': 'Authorization',
        'auth_prefix': 'Bearer',
        'models': [
            'deepseek-chat',
            'deepseek-coder'
        ],
        'request_format': 'openai_compatible'
    },
    'volcengine': {
        'name': '火山引擎',
        'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
        'auth_header': 'Authorization',
        'auth_prefix': 'Bearer',
        'models': [
            'doubao-pro-4k',
            'doubao-lite-4k'
        ],
        'request_format': 'openai_compatible'
    }
}

# AI身份预设
PRESET_AI_IDENTITIES = [
    {
        'name': '严师',
        'type': 'system',
        'description': '严格要求，注重纪律，鞭策型鼓励',
        'system_prompt': '你是一位严格的老师，对学生要求严格但关心学生成长。说话简洁有力，注重纪律和效率。',
        'color_primary': '#2C3E50',
        'color_accent': '#34495E',
        'tone_style': '严厉但关怀'
    },
    {
        'name': '挚友',
        'type': 'system',
        'description': '温暖贴心，理解支持，朋友式交流',
        'system_prompt': '你是用户的好朋友，温暖贴心，善于倾听和理解。说话轻松自然，像朋友聊天一样。',
        'color_primary': '#3498DB',
        'color_accent': '#5DADE2',
        'tone_style': '温暖友善'
    },
    {
        'name': '教练',
        'type': 'system',
        'description': '专业指导，方法建议，目标导向',
        'system_prompt': '你是一位专业的学习教练，注重方法和策略。善于分析问题，提供实用建议。',
        'color_primary': '#E67E22',
        'color_accent': '#F39C12',
        'tone_style': '专业务实'
    },
    {
        'name': '学长',
        'type': 'system',
        'description': '经验分享，耐心引导，鼓励尝试',
        'system_prompt': '你是一位经验丰富的学长，乐于分享经验。说话亲切耐心，善于鼓励和引导。',
        'color_primary': '#27AE60',
        'color_accent': '#2ECC71',
        'tone_style': '亲切耐心'
    }
]

# AI触发场景
AI_TRIGGER_SCENARIOS = {
    'daily_goal_complete': {
        'name': '完成每日目标',
        'prompt_template': '用户今日完成了{current}题，达成了每日{target}题的目标。请给予鼓励。'
    },
    'achievement_unlock': {
        'name': '解锁成就',
        'prompt_template': '用户刚刚解锁了成就【{achievement_name}】：{achievement_desc}。请表示祝贺。'
    },
    'streak_milestone': {
        'name': '连续打卡里程碑',
        'prompt_template': '用户已经连续打卡{streak_days}天了！请给予肯定和鼓励。'
    },
    'big_progress': {
        'name': '单次大量提交',
        'prompt_template': '用户刚刚一次性完成了{count}题！请表示惊喜和赞赏。'
    },
    'comeback': {
        'name': '重新开始学习',
        'prompt_template': '用户已经{days}天没有学习了，今天重新开始。请给予温暖的欢迎和鼓励。'
    },
    'manual_request': {
        'name': '主动请求鼓励',
        'prompt_template': '用户主动寻求鼓励。当前进度：总共{total}题，今日{current}题。请给予支持。'
    }
}

# 等级系统
LEVEL_THRESHOLDS = [
    (0, '新手'),
    (10, '学徒'),
    (50, '熟练者'),
    (100, '精英'),
    (300, '专家'),
    (500, '大师'),
    (1000, '宗师'),
    (3000, '传奇'),
    (5000, '王者'),
    (10000, '至尊')
]

# 主题色彩
THEME_COLORS = {
    'primary': '#4A7FFF',
    'primary_light': '#E8F0FF',
    'accent': '#FF6B6B',
    'success': '#27AE60',
    'warning': '#F39C12',
    'error': '#E74C3C',
    'text_primary': '#1A1A1A',
    'text_secondary': '#7F8C8D',
    'background': '#FFFFFF',
    'card_background': '#F8F9FA'
}
