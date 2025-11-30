import sqlite3
import json

# 直接连接数据库
conn = sqlite3.connect('data/achievement.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("开始更新...")

# 1. 更新365天成就名字
cursor.execute("""
    UPDATE achievements 
    SET name = '年度传奇' 
    WHERE type = 'STREAK' AND json_extract(condition, '$.streak_days') = 365
""")

# 2. 更新速度型成就为可重复
cursor.execute("""
    UPDATE achievements 
    SET repeatable = 1 
    WHERE type = 'SPEED'
""")

# 3. 添加30题速度成就（如果不存在）
cursor.execute("SELECT COUNT(*) FROM achievements WHERE name = '御风而行'")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO achievements (name, description, type, rarity, icon, condition, repeatable)
        VALUES ('御风而行', '单次提交超过30题', 'SPEED', 'BRONZE', '🌪️', '{"single_submit": 30}', 1)
    """)
    print("✅ 已添加30题成就")

# 4. 删除全能型成就
cursor.execute("DELETE FROM achievements WHERE type = 'VERSATILE'")

conn.commit()

print("✅ 更新完成！")

# 显示结果
cursor.execute("SELECT name FROM achievements WHERE type = 'STREAK' AND json_extract(condition, '$.streak_days') = 365")
result = cursor.fetchone()
print(f"365天成就：{result['name']}")

cursor.execute("SELECT name, repeatable FROM achievements WHERE type = 'SPEED' ORDER BY json_extract(condition, '$.single_submit')")
print("\n速度型成就：")
for row in cursor.fetchall():
    print(f"  {row['name']} (可重复: {'是' if row['repeatable'] else '否'})")

conn.close()
