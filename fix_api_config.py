"""修复API配置中的base_url"""
from database.db_manager import DatabaseManager
from config.constants import API_PLATFORMS

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# 获取所有volcengine配置
cursor.execute("SELECT * FROM api_configs WHERE platform_type = 'volcengine'")
configs = cursor.fetchall()

print(f"找到 {len(configs)} 个Volcengine配置需要修复")

# 获取默认base_url
default_base_url = API_PLATFORMS['volcengine']['base_url']
print(f"默认Base URL: {default_base_url}")

# 更新所有base_url为None的配置
for config in configs:
    if not config['base_url']:
        print(f"\n修复配置ID {config['id']}")
        cursor.execute("""
            UPDATE api_configs 
            SET base_url = ? 
            WHERE id = ?
        """, (default_base_url, config['id']))
        print(f"  已设置Base URL: {default_base_url}")

conn.commit()
print(f"\n✅ 修复完成！")

# 验证
cursor.execute("SELECT * FROM api_configs WHERE is_default = 1")
default_config = cursor.fetchone()
if default_config:
    print(f"\n默认配置:")
    print(f"  平台: {default_config['platform_type']}")
    print(f"  Base URL: {default_config['base_url']}")
    print(f"  Model: {default_config['model_id']}")
