"""核心功能测试脚本"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from services.study_service import StudyService
from services.achievement_service import AchievementService
from services.stats_service import StatsService


def test_database():
    """测试数据库"""
    print("\n" + "="*50)
    print("📊 测试数据库初始化")
    print("="*50)
    
    db = DatabaseManager()
    
    # 测试获取科目
    subjects = db.get_all_subjects()
    print(f"\n✅ 科目数量: {len(subjects)}")
    for subject in subjects:
        print(f"   - {subject['icon']} {subject['name']}: {subject['total_count']}题")
    
    # 测试获取成就
    achievements = db.get_all_achievements()
    print(f"\n✅ 成就数量: {len(achievements)}")
    for ach in achievements[:3]:  # 只显示前3个
        print(f"   - {ach['icon']} {ach['name']}: {ach['description']}")
    
    # 测试获取AI身份
    identities = db.get_all_ai_identities()
    print(f"\n✅ AI身份数量: {len(identities)}")
    for identity in identities:
        print(f"   - {identity['name']}: {identity['tone_style']}")
    
    db.close()
    print("\n✅ 数据库测试通过！")


def test_study_service():
    """测试学习服务"""
    print("\n" + "="*50)
    print("📚 测试学习服务")
    print("="*50)
    
    service = StudyService()
    
    # 添加学习记录
    print("\n📝 添加学习记录...")
    result = service.add_record(subject_id=1, count=5)
    print(f"   添加了 {result['added_count']} 题")
    print(f"   今日进度: {result['today_progress']['current']}/{result['today_progress']['target']}")
    print(f"   总题数: {result['total_count']}")
    print(f"   连续天数: {result['streak_days']}")
    
    # 获取等级信息
    level_info = service.get_level_info()
    print(f"\n🏆 等级信息:")
    print(f"   Level {level_info['level']}: {level_info['title']}")
    print(f"   总题数: {level_info['total_count']}")
    print(f"   距离下一级: {level_info['remaining']}题")
    
    # 计算学习时长
    study_time = service.calculate_study_time()
    print(f"\n⏱️  累计学习时长: {study_time}")
    
    print("\n✅ 学习服务测试通过！")


def test_achievement_service():
    """测试成就服务"""
    print("\n" + "="*50)
    print("🏅 测试成就服务")
    print("="*50)
    
    service = AchievementService()
    
    # 检查成就
    print("\n🔍 检查成就解锁...")
    newly_unlocked = service.check_achievements()
    
    if newly_unlocked:
        print(f"   🎉 新解锁 {len(newly_unlocked)} 个成就:")
        for ach in newly_unlocked:
            print(f"      {ach['icon']} {ach['name']}")
    else:
        print("   暂无新成就解锁")
    
    # 获取成就统计
    stats = service.get_achievement_stats()
    print(f"\n📊 成就统计:")
    print(f"   总成就: {stats['total']}")
    print(f"   已解锁: {stats['unlocked']}")
    print(f"   完成率: {stats['completion_rate']}%")
    
    print("\n✅ 成就服务测试通过！")


def test_stats_service():
    """测试统计服务"""
    print("\n" + "="*50)
    print("📈 测试统计服务")
    print("="*50)
    
    service = StatsService()
    
    # 获取总览统计
    overview = service.get_overview_stats()
    print(f"\n📊 总览统计:")
    print(f"   总题数: {overview['total_count']}")
    print(f"   今日: {overview['today_current']}/{overview['today_target']}")
    print(f"   连续: {overview['streak_days']}天")
    print(f"   等级: Level {overview['level']} {overview['level_title']}")
    print(f"   时长: {overview['study_time']}")
    
    # 获取本周趋势
    weekly = service.get_weekly_trend()
    print(f"\n📅 本周趋势:")
    print(f"   本周总计: {weekly['total_week']}题")
    print(f"   日均: {weekly['avg_daily']}题")
    
    print("\n✅ 统计服务测试通过！")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🚀 成就殿堂 - 核心功能测试")
    print("="*60)
    
    try:
        test_database()
        test_study_service()
        test_achievement_service()
        test_stats_service()
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！核心功能正常运行")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
