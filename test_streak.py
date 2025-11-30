"""测试连续打卡计算"""
from database.db_manager import DatabaseManager
from datetime import date

db = DatabaseManager()

# 获取所有打卡记录
print("=" * 50)
print("所有打卡记录（按时间倒序）：")
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT DISTINCT record_date 
    FROM study_records 
    ORDER BY record_date DESC
    LIMIT 15
""")
dates = [row['record_date'] for row in cursor.fetchall()]
for i, d in enumerate(dates):
    print(f"  {i}: {d}")

# 测试连续打卡天数
print("\n" + "=" * 50)
print(f"今天日期: {date.today()}")
streak = db.get_streak_days()
print(f"连续打卡天数: {streak} 天")
print("=" * 50)
