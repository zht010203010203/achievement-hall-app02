"""统计分析服务"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from database.db_manager import DatabaseManager
from .study_service import StudyService


class StatsService:
    """统计分析服务类"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.study_service = StudyService()
    
    def get_heatmap_data(self, year: int = None) -> List[Dict]:
        """
        获取热力图数据
        
        Args:
            year: 年份，默认当前年
            
        Returns:
            热力图数据列表，包含打卡状态和目标完成情况
        """
        if year is None:
            year = datetime.now().year
        
        raw_data = self.db.get_heatmap_data(year)
        
        # 转换为字典便于查找
        data_dict = {item['record_date']: item['count'] for item in raw_data}
        
        # 获取每日目标
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT daily_target FROM users LIMIT 1")
        daily_target = cursor.fetchone()['daily_target']
        
        # 从今天往前推365天（而不是从1月1日开始）
        today = date.today()
        start_date = today - timedelta(days=364)  # 包括今天共365天
        heatmap_data = []
        
        for i in range(365):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            count = data_dict.get(date_str, 0)
            
            # 计算等级：
            # 0 - 没打卡（灰色）
            # 1 - 打卡但未完成目标（淡蓝色）
            # 2 - 完成目标（深蓝色）
            if count == 0:
                level = 0  # 未打卡
            elif count < daily_target:
                level = 1  # 打卡未完成
            else:
                level = 2  # 完成目标
            
            heatmap_data.append({
                'date': date_str,
                'count': count,
                'level': level,
                'weekday': current_date.weekday(),
                'target_completed': count >= daily_target if count > 0 else False
            })
        
        return heatmap_data
    
    def get_weekly_trend(self) -> Dict[str, Any]:
        """
        获取本周趋势数据
        
        Returns:
            包含每日数据的字典
        """
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        daily_data = []
        total_week = 0
        
        for i in range(7):
            day = week_start + timedelta(days=i)
            date_str = day.strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT COALESCE(SUM(count), 0) as count
                FROM study_records
                WHERE record_date = ?
            """, (date_str,))
            
            count = cursor.fetchone()['count']
            total_week += count
            
            daily_data.append({
                'date': date_str,
                'weekday': day.strftime('%a'),
                'weekday_cn': ['一', '二', '三', '四', '五', '六', '日'][i],
                'count': count,
                'is_today': day == today
            })
        
        avg_daily = total_week / 7 if total_week > 0 else 0
        
        return {
            'week_start': week_start.strftime('%Y-%m-%d'),
            'daily_data': daily_data,
            'total_week': total_week,
            'avg_daily': round(avg_daily, 1)
        }
    
    def get_monthly_trend(self) -> Dict[str, Any]:
        """
        获取本月趋势数据
        
        Returns:
            包含每日数据的字典
        """
        today = date.today()
        month_start = date(today.year, today.month, 1)
        
        # 计算本月天数
        if today.month == 12:
            next_month = date(today.year + 1, 1, 1)
        else:
            next_month = date(today.year, today.month + 1, 1)
        
        days_in_month = (next_month - month_start).days
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        daily_data = []
        total_month = 0
        
        for i in range(days_in_month):
            day = month_start + timedelta(days=i)
            date_str = day.strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT COALESCE(SUM(count), 0) as count
                FROM study_records
                WHERE record_date = ?
            """, (date_str,))
            
            count = cursor.fetchone()['count']
            total_month += count
            
            daily_data.append({
                'date': date_str,
                'day': i + 1,
                'count': count,
                'is_today': day == today
            })
        
        avg_daily = total_month / days_in_month if total_month > 0 else 0
        
        return {
            'month_start': month_start.strftime('%Y-%m-%d'),
            'daily_data': daily_data,
            'total_month': total_month,
            'avg_daily': round(avg_daily, 1),
            'days_in_month': days_in_month
        }
    
    def get_subject_stats(self) -> List[Dict]:
        """
        获取科目统计
        
        Returns:
            科目统计列表
        """
        subjects = self.db.get_all_subjects()
        total = sum(s['total_count'] for s in subjects)
        
        stats = []
        for subject in subjects:
            percentage = int(subject['total_count'] / total * 100) if total > 0 else 0
            
            stats.append({
                'id': subject['id'],
                'name': subject['name'],
                'count': subject['total_count'],
                'percentage': percentage,
                'color': subject['color'],
                'icon': subject['icon']
            })
        
        return sorted(stats, key=lambda x: x['count'], reverse=True)
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """
        获取总览统计数据
        
        Returns:
            包含各种统计指标的字典
        """
        total_count = self.study_service.get_total_count()
        today_progress = self.study_service.get_today_progress()
        streak_days = self.study_service.get_streak_days()
        level_info = self.study_service.get_level_info()
        study_time = self.study_service.calculate_study_time()
        
        # 获取本周和本月数据
        weekly = self.get_weekly_trend()
        monthly = self.get_monthly_trend()
        
        return {
            'total_count': total_count,
            'today_current': today_progress['current'],
            'today_target': today_progress['target'],
            'today_percentage': today_progress['percentage'],
            'streak_days': streak_days,
            'level': level_info['level'],
            'level_title': level_info['title'],
            'study_time': study_time,
            'week_total': weekly['total_week'],
            'week_avg': weekly['avg_daily'],
            'month_total': monthly['total_month'],
            'month_avg': monthly['avg_daily']
        }
    
    def get_date_detail(self, target_date: str) -> Dict[str, Any]:
        """
        获取指定日期的详细数据
        
        Args:
            target_date: 日期字符串 'YYYY-MM-DD'
            
        Returns:
            该日期的详细统计
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 获取该日期的所有记录
        cursor.execute("""
            SELECT sr.count, s.name, s.color, s.icon
            FROM study_records sr
            JOIN subjects s ON sr.subject_id = s.id
            WHERE sr.record_date = ?
        """, (target_date,))
        
        records = [dict(row) for row in cursor.fetchall()]
        
        total_count = sum(r['count'] for r in records)
        study_time = self.study_service.calculate_study_time(total_count)
        
        return {
            'date': target_date,
            'total_count': total_count,
            'study_time': study_time,
            'records': records
        }
    
    def get_best_streak(self) -> int:
        """
        获取历史最佳连续天数
        
        Returns:
            最长连续天数
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT record_date 
            FROM study_records 
            ORDER BY record_date
        """)
        
        dates = [row['record_date'] for row in cursor.fetchall()]
        
        if not dates:
            return 0
        
        max_streak = 1
        current_streak = 1
        
        for i in range(len(dates) - 1):
            current_date = datetime.strptime(dates[i], '%Y-%m-%d').date()
            next_date = datetime.strptime(dates[i + 1], '%Y-%m-%d').date()
            
            if (next_date - current_date).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    def get_total_days_studied(self) -> int:
        """
        获取总学习天数
        
        Returns:
            总学习天数
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT record_date) as days
            FROM study_records
        """)
        
        return cursor.fetchone()['days']
