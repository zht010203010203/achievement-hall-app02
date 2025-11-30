"""测试AI历史记录"""
from database.db_manager import DatabaseManager

db = DatabaseManager()
history = db.get_ai_encouragement_history(20)

print(f"=== AI鼓励历史记录 ===")
print(f"总记录数: {len(history)}")
print()

if history:
    for i, h in enumerate(history[:10], 1):
        print(f"{i}. [{h.get('identity_name', 'AI')}]")
        print(f"   完整内容: [{h['content']}]")
        print(f"   内容长度: {len(h['content'])} 字符")
        print(f"   时间: {h['created_at']}")
        print(f"   所有字段: {h.keys()}")
        print()
else:
    print("❌ 没有任何记录！")
