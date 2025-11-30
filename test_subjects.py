"""测试科目显示"""
from database.db_manager import DatabaseManager

db = DatabaseManager()

# 获取所有科目
subjects = db.get_all_subjects()

print("=" * 50)
print("数据库中的科目：")
for s in subjects:
    name = s['name']
    print(f"ID={s['id']}, 名称='{name}', 字节长度={len(name.encode('utf-8'))}")
    print(f"  Unicode: {[hex(ord(c)) for c in name]}")
    print(f"  总题数: {s['total_count']}, 目标: {s.get('daily_target', '未设置')}")
print("=" * 50)
