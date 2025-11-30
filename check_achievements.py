"""检查成就系统"""
from database.db_manager import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

print("📊 数量型成就（20个）：")
cursor.execute("""
    SELECT name, json_extract(condition, '$.total_count') as target
    FROM achievements 
    WHERE type = 'QUANTITY' 
    ORDER BY target
""")
for row in cursor.fetchall():
    print(f"  {row['name']}: {row['target']}题")

print("\n📅 连续打卡成就（9个）：")
cursor.execute("""
    SELECT name, json_extract(condition, '$.streak_days') as days, repeatable
    FROM achievements 
    WHERE type = 'STREAK' 
    ORDER BY days
""")
for row in cursor.fetchall():
    repeat_mark = "♻️" if row['repeatable'] else "❌"
    print(f"  {row['name']}: {row['days']}天 {repeat_mark}")

print("\n⚡ 速度型成就（3个）：")
cursor.execute("""
    SELECT name, json_extract(condition, '$.single_submit') as target
    FROM achievements 
    WHERE type = 'SPEED' 
    ORDER BY target
""")
for row in cursor.fetchall():
    print(f"  {row['name']}: 单次{row['target']}题")

print("\n🌟 全能型成就（3个）：")
cursor.execute("""
    SELECT name, json_extract(condition, '$.all_subjects') as target
    FROM achievements 
    WHERE type = 'VERSATILE' 
    ORDER BY target
""")
for row in cursor.fetchall():
    print(f"  {row['name']}: 所有科目≥{row['target']}题")

cursor.execute("SELECT COUNT(*) FROM achievements")
total = cursor.fetchone()[0]
print(f"\n✅ 总成就数：{total}")
