"""成就页面"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from services.achievement_service import AchievementService


class AchievementScreen(MDScreen):
    """成就页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'achievement'
        
        # 初始化服务
        self.achievement_service = AchievementService()
        
        # 当前筛选
        self.current_filter = 'all'  # all, unlocked, locked
        
        # 构建UI
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        # 主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )
        
        # 标题
        title = MDLabel(
            text="我的成就",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        main_layout.add_widget(title)
        
        # 筛选按钮
        filter_layout = self.create_filter_buttons()
        main_layout.add_widget(filter_layout)
        
        # 滚动视图
        scroll = MDScrollView()
        
        # 成就网格
        self.achievement_grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        self.achievement_grid.bind(minimum_height=self.achievement_grid.setter('height'))
        
        scroll.add_widget(self.achievement_grid)
        main_layout.add_widget(scroll)
        
        # 加载成就
        self.load_achievements()
        
        self.add_widget(main_layout)
    
    def create_filter_buttons(self):
        """创建筛选按钮"""
        filter_layout = BoxLayout(
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )
        
        # 全部按钮
        self.btn_all = MDFlatButton(
            text="全部",
            on_release=lambda x: self.filter_achievements('all')
        )
        filter_layout.add_widget(self.btn_all)
        
        # 已解锁按钮
        self.btn_unlocked = MDFlatButton(
            text="已解锁",
            on_release=lambda x: self.filter_achievements('unlocked')
        )
        filter_layout.add_widget(self.btn_unlocked)
        
        # 未解锁按钮
        self.btn_locked = MDFlatButton(
            text="未解锁",
            on_release=lambda x: self.filter_achievements('locked')
        )
        filter_layout.add_widget(self.btn_locked)
        
        return filter_layout
    
    def load_achievements(self):
        """加载成就"""
        # 清空现有成就
        self.achievement_grid.clear_widgets()
        
        # 获取成就数据
        achievements_data = self.achievement_service.get_all_achievements()
        
        # 根据筛选显示
        if self.current_filter == 'all':
            achievements = achievements_data['unlocked'] + achievements_data['locked']
        elif self.current_filter == 'unlocked':
            achievements = achievements_data['unlocked']
        else:  # locked
            achievements = achievements_data['locked']
        
        # 创建成就卡片
        for achievement in achievements:
            card = self.create_achievement_card(achievement)
            self.achievement_grid.add_widget(card)
    
    def create_achievement_card(self, achievement):
        """创建成就卡片"""
        is_unlocked = achievement['is_unlocked']
        
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            radius=[dp(15)],
            size_hint_y=None,
            height=dp(180)
        )
        
        # 设置背景色
        if is_unlocked:
            # 根据稀有度设置颜色
            rarity_colors = {
                'BRONZE': (0.8, 0.5, 0.2, 0.2),
                'SILVER': (0.75, 0.75, 0.75, 0.2),
                'GOLD': (1, 0.84, 0, 0.2),
                'DIAMOND': (0.73, 0.95, 1, 0.2),
                'LEGEND': (1, 0.42, 0.42, 0.2)
            }
            card.md_bg_color = rarity_colors.get(achievement['rarity'], (0.95, 0.95, 0.95, 1))
        else:
            card.md_bg_color = (0.95, 0.95, 0.95, 1)
        
        # 图标
        icon_text = achievement['icon'] if is_unlocked else "🔒"
        icon = MDLabel(
            text=icon_text,
            font_style="H3",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        card.add_widget(icon)
        
        # 名称（带计数徽章）
        name_text = achievement['name']
        
        # 如果已解锁且是可重复成就，显示计数
        if is_unlocked and achievement.get('repeatable', False):
            # 获取计数
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT count FROM user_achievements WHERE achievement_id = ?", (achievement['id'],))
            result = cursor.fetchone()
            if result and result['count'] > 1:
                name_text = f"{achievement['name']} ×{result['count']}"
        
        name = MDLabel(
            text=name_text,
            font_style="Subtitle1",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(name)
        
        # 描述
        desc = MDLabel(
            text=achievement['description'],
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(40)
        )
        card.add_widget(desc)
        
        # 解锁时间或进度
        if is_unlocked and achievement['unlocked_at']:
            time_label = MDLabel(
                text=f"获得于 {achievement['unlocked_at'][:10]}",
                font_style="Caption",
                halign="center",
                theme_text_color="Hint"
            )
            card.add_widget(time_label)
        else:
            # 显示进度
            progress_info = self.achievement_service.get_achievement_progress(achievement['id'])
            if progress_info and progress_info['target'] > 0:
                progress_text = f"进度: {progress_info['current']}/{progress_info['target']}"
                progress_label = MDLabel(
                    text=progress_text,
                    font_style="Caption",
                    halign="center",
                    theme_text_color="Hint"
                )
                card.add_widget(progress_label)
        
        return card
    
    def filter_achievements(self, filter_type):
        """筛选成就"""
        self.current_filter = filter_type
        self.load_achievements()
    
    def on_enter(self):
        """进入页面时刷新"""
        self.load_achievements()
