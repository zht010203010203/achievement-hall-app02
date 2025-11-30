"""重置成就系统（添加新成就）"""
from database.db_manager import DatabaseManager
from config.constants import PRESET_ACHIEVEMENTS
import json

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

print("🔄 开始重置成就系统...")

# 清空现有成就定义（保留用户已获得的成就记录）
cursor.execute("DELETE FROM achievements")
print("✅ 已清空旧成就定义")

# 重新插入所有成就
for achievement in PRESET_ACHIEVEMENTS:
    cursor.execute("""
        INSERT INTO achievements (name, description, type, rarity, icon, condition, repeatable)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        achievement['name'],
        achievement['description'],
        achievement['type'],
        achievement['rarity'],
        achievement['icon'],
        json.dumps(achievement['condition']),
        1 if achievement.get('repeatable', False) else 0
    ))

conn.commit()

# 统计成就数量
cursor.execute("SELECT COUNT(*) FROM achievements")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM achievements WHERE repeatable = 1")
repeatable_count = cursor.fetchone()[0]

print(f"\n✅ 成就系统重置完成！")
print(f"📊 总成就数：{total}")
print(f"♻️  可重复成就：{repeatable_count}")
print(f"🏆 一次性成就：{total - repeatable_count}")

# 显示数量型成就阶梯
cursor.execute("""
    SELECT name, json_extract(condition, '$.total_count') as target
    FROM achievements 
    WHERE type = 'QUANTITY' 
    ORDER BY target
""")

print(f"\n📈 数量型成就阶梯：")
for row in cursor.fetchall():
    print(f"  {row['name']}: {row['target']}题")

print("\n🎉 现在运行程序即可看到新成就！")
