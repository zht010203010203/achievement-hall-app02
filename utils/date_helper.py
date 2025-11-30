"""日期处理工具"""
from datetime import datetime, date, timedelta
from typing import Tuple


def format_date(date_obj: date, format_str: str = '%Y-%m-%d') -> str:
    """格式化日期"""
    return date_obj.strftime(format_str)


def parse_date(date_str: str, format_str: str = '%Y-%m-%d') -> date:
    """解析日期字符串"""
    return datetime.strptime(date_str, format_str).date()


def get_today() -> date:
    """获取今天的日期"""
    return date.today()


def get_week_range(target_date: date = None) -> Tuple[date, date]:
    """
    获取指定日期所在周的起止日期
    
    Args:
        target_date: 目标日期，默认今天
        
    Returns:
        (周一日期, 周日日期)
    """
    if target_date is None:
        target_date = get_today()
    
    week_start = target_date - timedelta(days=target_date.weekday())
    week_end = week_start + timedelta(days=6)
    
    return week_start, week_end


def get_month_range(target_date: date = None) -> Tuple[date, date]:
    """
    获取指定日期所在月的起止日期
    
    Args:
        target_date: 目标日期，默认今天
        
    Returns:
        (月初日期, 月末日期)
    """
    if target_date is None:
        target_date = get_today()
    
    month_start = date(target_date.year, target_date.month, 1)
    
    if target_date.month == 12:
        month_end = date(target_date.year, 12, 31)
    else:
        next_month = date(target_date.year, target_date.month + 1, 1)
        month_end = next_month - timedelta(days=1)
    
    return month_start, month_end


def days_between(date1: date, date2: date) -> int:
    """计算两个日期之间的天数"""
    return abs((date2 - date1).days)


def format_relative_time(target_datetime: datetime) -> str:
    """
    格式化相对时间
    
    Args:
        target_datetime: 目标时间
        
    Returns:
        相对时间字符串，如 "刚刚"、"5分钟前"、"昨天"
    """
    now = datetime.now()
    diff = now - target_datetime
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "刚刚"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}分钟前"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}小时前"
    elif seconds < 172800:
        return "昨天"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}天前"
    else:
        return target_datetime.strftime('%Y-%m-%d')


def get_weekday_name(date_obj: date, lang: str = 'cn') -> str:
    """
    获取星期名称
    
    Args:
        date_obj: 日期对象
        lang: 语言，'cn' 或 'en'
        
    Returns:
        星期名称
    """
    weekday = date_obj.weekday()
    
    if lang == 'cn':
        names = ['一', '二', '三', '四', '五', '六', '日']
        return f"周{names[weekday]}"
    else:
        names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return names[weekday]
