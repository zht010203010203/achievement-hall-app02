"""学习记录服务"""
from datetime import date, datetime, timedelta
from typing import Dict, Any
from database.db_manager import DatabaseManager


class StudyService:
    """学习记录服务类"""
    
    def __init__(self, db=None):
        """
        初始化学习服务
        
        Args:
            db: 数据库管理器实例（可选，用于多线程）
        """
        self.db = db if db else DatabaseManager()
    
    def add_record(self, subject_id: int, count: int) -> Dict[str, Any]:
        """
        添加学习记录
        
        Args:
            subject_id: 科目ID
            count: 题目数量
            
        Returns:
            包含更新后统计信息的字典
        """
        # 添加记录
        record_id = self.db.add_study_record(subject_id, count)
        
        # 获取更新后的统计信息
        today_progress = self.db.get_today_progress()
        total_count = self.db.get_total_count()
        streak_days = self.db.get_streak_days()
        
        return {
            'record_id': record_id,
            'today_progress': today_progress,
            'total_count': total_count,
            'streak_days': streak_days,
            'added_count': count
        }
    
    def get_today_progress(self) -> Dict[str, Any]:
        """获取今日进度"""
        return self.db.get_today_progress()
    
    def get_total_count(self) -> int:
        """获取总题数"""
        return self.db.get_total_count()
    
    def get_streak_days(self) -> int:
        """获取连续打卡天数"""
        return self.db.get_streak_days()
    
    def get_level_info(self) -> Dict[str, Any]:
        """
        获取等级信息
        
        Returns:
            包含等级、称号、进度的字典
        """
        from config.constants import LEVEL_THRESHOLDS
        
        total_count = self.get_total_count()
        
        # 确定当前等级
        current_level = 0
        current_title = '新手'
        next_threshold = 0
        
        for i, (threshold, title) in enumerate(LEVEL_THRESHOLDS):
            if total_count >= threshold:
                current_level = i
                current_title = title
                # 获取下一级门槛
                if i < len(LEVEL_THRESHOLDS) - 1:
                    next_threshold = LEVEL_THRESHOLDS[i + 1][0]
            else:
                break
        
        # 如果已是最高级
        if current_level == len(LEVEL_THRESHOLDS) - 1:
            next_threshold = LEVEL_THRESHOLDS[-1][0]
            progress_to_next = 100
        else:
            current_threshold = LEVEL_THRESHOLDS[current_level][0]
            if next_threshold > current_threshold:
                progress_to_next = int((total_count - current_threshold) / 
                                     (next_threshold - current_threshold) * 100)
            else:
                progress_to_next = 100
        
        return {
            'level': current_level,
            'title': current_title,
            'total_count': total_count,
            'next_threshold': next_threshold,
            'progress_to_next': progress_to_next,
            'remaining': max(0, next_threshold - total_count)
        }
    
    def get_subject_distribution(self) -> list:
        """获取科目分布"""
        subjects = self.db.get_all_subjects()
        total = sum(s['total_count'] for s in subjects)
        
        if total == 0:
            return []
        
        distribution = []
        for subject in subjects:
            percentage = int(subject['total_count'] / total * 100)
            distribution.append({
                'id': subject['id'],
                'name': subject['name'],
                'count': subject['total_count'],
                'percentage': percentage,
                'color': subject['color'],
                'icon': subject['icon']
            })
        
        return sorted(distribution, key=lambda x: x['count'], reverse=True)
    
    def get_weekly_summary(self) -> Dict[str, Any]:
        """获取本周总结"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # 获取本周每天的数据
        daily_data = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            # 这里简化处理，实际应从数据库查询
            daily_data.append({
                'date': day.strftime('%Y-%m-%d'),
                'count': 0  # 需要从数据库查询
            })
        
        return {
            'week_start': week_start.strftime('%Y-%m-%d'),
            'daily_data': daily_data
        }
    
    def calculate_study_time(self, question_count: int = None) -> str:
        """
        计算学习时长
        
        Args:
            question_count: 题目数量，默认使用总题数
            
        Returns:
            格式化的时长字符串，如 "42h 30m"
        """
        from config.settings import AVG_TIME_PER_QUESTION
        
        if question_count is None:
            question_count = self.get_total_count()
        
        total_minutes = question_count * AVG_TIME_PER_QUESTION
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    def get_last_study_date(self) -> str:
        """获取最后学习日期"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(record_date) as last_date FROM study_records
        """)
        
        result = cursor.fetchone()
        return result['last_date'] if result['last_date'] else None
    
    def get_days_since_last_study(self) -> int:
        """获取距离上次学习的天数"""
        last_date = self.get_last_study_date()
        
        if not last_date:
            return 0
        
        last_date_obj = datetime.strptime(last_date, '%Y-%m-%d').date()
        today = date.today()
        
        return (today - last_date_obj).days
