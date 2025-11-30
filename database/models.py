"""数据模型定义"""

# 数据库表结构SQL

# 用户配置表
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    daily_target INTEGER DEFAULT 20,
    total_target INTEGER DEFAULT 10000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# 科目表
CREATE_SUBJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#4A7FFF',
    icon TEXT DEFAULT '📚',
    total_count INTEGER DEFAULT 0,
    daily_target INTEGER DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
"""

# 学习记录表
CREATE_STUDY_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS study_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    count INTEGER NOT NULL,
    record_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
)
"""

# 成就定义表
CREATE_ACHIEVEMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    type TEXT NOT NULL,
    rarity TEXT NOT NULL,
    condition TEXT NOT NULL,
    icon TEXT DEFAULT '🏆',
    repeatable INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# 用户成就表
CREATE_USER_ACHIEVEMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    achievement_id INTEGER NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    count INTEGER DEFAULT 1,
    last_achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
)
"""

# AI身份表
CREATE_AI_IDENTITIES_TABLE = """
CREATE TABLE IF NOT EXISTS ai_identities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT DEFAULT 'custom',
    description TEXT,
    system_prompt TEXT,
    color_primary TEXT DEFAULT '#4A7FFF',
    color_accent TEXT DEFAULT '#5DADE2',
    avatar_icon TEXT DEFAULT '🤖',
    tone_style TEXT DEFAULT '友善',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
"""

# AI鼓励记录表
CREATE_AI_ENCOURAGEMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS ai_encouragements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identity_id INTEGER,
    trigger_scene TEXT,
    user_mood TEXT,
    content TEXT NOT NULL,
    response_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (identity_id) REFERENCES ai_identities(id)
)
"""

# API配置表
CREATE_API_CONFIGS_TABLE = """
CREATE TABLE IF NOT EXISTS api_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_type TEXT NOT NULL,
    api_key TEXT NOT NULL,
    base_url TEXT,
    model_id TEXT,
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP
)
"""

# 系统设置表
CREATE_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# 学习会话表
CREATE_STUDY_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    questions_completed INTEGER,
    subject_id INTEGER,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
)
"""

# 所有表的创建语句列表
ALL_TABLES = [
    CREATE_USERS_TABLE,
    CREATE_SUBJECTS_TABLE,
    CREATE_STUDY_RECORDS_TABLE,
    CREATE_ACHIEVEMENTS_TABLE,
    CREATE_USER_ACHIEVEMENTS_TABLE,
    CREATE_AI_IDENTITIES_TABLE,
    CREATE_AI_ENCOURAGEMENTS_TABLE,
    CREATE_API_CONFIGS_TABLE,
    CREATE_SETTINGS_TABLE,
    CREATE_STUDY_SESSIONS_TABLE
]

# 索引创建
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_study_records_date ON study_records(record_date)",
    "CREATE INDEX IF NOT EXISTS idx_study_records_subject ON study_records(subject_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_achievements_achievement ON user_achievements(achievement_id)",
    "CREATE INDEX IF NOT EXISTS idx_ai_encouragements_identity ON ai_encouragements(identity_id)",
    "CREATE INDEX IF NOT EXISTS idx_ai_encouragements_created ON ai_encouragements(created_at)"
]
