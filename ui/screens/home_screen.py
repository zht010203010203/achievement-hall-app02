"""成就殿堂 - 主页"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.animation import Animation

from services.study_service import StudyService
from services.achievement_service import AchievementService
from utils.animation import number_count_up


class HomeScreen(MDScreen):
    """成就殿堂主页"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        
        # 初始化服务
        self.study_service = StudyService()
        self.achievement_service = AchievementService()
        
        # 构建UI
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        # 主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20)
        )
        
        # 标题
        title = MDLabel(
            text="成就殿堂",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        main_layout.add_widget(title)
        
        # 总题量卡片
        self.total_card = self.create_total_card()
        main_layout.add_widget(self.total_card)
        
        # 今日进度卡片
        self.progress_card = self.create_progress_card()
        main_layout.add_widget(self.progress_card)
        
        # 连续打卡卡片
        self.streak_card = self.create_streak_card()
        main_layout.add_widget(self.streak_card)
        
        # 开始刷题按钮
        start_btn = MDRaisedButton(
            text="开始刷题",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=(0.29, 0.5, 1, 1),  # #4A7FFF
            on_release=self.go_to_record
        )
        main_layout.add_widget(start_btn)
        
        self.add_widget(main_layout)
    
    def create_total_card(self):
        """创建总题量卡片"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(200),
            padding=dp(20),
            radius=[dp(20)],
            md_bg_color=(0.29, 0.5, 1, 1)  # 蓝色背景
        )
        
        # 小标题
        subtitle = MDLabel(
            text="总刷题量",
            font_style="Caption",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.7),
            size_hint_y=None,
            height=dp(20)
        )
        card.add_widget(subtitle)
        
        # 大数字
        level_info = self.study_service.get_level_info()
        self.total_label = MDLabel(
            text=f"{level_info['total_count']:,}",
            font_style="H2",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(80)
        )
        card.add_widget(self.total_label)
        
        # 等级徽章
        level_badge = MDLabel(
            text=f"🔥 Level {level_info['level']} {level_info['title']}",
            font_style="H6",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.9),
            size_hint_y=None,
            height=dp(40)
        )
        card.add_widget(level_badge)
        
        return card
    
    def create_progress_card(self):
        """创建今日进度卡片"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(120),
            padding=dp(20),
            radius=[dp(15)]
        )
        
        # 标题行
        title_layout = BoxLayout(
            size_hint_y=None,
            height=dp(30)
        )
        
        title = MDLabel(
            text="今日进度",
            font_style="Subtitle1",
            size_hint_x=0.7
        )
        title_layout.add_widget(title)
        
        # 进度百分比
        today_progress = self.study_service.get_today_progress()
        self.progress_percent = MDLabel(
            text=f"{today_progress['percentage']}%",
            font_style="H6",
            halign="right",
            theme_text_color="Primary",
            size_hint_x=0.3
        )
        title_layout.add_widget(self.progress_percent)
        
        card.add_widget(title_layout)
        
        # 进度文字
        self.progress_text = MDLabel(
            text=f"{today_progress['current']}/{today_progress['target']} 题",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )
        card.add_widget(self.progress_text)
        
        # 进度条
        progress_bg = FloatLayout(
            size_hint=(1, None),
            height=dp(10)
        )
        
        # 进度条背景
        with progress_bg.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.progress_bg_rect = RoundedRectangle(
                pos=progress_bg.pos,
                size=progress_bg.size,
                radius=[dp(5)]
            )
        
        # 进度条前景（初始化为0宽度，等待布局完成后更新）
        with progress_bg.canvas:
            Color(0.29, 0.5, 1, 1)  # 蓝色
            self.progress_fg_rect = RoundedRectangle(
                pos=progress_bg.pos,
                size=(0, progress_bg.height),  # 初始宽度为0
                radius=[dp(5)]
            )
        
        # 保存进度条容器和当前百分比
        self.progress_bg_container = progress_bg
        self.current_percentage = today_progress['percentage']
        
        progress_bg.bind(pos=self.update_progress_bar, size=self.update_progress_bar)
        
        card.add_widget(progress_bg)
        
        return card
    
    def create_streak_card(self):
        """创建连续打卡卡片"""
        card = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(80),
            padding=dp(20),
            radius=[dp(15)]
        )
        
        # 图标
        icon_label = MDLabel(
            text="⚡",
            font_style="H4",
            size_hint_x=None,
            width=dp(50),
            halign="center"
        )
        card.add_widget(icon_label)
        
        # 文字信息
        info_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5)
        )
        
        streak_days = self.study_service.get_streak_days()
        
        streak_title = MDLabel(
            text=f"连续打卡: {streak_days}天",
            font_style="Subtitle1"
        )
        info_layout.add_widget(streak_title)
        
        # 计算超越百分比（示例）
        streak_percent = min(92, streak_days * 3)  # 简化计算
        
        streak_subtitle = MDLabel(
            text=f"超越 {streak_percent}% 刷题者",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        info_layout.add_widget(streak_subtitle)
        
        card.add_widget(info_layout)
        
        return card
    
    def update_progress_bar(self, instance, value):
        """更新进度条位置"""
        self.progress_bg_rect.pos = instance.pos
        self.progress_bg_rect.size = instance.size
        
        today_progress = self.study_service.get_today_progress()
        width = instance.width * (today_progress['percentage'] / 100)
        self.progress_fg_rect.pos = instance.pos
        self.progress_fg_rect.size = (width, instance.height)
    
    def go_to_record(self, *args):
        """跳转到刷题页面"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if app and hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'record'
    
    def on_enter(self):
        """进入页面时刷新数据"""
        self.refresh_data()
    
    def refresh_data(self):
        """刷新数据"""
        # 刷新总题量
        level_info = self.study_service.get_level_info()
        self.total_label.text = f"{level_info['total_count']:,}"
        
        # 刷新今日进度
        today_progress = self.study_service.get_today_progress()
        self.progress_percent.text = f"{today_progress['percentage']}%"
        self.progress_text.text = f"{today_progress['current']}/{today_progress['target']} 题"
        
        # 更新进度条（直接调用update方法）
        self.current_percentage = today_progress['percentage']
        if hasattr(self, 'progress_bg_container'):
            self.update_progress_bar(self.progress_bg_container, None)
