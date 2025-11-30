"""刷题记录页面"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.clock import Clock
import random

from services.study_service import StudyService
from services.achievement_service import AchievementService
from services.ai_service import AIService
from ui.components.achievement_animation import show_achievement_unlock


class RecordScreen(MDScreen):
    """刷题记录页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'record'
        
        # 初始化服务
        self.study_service = StudyService()
        self.achievement_service = AchievementService()
        self.ai_service = AIService()
        
        # 动态加载当前科目（取第一个科目）
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        subjects = db.get_all_subjects()
        
        if subjects:
            self.current_subject_id = subjects[0]['id']
            self.current_subject_name = subjects[0]['name']
        else:
            # 如果没有科目，使用默认值
            self.current_subject_id = None
            self.current_subject_name = "请先添加科目"
        
        # Combo相关
        self.combo_count = 0
        self.last_click_time = 0
        
        # 构建UI
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        # 主布局
        main_layout = FloatLayout()
        
        # 内容布局
        content_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20),
            size_hint=(1, 1)
        )
        
        # 标题
        title = MDLabel(
            text="今日挑战",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        content_layout.add_widget(title)
        
        # 进度卡片
        self.progress_card = self.create_progress_card()
        content_layout.add_widget(self.progress_card)
        
        # 科目选择
        self.subject_selector = self.create_subject_selector()
        content_layout.add_widget(self.subject_selector)
        
        # +1 大按钮
        self.plus_one_btn = self.create_plus_one_button()
        content_layout.add_widget(self.plus_one_btn)
        
        # 快捷按钮
        quick_buttons = self.create_quick_buttons()
        content_layout.add_widget(quick_buttons)
        
        # 今日目标提示
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        user_config = db.get_user_config()
        daily_target = user_config.get('daily_target', 20)
        
        # 获取今日已完成数
        from services.study_service import StudyService
        study_service = StudyService()
        today_progress = study_service.get_today_progress()
        today_count = today_progress.get('current', 0)
        
        self.achievement_hint = MDLabel(
            text=f'今日目标：{today_count}/{daily_target}题  继续加油！💪',
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30)
        )
        content_layout.add_widget(self.achievement_hint)
        
        main_layout.add_widget(content_layout)
        
        # Combo显示层（浮动）
        self.combo_label = MDLabel(
            text="",
            font_style="H3",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 0.42, 0.42, 1),  # 红色
            opacity=0,
            pos_hint={'center_x': 0.5, 'center_y': 0.7}
        )
        main_layout.add_widget(self.combo_label)
        
        self.add_widget(main_layout)
    
    def create_progress_card(self):
        """创建进度卡片"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(100),
            padding=dp(15),
            radius=[dp(15)]
        )
        
        # 获取当前科目进度
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        if self.current_subject_id:
            progress = db.get_subject_today_progress(self.current_subject_id)
        else:
            progress = {'current': 0, 'target': 20, 'percentage': 0}
        
        # 标题行
        title_layout = BoxLayout(
            size_hint_y=None,
            height=dp(30)
        )
        
        self.target_label = MDLabel(
            text=f"目标: {progress['target']}题",
            font_style="Body1",
            size_hint_x=0.5
        )
        title_layout.add_widget(self.target_label)
        
        self.progress_label = MDLabel(
            text=f"已完成: {progress['current']}题",
            font_style="Body1",
            halign="right",
            theme_text_color="Primary",
            size_hint_x=0.5
        )
        title_layout.add_widget(self.progress_label)
        
        card.add_widget(title_layout)
        
        # 进度条
        progress_container = FloatLayout(
            size_hint=(1, None),
            height=dp(10)
        )
        
        with progress_container.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.progress_bg = Ellipse(size=(0, 0))  # 占位
        
        with progress_container.canvas:
            Color(0.29, 0.5, 1, 1)
            self.progress_fg = Ellipse(size=(0, 0))  # 占位
        
        card.add_widget(progress_container)
        
        return card
    
    def create_subject_selector(self):
        """创建科目选择器"""
        selector_layout = BoxLayout(
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )
        
        # 科目指示器
        indicator = MDLabel(
            text="●",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_x=None,
            width=dp(30)
        )
        selector_layout.add_widget(indicator)
        
        # 科目名称按钮
        self.subject_btn = MDFlatButton(
            text=self.current_subject_name,
            on_release=self.show_subject_menu
        )
        selector_layout.add_widget(self.subject_btn)
        
        # 下拉图标
        dropdown_icon = MDLabel(
            text="▼",
            font_style="Caption",
            size_hint_x=None,
            width=dp(30),
            halign="right"
        )
        selector_layout.add_widget(dropdown_icon)
        
        return selector_layout
    
    def create_plus_one_button(self):
        """创建+1大按钮"""
        btn_container = FloatLayout(
            size_hint=(1, None),
            height=dp(250)
        )
        
        # 创建圆形按钮
        btn = MDRaisedButton(
            text="+1\n完成一题",
            font_style="H4",
            size_hint=(None, None),
            size=(dp(200), dp(200)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            md_bg_color=(0.29, 0.5, 1, 1),
            on_release=self.on_plus_one_click
        )
        
        # 设置圆形
        btn.radius = [dp(100)]
        
        self.plus_one_button = btn
        btn_container.add_widget(btn)
        
        return btn_container
    
    def create_quick_buttons(self):
        """创建快捷按钮"""
        btn_layout = BoxLayout(
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )
        
        # +5 按钮
        btn_5 = MDRaisedButton(
            text="+5",
            size_hint=(0.3, 1),
            on_release=lambda x: self.add_count(5)
        )
        btn_layout.add_widget(btn_5)
        
        # +10 按钮
        btn_10 = MDRaisedButton(
            text="+10",
            size_hint=(0.3, 1),
            on_release=lambda x: self.add_count(10)
        )
        btn_layout.add_widget(btn_10)
        
        # 自定义按钮
        btn_custom = MDRaisedButton(
            text="自定义",
            size_hint=(0.4, 1),
            on_release=self.show_custom_dialog
        )
        btn_layout.add_widget(btn_custom)
        
        return btn_layout
    
    def show_subject_menu(self, *args):
        """显示科目菜单"""
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        subjects = db.get_all_subjects()
        
        menu_items = []
        for subject in subjects:
            menu_items.append({
                "text": f"{subject['icon']} {subject['name']}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=subject: self.select_subject(x)
            })
        
        self.menu = MDDropdownMenu(
            caller=self.subject_btn,
            items=menu_items,
            width_mult=4
        )
        self.menu.open()
    
    def select_subject(self, subject):
        """选择科目"""
        self.current_subject_id = subject['id']
        self.current_subject_name = subject['name']
        self.subject_btn.text = self.current_subject_name
        self.menu.dismiss()
        
        # 刷新进度显示
        self.refresh_progress()
    
    def on_plus_one_click(self, *args):
        """点击+1按钮"""
        self.add_count(1)
        
        # 按钮动画（使用opacity替代scale）
        try:
            anim = Animation(opacity=0.7, duration=0.1)
            anim += Animation(opacity=1, duration=0.1)
            anim.start(self.plus_one_button)
        except:
            pass  # 动画失败不影响功能
        
        # 粒子效果
        self.create_particle_effect()
        
        # 检查Combo
        self.check_combo()
    
    def add_count(self, count):
        """添加题目数量"""
        # 检查是否有科目
        if self.current_subject_id is None:
            print("[WARN] 请先在设置页面添加科目")
            return
        
        # 添加记录
        result = self.study_service.add_record(self.current_subject_id, count)
        
        # 刷新当前科目的进度显示
        self.refresh_progress()
        
        # 更新今日目标提示
        self.update_daily_hint()
        
        # 获取全局进度用于AI和成就检查
        today_progress = result['today_progress']
        
        # 检查成就
        newly_unlocked = self.achievement_service.check_achievements()
        if newly_unlocked:
            self.show_achievement_dialog(newly_unlocked[0])
        
        # 检查速度成就
        if count >= 50:
            speed_achievements = self.achievement_service.check_speed_achievement(count)
            if speed_achievements:
                self.show_achievement_dialog(speed_achievements[0])
        
        # 检查AI触发
        self.check_ai_trigger(today_progress)
    
    def create_particle_effect(self):
        """创建粒子特效"""
        # 简化版粒子效果
        for _ in range(10):
            particle = MDLabel(
                text="*",
                font_style="H6",
                opacity=1,
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            
            # 随机方向
            dx = random.uniform(-0.3, 0.3)
            dy = random.uniform(0.1, 0.4)
            
            # 动画
            anim = Animation(
                pos_hint={'center_x': 0.5 + dx, 'center_y': 0.5 + dy},
                opacity=0,
                duration=0.5
            )
            anim.bind(on_complete=lambda *x: self.remove_widget(particle))
            
            self.add_widget(particle)
            anim.start(particle)
    
    def check_combo(self):
        """检查Combo"""
        import time
        current_time = time.time()
        
        if current_time - self.last_click_time < 1.0:  # 1秒内
            self.combo_count += 1
            if self.combo_count >= 3:
                self.show_combo()
        else:
            self.combo_count = 1
        
        self.last_click_time = current_time
    
    def show_combo(self):
        """显示Combo"""
        self.combo_label.text = f"🔥 x{self.combo_count} COMBO!"
        
        # 动画
        self.combo_label.opacity = 1
        anim = Animation(opacity=0, duration=1.0)
        anim.start(self.combo_label)
    
    def show_custom_dialog(self, *args):
        """显示自定义输入对话框"""
        content = BoxLayout(
            orientation='vertical', 
            spacing=dp(10), 
            padding=dp(20),
            size_hint_y=None,
            height=dp(80)  # 明确指定内容高度
        )
        
        self.custom_input = MDTextField(
            hint_text="输入题目数量（如：10、20、50）",
            input_filter="int",
            size_hint_y=None,
            height=dp(50),
            mode="rectangle",  # 使用矩形模式
            text=""  # 初始为空
        )
        content.add_widget(self.custom_input)
        
        self.custom_dialog = MDDialog(
            title="自定义输入",
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),  # 控制对话框宽度
            buttons=[
                MDFlatButton(
                    text="取消", 
                    on_release=lambda x: self.custom_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="确定", 
                    on_release=self.submit_custom_count
                )
            ]
        )
        self.custom_dialog.open()
    
    def submit_custom_count(self, *args):
        """提交自定义数量"""
        try:
            count = int(self.custom_input.text)
            if count > 0:
                self.add_count(count)
                self.custom_dialog.dismiss()
        except:
            pass
    
    def show_achievement_dialog(self, achievement):
        """显示成就解锁对话框 - 使用超炫酷动画"""
        # 使用新的超炫酷动画
        show_achievement_unlock(achievement)
    
    def check_ai_trigger(self, today_progress):
        """检查AI触发"""
        # 完成每日目标
        if today_progress['current'] >= today_progress['target']:
            trigger_scene = self.ai_service.check_trigger_conditions('daily_goal_complete')
            if trigger_scene:
                self.request_ai_encouragement(trigger_scene)
    
    def request_ai_encouragement(self, trigger_scene):
        """请求AI鼓励"""
        # 这里简化处理，实际应该异步调用
        pass
    
    def on_enter(self):
        """进入页面时刷新"""
        # 1. 刷新科目列表
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        subjects = db.get_all_subjects()
        
        if subjects:
            # 如果当前科目不存在于列表中，切换到第一个科目
            subject_ids = [s['id'] for s in subjects]
            if self.current_subject_id not in subject_ids:
                self.current_subject_id = subjects[0]['id']
                self.current_subject_name = subjects[0]['name']
                self.subject_btn.text = self.current_subject_name
        else:
            self.current_subject_id = None
            self.current_subject_name = "请先添加科目"
            self.subject_btn.text = self.current_subject_name
        
        # 2. 刷新今日进度
        self.refresh_progress()
    
    def refresh_progress(self):
        """刷新当前科目的进度显示"""
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        
        if self.current_subject_id:
            progress = db.get_subject_today_progress(self.current_subject_id)
            self.target_label.text = f"目标: {progress['target']}题"
            self.progress_label.text = f"已完成: {progress['current']}题"
        else:
            self.target_label.text = "目标: 20题"
            self.progress_label.text = "已完成: 0题"
    
    def update_daily_hint(self):
        """更新今日目标提示"""
        from database.db_manager import DatabaseManager
        from services.study_service import StudyService
        
        db = DatabaseManager()
        user_config = db.get_user_config()
        daily_target = user_config.get('daily_target', 20)
        
        study_service = StudyService()
        today_progress = study_service.get_today_progress()
        today_count = today_progress.get('current', 0)
        
        # 更新提示文本
        if today_count >= daily_target:
            self.achievement_hint.text = f'今日目标已完成！🎉 ({today_count}/{daily_target}题)'
        else:
            remaining = daily_target - today_count
            self.achievement_hint.text = f'今日目标：{today_count}/{daily_target}题  还需{remaining}题！💪'
