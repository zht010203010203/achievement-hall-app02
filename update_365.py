"""快速更新365天成就名字"""
from database.db_manager import DatabaseManager
import json

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

print("🔄 更新365天成就名字...")

# 更新365天成就
cursor.execute("""
    UPDATE achievements 
    SET name = '年度传奇' 
    WHERE type = 'STREAK' AND json_extract(condition, '$.streak_days') = 365
""")

conn.commit()

# 验证
cursor.execute("""
    SELECT name, json_extract(condition, '$.streak_days') as days 
    FROM achievements 
    WHERE type = 'STREAK' AND json_extract(condition, '$.streak_days') = 365
""")

result = cursor.fetchone()
if result:
    print(f"✅ 更新成功！365天成就现在是：{result['name']}")
else:
    print("❌ 未找到365天成就")

print("\n📅 所有打卡成就：")
cursor.execute("""
    SELECT name, json_extract(condition, '$.streak_days') as days
    FROM achievements 
    WHERE type = 'STREAK' 
    ORDER BY days
""")
for row in cursor.fetchall():
    print(f"  {row['name']}: {row['days']}天")
