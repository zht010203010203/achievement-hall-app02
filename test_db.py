"""测试数据库内容"""
import sqlite3
from datetime import date

db_path = "d:/OneDrive/桌面/文件/程序/刷题app/data/achievement.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("="*60)
print("查看数据库中的学习记录")
print("="*60)

# 查看所有记录
cursor.execute("SELECT * FROM study_records ORDER BY record_date DESC")
records = cursor.fetchall()

print(f"\n总记录数：{len(records)}")
print(f"今天日期：{date.today()}\n")

print("最近10条记录：")
for rec in records[:10]:
    print(f"  ID={rec['id']}, 日期={rec['record_date']}, 科目={rec['subject_id']}, 数量={rec['count']}")

# 按日期汇总
cursor.execute("""
    SELECT record_date, SUM(count) as total_count
    FROM study_records
    GROUP BY record_date
    ORDER BY record_date DESC
    LIMIT 10
""")

print("\n按日期汇总（最近10天）：")
for rec in cursor.fetchall():
    print(f"  日期={rec['record_date']}, 总数={rec['total_count']}")

conn.close()
