"""测试数据清除"""
from database.db_manager import DatabaseManager

db = DatabaseManager()

# 查询当前总题数
total = db.get_total_count()
print(f"当前总题数: {total}")

# 查询study_records表记录数
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM study_records")
count = cursor.fetchone()[0]
print(f"study_records记录数: {count}")

# 查询今日题数
from datetime import date
today = date.today().strftime('%Y-%m-%d')
cursor.execute("SELECT COALESCE(SUM(count), 0) FROM study_records WHERE DATE(record_date) = ?", (today,))
today_count = cursor.fetchone()[0]
print(f"今日题数: {today_count}")
