"""数据库管理器"""
import sqlite3
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from config.settings import DATABASE_PATH
from config.constants import PRESET_ACHIEVEMENTS, PRESET_AI_IDENTITIES
from .models import ALL_TABLES, CREATE_INDEXES


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 返回字典格式
        return self.connection
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self):
        """初始化数据库"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 创建所有表
            for table_sql in ALL_TABLES:
                cursor.execute(table_sql)
            
            # 创建索引
            for index_sql in CREATE_INDEXES:
                cursor.execute(index_sql)
            
            conn.commit()
            
            # 数据库迁移：添加科目的daily_target字段
            self.migrate_add_subject_daily_target()
            
            # 数据库迁移：添加科目的total_target字段
            self.migrate_add_subject_total_target()
            
            # 数据库迁移：升级成就系统支持计数
            self.migrate_achievement_count()
            
            # 数据库迁移：添加成就可重复标记
            self.migrate_achievement_repeatable()
            
            # 初始化默认数据
            self._initialize_default_data()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"数据库初始化失败: {e}")
    
    def migrate_add_subject_daily_target(self):
        """迁移：给subjects表添加daily_target字段"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查字段是否存在
            cursor.execute("PRAGMA table_info(subjects)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'daily_target' not in columns:
                print("[INFO] 迁移：添加subjects.daily_target字段")
                cursor.execute("ALTER TABLE subjects ADD COLUMN daily_target INTEGER DEFAULT 20")
                conn.commit()
                print("[OK] 迁移成功")
        except Exception as e:
            print(f"[WARN] 迁移失败（可能字段已存在）: {e}")
    
    def migrate_add_subject_total_target(self):
        """迁移：给subjects表添加total_target字段"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查字段是否存在
            cursor.execute("PRAGMA table_info(subjects)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'total_target' not in columns:
                print("[INFO] 迁移：添加subjects.total_target字段")
                cursor.execute("ALTER TABLE subjects ADD COLUMN total_target INTEGER DEFAULT 0")
                conn.commit()
                print("[OK] 迁移成功：subjects.total_target")
        except Exception as e:
            print(f"[WARN] 迁移失败（可能字段已存在）: {e}")
    
    def migrate_achievement_count(self):
        """迁移：升级成就系统支持计数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查字段是否存在
            cursor.execute("PRAGMA table_info(user_achievements)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'count' not in columns:
                print("[INFO] 迁移：升级成就系统支持计数")
                cursor.execute("ALTER TABLE user_achievements ADD COLUMN count INTEGER DEFAULT 1")
                cursor.execute("ALTER TABLE user_achievements ADD COLUMN last_achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                conn.commit()
                print("[OK] 成就系统升级成功")
        except Exception as e:
            print(f"[WARN] 迁移失败（可能字段已存在）: {e}")
    
    def migrate_achievement_repeatable(self):
        """迁移：添加成就可重复标记"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查字段是否存在
            cursor.execute("PRAGMA table_info(achievements)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'repeatable' not in columns:
                print("[INFO] 迁移：添加成就可重复标记")
                cursor.execute("ALTER TABLE achievements ADD COLUMN repeatable INTEGER DEFAULT 0")
                conn.commit()
                print("[OK] 成就可重复标记添加成功")
        except Exception as e:
            print(f"[WARN] 迁移失败（可能字段已存在）: {e}")
    
    def _initialize_default_data(self):
        """初始化默认数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已初始化
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                # 创建默认用户
                cursor.execute("INSERT INTO users (daily_target, total_target) VALUES (20, 10000)")
            
            # 初始化预设成就
            cursor.execute("SELECT COUNT(*) FROM achievements")
            if cursor.fetchone()[0] == 0:
                for achievement in PRESET_ACHIEVEMENTS:
                    cursor.execute("""
                        INSERT INTO achievements (name, description, type, rarity, icon, condition, repeatable)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        achievement['name'],
                        achievement['description'],
                        achievement['type'],
                        achievement['rarity'],
                        achievement['icon'],
                        json.dumps(achievement['condition']),
                        1 if achievement.get('repeatable', False) else 0
                    ))
            
            # 初始化预设AI身份
            cursor.execute("SELECT COUNT(*) FROM ai_identities")
            if cursor.fetchone()[0] == 0:
                for identity in PRESET_AI_IDENTITIES:
                    cursor.execute("""
                        INSERT INTO ai_identities 
                        (name, type, description, system_prompt, color_primary, color_accent, tone_style)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        identity['name'],
                        identity['type'],
                        identity['description'],
                        identity['system_prompt'],
                        identity['color_primary'],
                        identity['color_accent'],
                        identity['tone_style']
                    ))
            
            # 初始化默认科目
            cursor.execute("SELECT COUNT(*) FROM subjects")
            if cursor.fetchone()[0] == 0:
                default_subjects = [
                    ('算法训练', '#4A7FFF', '💻'),
                    ('数学专题', '#27AE60', '📐'),
                    ('英语阅读', '#E67E22', '📖')
                ]
                for name, color, icon in default_subjects:
                    cursor.execute("""
                        INSERT INTO subjects (name, color, icon)
                        VALUES (?, ?, ?)
                    """, (name, color, icon))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"默认数据初始化失败: {e}")
    
    # ==================== 学习记录相关 ====================
    
    def add_study_record(self, subject_id: int, count: int, record_date: date = None) -> int:
        """添加学习记录"""
        if record_date is None:
            record_date = date.today()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查当天是否已有记录
            cursor.execute("""
                SELECT id, count FROM study_records 
                WHERE subject_id = ? AND record_date = ?
            """, (subject_id, record_date))
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                new_count = existing['count'] + count
                cursor.execute("""
                    UPDATE study_records SET count = ? WHERE id = ?
                """, (new_count, existing['id']))
                record_id = existing['id']
            else:
                # 创建新记录
                cursor.execute("""
                    INSERT INTO study_records (subject_id, count, record_date)
                    VALUES (?, ?, ?)
                """, (subject_id, count, record_date))
                record_id = cursor.lastrowid
            
            # 更新科目总数
            cursor.execute("""
                UPDATE subjects SET total_count = total_count + ? WHERE id = ?
            """, (count, subject_id))
            
            conn.commit()
            return record_id
            
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] 添加学习记录失败: {e}")
            raise Exception(f"添加学习记录失败: {e}")
    
    def get_today_progress(self) -> Dict[str, Any]:
        """获取今日进度"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today()
        
        # 获取今日完成数
        cursor.execute("""
            SELECT COALESCE(SUM(count), 0) as today_count
            FROM study_records
            WHERE record_date = ?
        """, (today,))
        
        today_count = cursor.fetchone()['today_count']
        
        # 获取每日目标
        cursor.execute("SELECT daily_target FROM users LIMIT 1")
        daily_target = cursor.fetchone()['daily_target']
        
        return {
            'current': today_count,
            'target': daily_target,
            'percentage': min(100, int(today_count / daily_target * 100)) if daily_target > 0 else 0
        }
    
    def get_total_count(self) -> int:
        """获取总题数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COALESCE(SUM(total_count), 0) as total FROM subjects")
        return cursor.fetchone()['total']
    
    def get_streak_days(self) -> int:
        """获取连续打卡天数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT record_date 
            FROM study_records 
            ORDER BY record_date DESC
        """)
        
        dates = [row['record_date'] for row in cursor.fetchall()]
        
        if not dates:
            return 0
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # 转换日期字符串为date对象
        date_objs = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]
        
        # 判断起始日期：如果今天有记录，从今天开始；否则从昨天开始
        if date_objs[0] == today:
            start_date = today
            streak = 1
            check_from_index = 1
        elif date_objs[0] == yesterday:
            start_date = yesterday
            streak = 1
            check_from_index = 1
        else:
            # 最近的记录既不是今天也不是昨天，连续打卡已断
            return 0
        
        # 从第二个日期开始往前检查连续性
        for i in range(check_from_index, len(date_objs)):
            expected_date = start_date - timedelta(days=i)
            if date_objs[i] == expected_date:
                streak += 1
            else:
                break
        
        return streak
    
    def get_heatmap_data(self, year: int = None) -> List[Dict]:
        """获取热力图数据（最近365天）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取最近365天的数据（不限制年份）
        from datetime import timedelta
        today = date.today()
        start_date = today - timedelta(days=364)
        
        print(f"[DEBUG] 查询热力图数据：从{start_date}到{today}")
        
        cursor.execute("""
            SELECT record_date, SUM(count) as count
            FROM study_records
            WHERE record_date >= ? AND record_date <= ?
            GROUP BY record_date
        """, (start_date, today))
        
        results = [dict(row) for row in cursor.fetchall()]
        print(f"[DEBUG] 查询到{len(results)}天有记录")
        if results:
            print(f"[DEBUG] 最早记录：{results[0]}, 最晚记录：{results[-1]}")
        return results
    
    # ==================== 科目管理 ====================
    
    def get_all_subjects(self) -> List[Dict]:
        """获取所有科目"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM subjects WHERE is_active = 1 ORDER BY created_at
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_subject_today_progress(self, subject_id: int) -> Dict[str, Any]:
        """获取科目今日进度"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today()
        
        # 获取科目今日完成数
        cursor.execute("""
            SELECT COALESCE(SUM(count), 0) as today_count
            FROM study_records
            WHERE subject_id = ? AND record_date = ?
        """, (subject_id, today))
        
        today_count = cursor.fetchone()['today_count']
        
        # 获取科目每日目标
        cursor.execute("SELECT daily_target, name FROM subjects WHERE id = ?", (subject_id,))
        subject = cursor.fetchone()
        if not subject:
            return {'current': 0, 'target': 20, 'percentage': 0, 'name': ''}
        
        daily_target = subject['daily_target']
        
        return {
            'current': today_count,
            'target': daily_target,
            'percentage': min(100, int(today_count / daily_target * 100)) if daily_target > 0 else 0,
            'name': subject['name']
        }
    
    def update_subject_target(self, subject_id: int, daily_target: int):
        """更新科目每日目标"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE subjects 
                SET daily_target = ?
                WHERE id = ?
            """, (daily_target, subject_id))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                raise Exception(f"科目ID {subject_id} 不存在")
                
        except Exception as e:
            conn.rollback()
            raise Exception(f"更新科目目标失败: {e}")
    
    def add_subject(self, name: str, color: str = '#4A7FFF', icon: str = '📚') -> int:
        """添加科目"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO subjects (name, color, icon)
                VALUES (?, ?, ?)
            """, (name, color, icon))
            
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            raise Exception(f"科目 '{name}' 已存在")
        except Exception as e:
            conn.rollback()
            raise Exception(f"添加科目失败: {e}")
    
    def update_subject(self, subject_id: int, name: str):
        """更新科目名称"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE subjects 
                SET name = ?
                WHERE id = ?
            """, (name, subject_id))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                raise Exception("科目不存在")
            
            print(f"[INFO] 已更新科目: ID={subject_id}, 新名称={name}")
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"更新科目失败: {e}")
    
    def delete_subject(self, subject_id: int):
        """删除科目（硬删除，同时删除相关记录）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 先删除该科目的所有学习记录
            cursor.execute("DELETE FROM study_records WHERE subject_id = ?", (subject_id,))
            
            # 再删除科目
            cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                raise Exception("科目不存在")
            
            print(f"[INFO] 已删除科目: ID={subject_id}")
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"删除科目失败: {e}")
    
    # ==================== 成就系统 ====================
    
    def get_all_achievements(self) -> List[Dict]:
        """获取所有成就"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.*, ua.unlocked_at,
                   CASE WHEN ua.id IS NOT NULL THEN 1 ELSE 0 END as is_unlocked
            FROM achievements a
            LEFT JOIN user_achievements ua ON a.id = ua.achievement_id
            ORDER BY a.id
        """)
        
        achievements = []
        for row in cursor.fetchall():
            achievement = dict(row)
            achievement['condition'] = json.loads(achievement['condition'])
            achievements.append(achievement)
        
        return achievements
    
    def unlock_achievement(self, achievement_id: int, repeatable: bool = False) -> Dict[str, Any]:
        """
        解锁成就（支持可重复成就）
        
        Args:
            achievement_id: 成就ID
            repeatable: 是否为可重复成就
            
        Returns:
            包含解锁信息的字典：{'unlocked': bool, 'count': int, 'is_first': bool}
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已解锁
            cursor.execute("""
                SELECT id, count FROM user_achievements WHERE achievement_id = ?
            """, (achievement_id,))
            
            existing = cursor.fetchone()
            
            if existing and not repeatable:
                # 不可重复成就已解锁
                return {'unlocked': False, 'count': existing['count'], 'is_first': False}
            
            if existing and repeatable:
                # 可重复成就，增加计数
                new_count = existing['count'] + 1
                cursor.execute("""
                    UPDATE user_achievements 
                    SET count = ?, last_achieved_at = CURRENT_TIMESTAMP
                    WHERE achievement_id = ?
                """, (new_count, achievement_id))
                conn.commit()
                return {'unlocked': True, 'count': new_count, 'is_first': False}
            
            # 首次解锁成就
            cursor.execute("""
                INSERT INTO user_achievements (achievement_id, count) VALUES (?, 1)
            """, (achievement_id,))
            
            conn.commit()
            return {'unlocked': True, 'count': 1, 'is_first': True}
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"解锁成就失败: {e}")
    
    # ==================== AI系统 ====================
    
    def get_all_ai_identities(self) -> List[Dict]:
        """获取所有AI身份"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ai_identities WHERE is_active = 1 ORDER BY type, created_at
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def add_ai_identity(self, name: str, description: str, system_prompt: str,
                       color_primary: str = '#4A7FFF', tone_style: str = '友善') -> int:
        """添加自定义AI身份"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ai_identities 
                (name, type, description, system_prompt, color_primary, tone_style)
                VALUES (?, 'custom', ?, ?, ?, ?)
            """, (name, description, system_prompt, color_primary, tone_style))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"添加AI身份失败: {e}")
    
    def update_ai_identity(self, identity_id: int, system_prompt: str):
        """更新AI身份的提示词"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE ai_identities 
                SET system_prompt = ?
                WHERE id = ?
            """, (system_prompt, identity_id))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                raise Exception("AI身份不存在")
            
            print(f"[INFO] 已更新AI身份: ID={identity_id}")
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"更新AI身份失败: {e}")
    
    def delete_ai_identity(self, identity_id: int):
        """删除AI身份（所有身份都可以删除）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 删除AI身份（包括系统预设）
            cursor.execute("""
                DELETE FROM ai_identities 
                WHERE id = ?
            """, (identity_id,))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                raise Exception("AI身份不存在")
            
            print(f"[INFO] 已删除AI身份: ID={identity_id}")
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"删除AI身份失败: {e}")
    
    def save_ai_encouragement(self, identity_id: int, trigger_scene: str, 
                             content: str, response_time: float = None,
                             user_mood: str = None) -> int:
        """保存AI鼓励记录（只保留最新3条）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 保存新记录
            cursor.execute("""
                INSERT INTO ai_encouragements 
                (identity_id, trigger_scene, content, response_time, user_mood)
                VALUES (?, ?, ?, ?, ?)
            """, (identity_id, trigger_scene, content, response_time, user_mood))
            
            new_id = cursor.lastrowid
            
            # 只保留最新的3条记录，删除旧的
            cursor.execute("""
                DELETE FROM ai_encouragements 
                WHERE id NOT IN (
                    SELECT id FROM ai_encouragements 
                    ORDER BY created_at DESC 
                    LIMIT 3
                )
            """)
            
            conn.commit()
            print(f"[INFO] AI鼓励已保存，自动清理旧记录，只保留最新3条")
            return new_id
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"保存AI鼓励失败: {e}")
    
    def get_ai_encouragement_history(self, limit: int = 50) -> List[Dict]:
        """获取AI鼓励历史"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.*, i.name as identity_name, i.color_primary
            FROM ai_encouragements e
            LEFT JOIN ai_identities i ON e.identity_id = i.id
            ORDER BY e.created_at DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== API配置 ====================
    
    def save_api_config(self, platform_type: str, api_key: str, 
                       base_url: str, model_id: str) -> int:
        """保存API配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 先取消其他配置的默认状态
            cursor.execute("UPDATE api_configs SET is_default = 0")
            
            # 保存新配置
            cursor.execute("""
                INSERT INTO api_configs (platform_type, api_key, base_url, model_id, is_default)
                VALUES (?, ?, ?, ?, 1)
            """, (platform_type, api_key, base_url, model_id))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"保存API配置失败: {e}")
    
    def get_default_api_config(self) -> Optional[Dict]:
        """获取默认API配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM api_configs WHERE is_default = 1 LIMIT 1
        """)
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # ==================== 设置管理 ====================
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取设置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        return row['value'] if row else default
    
    def set_setting(self, key: str, value: Any):
        """设置配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, str(value)))
        
        conn.commit()
    
    def get_user_config(self) -> Dict:
        """获取用户配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users LIMIT 1")
        row = cursor.fetchone()
        
        return dict(row) if row else {'daily_target': 20, 'total_target': 10000}
    
    def update_user_config(self, daily_target: int = None, total_target: int = None):
        """更新用户配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if daily_target is not None:
            updates.append("daily_target = ?")
            params.append(daily_target)
        
        if total_target is not None:
            updates.append("total_target = ?")
            params.append(total_target)
        
        if updates:
            cursor.execute(f"""
                UPDATE users SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            """, params)
            conn.commit()
