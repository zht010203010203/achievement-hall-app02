"""成就系统服务"""
import json
from typing import List, Dict, Any
from database.db_manager import DatabaseManager
from .study_service import StudyService


class AchievementService:
    """成就系统服务类"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.study_service = StudyService()
    
    def check_achievements(self) -> List[Dict[str, Any]]:
        """
        检查并解锁成就（支持可重复成就）
        
        Returns:
            新解锁的成就列表
        """
        newly_unlocked = []
        
        # 获取所有成就
        achievements = self.db.get_all_achievements()
        
        # 获取当前统计数据
        total_count = self.study_service.get_total_count()
        streak_days = self.study_service.get_streak_days()
        today_progress = self.study_service.get_today_progress()
        
        for achievement in achievements:
            # 检查是否可重复
            repeatable = achievement.get('repeatable', False)
            
            # 如果不可重复且已解锁，跳过
            if not repeatable and achievement['is_unlocked']:
                continue
            
            # 检查是否满足条件
            if self._check_condition(achievement, total_count, streak_days, today_progress):
                # 尝试解锁成就
                result = self.db.unlock_achievement(achievement['id'], repeatable)
                
                if result['unlocked']:
                    # 添加解锁信息
                    achievement['count'] = result['count']
                    achievement['is_first'] = result['is_first']
                    newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def _check_condition(self, achievement: Dict, total_count: int, 
                        streak_days: int, today_progress: Dict) -> bool:
        """
        检查成就条件是否满足
        
        Args:
            achievement: 成就信息
            total_count: 总题数
            streak_days: 连续天数
            today_progress: 今日进度
            
        Returns:
            是否满足条件
        """
        condition = achievement['condition']
        achievement_type = achievement['type']
        
        if achievement_type == 'QUANTITY':
            # 数量型成就
            if 'total_count' in condition:
                return total_count >= condition['total_count']
        
        elif achievement_type == 'STREAK':
            # 连续型成就
            if 'streak_days' in condition:
                return streak_days >= condition['streak_days']
        
        elif achievement_type == 'SPEED':
            # 速度型成就
            if 'single_submit' in condition:
                # 这个需要在添加记录时检查
                # 这里简化处理，返回False
                return False
        
        elif achievement_type == 'VERSATILE':
            # 全能型成就
            if 'all_subjects' in condition:
                subjects = self.db.get_all_subjects()
                threshold = condition['all_subjects']
                return all(s['total_count'] >= threshold for s in subjects)
        
        return False
    
    def check_speed_achievement(self, count: int) -> List[Dict[str, Any]]:
        """
        检查速度型成就（单次提交）
        
        Args:
            count: 单次提交的题目数
            
        Returns:
            新解锁的速度型成就列表
        """
        newly_unlocked = []
        achievements = self.db.get_all_achievements()
        
        for achievement in achievements:
            if achievement['type'] != 'SPEED':
                continue
            
            # 检查是否可重复
            repeatable = achievement.get('repeatable', False)
            
            # 如果不可重复且已解锁，跳过
            if not repeatable and achievement['is_unlocked']:
                continue
            
            condition = achievement['condition']
            if 'single_submit' in condition:
                if count >= condition['single_submit']:
                    result = self.db.unlock_achievement(achievement['id'], repeatable)
                    if result['unlocked']:
                        achievement['count'] = result['count']
                        achievement['is_first'] = result['is_first']
                        newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def get_all_achievements(self) -> Dict[str, List[Dict]]:
        """
        获取所有成就，按状态分类
        
        Returns:
            包含 unlocked 和 locked 两个列表的字典
        """
        achievements = self.db.get_all_achievements()
        
        unlocked = [a for a in achievements if a['is_unlocked']]
        locked = [a for a in achievements if not a['is_unlocked']]
        
        return {
            'unlocked': unlocked,
            'locked': locked,
            'total': len(achievements),
            'unlocked_count': len(unlocked)
        }
    
    def get_achievement_progress(self, achievement_id: int) -> Dict[str, Any]:
        """
        获取成就进度
        
        Args:
            achievement_id: 成就ID
            
        Returns:
            包含进度信息的字典
        """
        achievements = self.db.get_all_achievements()
        achievement = next((a for a in achievements if a['id'] == achievement_id), None)
        
        if not achievement:
            return None
        
        if achievement['is_unlocked']:
            return {
                'progress': 100,
                'current': achievement['condition'].get('total_count', 0),
                'target': achievement['condition'].get('total_count', 0),
                'unlocked': True
            }
        
        # 计算进度
        condition = achievement['condition']
        achievement_type = achievement['type']
        
        total_count = self.study_service.get_total_count()
        streak_days = self.study_service.get_streak_days()
        
        if achievement_type == 'QUANTITY':
            target = condition.get('total_count', 0)
            current = min(total_count, target)
            progress = int(current / target * 100) if target > 0 else 0
            
            return {
                'progress': progress,
                'current': current,
                'target': target,
                'remaining': max(0, target - current),
                'unlocked': False
            }
        
        elif achievement_type == 'STREAK':
            target = condition.get('streak_days', 0)
            current = min(streak_days, target)
            progress = int(current / target * 100) if target > 0 else 0
            
            return {
                'progress': progress,
                'current': current,
                'target': target,
                'remaining': max(0, target - current),
                'unlocked': False
            }
        
        return {
            'progress': 0,
            'current': 0,
            'target': 0,
            'unlocked': False
        }
    
    def get_achievement_stats(self) -> Dict[str, Any]:
        """
        获取成就统计信息
        
        Returns:
            成就统计数据
        """
        from config.constants import ACHIEVEMENT_RARITY
        
        achievements = self.db.get_all_achievements()
        
        # 按稀有度统计
        rarity_stats = {rarity: {'total': 0, 'unlocked': 0} 
                       for rarity in ACHIEVEMENT_RARITY.keys()}
        
        for achievement in achievements:
            rarity = achievement['rarity']
            if rarity in rarity_stats:
                rarity_stats[rarity]['total'] += 1
                if achievement['is_unlocked']:
                    rarity_stats[rarity]['unlocked'] += 1
        
        # 计算总体完成率
        total = len(achievements)
        unlocked = sum(1 for a in achievements if a['is_unlocked'])
        completion_rate = int(unlocked / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'unlocked': unlocked,
            'completion_rate': completion_rate,
            'rarity_stats': rarity_stats
        }
