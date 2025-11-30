"""测试API配置"""
from database.db_manager import DatabaseManager

db = DatabaseManager()

# 查询所有API配置
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM api_configs")
configs = cursor.fetchall()

print(f"共有 {len(configs)} 个API配置：")
for config in configs:
    config_dict = dict(config)
    print(f"\n配置ID: {config_dict.get('id')}")
    print(f"  所有字段: {list(config_dict.keys())}")
    print(f"  平台: {config_dict.get('platform_type')}")
    print(f"  名称: {config_dict.get('name', '未命名')}")
    print(f"  Base URL: {config_dict.get('base_url')}")
    print(f"  Model: {config_dict.get('model')}")
    print(f"  API Key: {config_dict.get('api_key', '')[:20] if config_dict.get('api_key') else 'None'}...")
    print(f"  是否默认: {config_dict.get('is_default')}")
    print(f"  是否启用: {config_dict.get('is_active')}")

# 获取默认配置
default_config = db.get_default_api_config()
print(f"\n默认配置:")
if default_config:
    print(f"  平台: {default_config['platform_type']}")
    print(f"  Base URL: {default_config.get('base_url')}")
    print(f"  Model: {default_config.get('model')}")
else:
    print("  未设置默认配置")
