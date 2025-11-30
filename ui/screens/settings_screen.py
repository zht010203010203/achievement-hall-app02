"""设置页面"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import os

# 定义可点击的图片按钮类
class ImageButton(ButtonBehavior, Image):
    """可点击的图片按钮"""
    pass

from database.db_manager import DatabaseManager


class SettingsScreen(MDScreen):
    """设置页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        
        # 初始化数据库
        self.db = DatabaseManager()
        
        # 构建UI
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        # 滚动视图
        scroll = MDScrollView()
        
        # 主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # 标题
        title = MDLabel(
            text="目标与任务",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        main_layout.add_widget(title)
        
        # 总体目标卡片
        goal_card = self.create_goal_card()
        main_layout.add_widget(goal_card)
        
        # 任务管理卡片
        task_card = self.create_task_card()
        main_layout.add_widget(task_card)
        
        # AI配置卡片
        ai_card = self.create_ai_config_card()
        main_layout.add_widget(ai_card)
        
        # 数据管理卡片（危险操作，放最后）
        data_card = self.create_data_management_card()
        main_layout.add_widget(data_card)
        
        scroll.add_widget(main_layout)
        self.add_widget(scroll)
    
    def create_goal_card(self):
        """创建目标卡片"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(160),
            padding=dp(20),
            radius=[dp(15)]
        )
        
        # 标题
        title = MDLabel(
            text="总体目标",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title)
        
        # 获取当前配置
        user_config = self.db.get_user_config()
        
        # 终极目标布局
        goal_layout = BoxLayout(
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )
        
        # 终极目标按钮
        goal_btn = MDRaisedButton(
            text="终极目标",
            size_hint=(0.35, 1),
            on_release=self.open_total_goal_dialog
        )
        goal_layout.add_widget(goal_btn)
        
        # 终极目标数值（纯文本显示）
        self.total_goal_label = MDLabel(
            text=f"题数    {user_config.get('total_target', 10000)}",
            size_hint=(0.65, 1),
            halign='left',
            valign='center'
        )
        self.total_goal_label.bind(size=self.total_goal_label.setter('text_size'))
        goal_layout.add_widget(self.total_goal_label)
        card.add_widget(goal_layout)
        
        # 每日目标布局
        daily_layout = BoxLayout(
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )
        
        # 每日目标按钮
        daily_btn = MDRaisedButton(
            text="每日目标",
            size_hint=(0.35, 1),
            on_release=self.open_daily_goal_dialog
        )
        daily_layout.add_widget(daily_btn)
        
        # 每日目标数值（纯文本显示）
        self.daily_goal_label = MDLabel(
            text=f"题数    {user_config.get('daily_target', 20)}",
            size_hint=(0.65, 1),
            halign='left',
            valign='center'
        )
        self.daily_goal_label.bind(size=self.daily_goal_label.setter('text_size'))
        daily_layout.add_widget(self.daily_goal_label)
        card.add_widget(daily_layout)
        
        return card
    
    def create_task_card(self):
        """创建任务管理卡片"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(300),  # 固定高度
            padding=dp(20),
            radius=[dp(15)]
        )
        
        # 标题行
        title_layout = BoxLayout(
            size_hint_y=None,
            height=dp(40)
        )
        
        title = MDLabel(
            text="任务管理",
            font_style="Subtitle1",
            size_hint_x=0.7
        )
        title_layout.add_widget(title)
        
        add_btn = MDFlatButton(
            text="+ 添加",
            size_hint_x=0.3,
            on_release=self.show_add_subject_dialog
        )
        title_layout.add_widget(add_btn)
        
        card.add_widget(title_layout)
        
        # 任务列表（添加滚动视图）
        task_scroll = MDScrollView(
            size_hint_y=None,
            height=dp(220)  # 固定滚动区域高度
        )
        
        self.task_list_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter('height'))
        
        # 加载任务
        self.load_tasks()
        
        task_scroll.add_widget(self.task_list_layout)
        card.add_widget(task_scroll)
        
        return card
    
    def load_tasks(self):
        """加载任务列表"""
        # 清空现有任务
        self.task_list_layout.clear_widgets()
        
        # 获取科目
        subjects = self.db.get_all_subjects()
        
        for subject in subjects:
            task_item = self.create_task_item(subject)
            self.task_list_layout.add_widget(task_item)
    
    def create_task_item(self, subject):
        """创建任务项"""
        item_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10),
            padding=[dp(5), 0, dp(5), 0]
        )
        
        # 颜色指示条
        color_bar = BoxLayout(
            size_hint_x=None,
            width=dp(5)
        )
        from kivy.graphics import Color, Rectangle
        with color_bar.canvas:
            # 解析颜色
            color_str = subject['color']
            if color_str.startswith('#'):
                r = int(color_str[1:3], 16) / 255
                g = int(color_str[3:5], 16) / 255
                b = int(color_str[5:7], 16) / 255
                Color(r, g, b, 1)
            else:
                Color(0.29, 0.5, 1, 1)
            color_rect = Rectangle(pos=color_bar.pos, size=color_bar.size)
        
        color_bar.bind(pos=lambda w, v: setattr(color_rect, 'pos', v))
        color_bar.bind(size=lambda w, v: setattr(color_rect, 'size', v))
        
        item_layout.add_widget(color_bar)
        
        # 任务信息
        info_layout = BoxLayout(
            orientation='vertical',
            size_hint_x=0.6  # 减小信息区宽度，给按钮更多空间
        )
        
        # patch会自动使用ChineseFont
        name_label = MDLabel(
            text=subject['name'],
            font_style="Subtitle2"
        )
        info_layout.add_widget(name_label)
        
        # 显示总题数和每日目标（patch会自动使用ChineseFont）
        daily_target = subject.get('daily_target', 20)
        count_label = MDLabel(
            text=f"已刷 {subject['total_count']} 题 · 目标 {daily_target} 题/天",
            font_style="Caption",
            theme_text_color="Hint"
        )
        info_layout.add_widget(count_label)
        
        item_layout.add_widget(info_layout)
        
        # 按钮组（改用文字按钮，更明显）
        btn_box = BoxLayout(
            orientation='vertical',
            size_hint_x=0.3,
            spacing=dp(3)
        )
        
        # 编辑按钮（文字按钮）
        edit_btn = MDFlatButton(
            text="编辑",
            size_hint_y=None,
            height=dp(28),
            md_bg_color=(0.29, 0.5, 1, 0.15),  # 浅蓝背景
            on_release=lambda x: self.show_edit_subject_dialog(subject)
        )
        btn_box.add_widget(edit_btn)
        
        # 删除按钮（文字按钮）
        delete_btn = MDFlatButton(
            text="删除",
            size_hint_y=None,
            height=dp(28),
            md_bg_color=(1, 0.3, 0.3, 0.15),  # 浅红背景
            on_release=lambda x: self.delete_subject(subject['id'], subject['name'])
        )
        btn_box.add_widget(delete_btn)
        
        item_layout.add_widget(btn_box)
        
        return item_layout
    
    def create_ai_config_card(self):
        """创建AI配置卡片"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(150),
            padding=dp(20),
            radius=[dp(15)]
        )
        
        # 标题
        title = MDLabel(
            text="🤖 AI配置",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title)
        
        # 说明
        desc = MDLabel(
            text="配置AI API以启用智能鼓励功能",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(40)
        )
        card.add_widget(desc)
        
        # 配置按钮
        config_btn = MDRaisedButton(
            text="配置API",
            size_hint=(1, None),
            height=dp(50),
            on_release=self.show_api_config_dialog
        )
        card.add_widget(config_btn)
        
        return card
    
    def create_data_management_card(self):
        """创建数据管理卡片"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(280),
            padding=dp(20),
            radius=[dp(15)],
            md_bg_color=(1, 0.95, 0.95, 1)  # 浅红背景，提示危险操作
        )
        
        # 标题
        title = MDLabel(
            text="⚠️ 数据管理",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title)
        
        # 说明
        desc = MDLabel(
            text="以下操作不可恢复，请谨慎使用",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),  # 红色警告
            size_hint_y=None,
            height=dp(25)
        )
        card.add_widget(desc)
        
        # 按钮容器
        btn_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(170)
        )
        
        # 清除今日数据按钮
        clear_today_btn = MDFlatButton(
            text="清除今日刷题数据",
            size_hint=(1, None),
            height=dp(45),
            md_bg_color=(1, 0.9, 0.9, 1),
            on_release=self.confirm_clear_today_data
        )
        btn_container.add_widget(clear_today_btn)
        
        # 清除单科目数据按钮
        clear_subject_btn = MDFlatButton(
            text="清除指定科目数据",
            size_hint=(1, None),
            height=dp(45),
            md_bg_color=(1, 0.9, 0.9, 1),
            on_release=self.confirm_clear_subject_data
        )
        btn_container.add_widget(clear_subject_btn)
        
        # 清除全部数据按钮（最危险）
        clear_all_btn = MDRaisedButton(
            text="🗑️ 清除全部刷题数据",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(0.9, 0.2, 0.2, 1),  # 深红色
            on_release=self.confirm_clear_all_data
        )
        btn_container.add_widget(clear_all_btn)
        
        card.add_widget(btn_container)
        
        return card
    
    def show_add_subject_dialog(self, *args):
        """显示添加科目对话框"""
        content = BoxLayout(
            orientation='vertical', 
            spacing=dp(10), 
            padding=dp(20),
            size_hint_y=None,
            height=dp(80)  # 明确指定内容高度
        )
        
        self.subject_name_field = MDTextField(
            hint_text="科目名称（如：数学、英语）",
            size_hint_y=None,
            height=dp(50),
            mode="rectangle"  # 使用矩形模式，更明显
        )
        content.add_widget(self.subject_name_field)
        
        self.add_subject_dialog = MDDialog(
            title="添加科目",
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),  # 控制对话框宽度
            buttons=[
                MDFlatButton(
                    text="取消", 
                    on_release=lambda x: self.add_subject_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="添加", 
                    on_release=self.add_subject
                )
            ]
        )
        self.add_subject_dialog.open()
    
    def add_subject(self, *args):
        """添加科目"""
        name = self.subject_name_field.text.strip()
        if name:
            try:
                self.db.add_subject(name)
                self.load_tasks()
                self.add_subject_dialog.dismiss()
                
                print(f"[OK] 已添加科目: {name}")
            except Exception as e:
                print(f"[ERROR] {str(e)}")
    
    def show_edit_subject_dialog(self, subject):
        """显示编辑科目对话框"""
        content = BoxLayout(
            orientation='vertical', 
            spacing=dp(10), 
            padding=dp(20),
            size_hint_y=None,
            height=dp(180)  # 明确指定内容高度（两个输入框+提示）
        )
        
        # 科目名称输入
        self.edit_subject_name_field = MDTextField(
            text=subject['name'],
            hint_text="科目名称",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(self.edit_subject_name_field)
        
        # 每日目标输入
        self.edit_subject_target_field = MDTextField(
            text=str(subject.get('daily_target', 20)),
            hint_text="每日目标（题数）",
            input_filter='int',
            mode="rectangle",
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(self.edit_subject_target_field)
        
        # 当前进度提示
        hint_label = MDLabel(
            text=f"总刷题量: {subject['total_count']}题",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(hint_label)
        
        self.edit_subject_dialog = MDDialog(
            title=f"编辑科目",
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),
            buttons=[
                MDFlatButton(
                    text="取消", 
                    on_release=lambda x: self.edit_subject_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存", 
                    on_release=lambda x: self.update_subject(subject['id'])
                )
            ]
        )
        self.edit_subject_dialog.open()
    
    def update_subject(self, subject_id):
        """更新科目"""
        new_name = self.edit_subject_name_field.text.strip()
        new_target = self.edit_subject_target_field.text.strip()
        
        if not new_name:
            print("[WARN] 科目名称不能为空")
            return
        
        try:
            # 更新名称
            self.db.update_subject(subject_id, new_name)
            
            # 更新每日目标
            if new_target and new_target.isdigit():
                target = int(new_target)
                if target > 0:
                    self.db.update_subject_target(subject_id, target)
                    print(f"[OK] 已更新科目: {new_name}，每日目标: {target}题")
                else:
                    print("[WARN] 每日目标必须大于0")
            
            self.load_tasks()
            self.edit_subject_dialog.dismiss()
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
    
    def delete_subject(self, subject_id, subject_name):
        """删除科目"""
        # 至少保留一个科目
        subjects = self.db.get_all_subjects()
        if len(subjects) <= 1:
            print("[WARN] 至少需要保留一个科目")
            return
        
        # 确认对话框
        from kivymd.uix.dialog import MDDialog
        confirm_dialog = MDDialog(
            title="确认删除",
            text=f"确定要删除科目【{subject_name}】吗？\n该科目的所有记录也会被删除。",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="删除",
                    on_release=lambda x: self.do_delete_subject(subject_id, confirm_dialog)
                )
            ]
        )
        confirm_dialog.open()
    
    def do_delete_subject(self, subject_id, dialog):
        """执行删除科目"""
        try:
            self.db.delete_subject(subject_id)
            self.load_tasks()
            dialog.dismiss()
            
            print(f"[OK] 已删除科目: {subject_id}")
        except Exception as e:
            print(f"[ERROR] 删除失败: {e}")
    
    def show_api_config_dialog(self, *args):
        """显示API配置对话框"""
        # 创建对话框内容
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(15),
            size_hint_y=None,
            height=dp(400)
        )
        
        # 标题说明
        title_label = MDLabel(
            text="配置AI助手\n选择一个AI平台并输入API密钥",
            font_style="Subtitle1",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(title_label)
        
        # 平台选择
        platform_label = MDLabel(
            text="选择平台:",
            font_style="Caption",
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(platform_label)
        
        # 平台按钮容器
        self.platform_buttons = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5)
        )
        
        platforms = [
            ('OpenRouter', 'openrouter'),
            ('DeepSeek', 'deepseek'),
            ('火山引擎', 'volcengine')
        ]
        
        self.selected_platform = 'openrouter'
        self.platform_btn_refs = {}
        
        for name, platform_id in platforms:
            btn = MDFlatButton(
                text=name,
                size_hint_x=None,
                width=dp(100)
            )
            btn.platform_id = platform_id
            btn.bind(on_release=self.on_platform_select)
            self.platform_btn_refs[platform_id] = btn
            self.platform_buttons.add_widget(btn)
        
        # 高亮默认选中
        self.platform_btn_refs['openrouter'].md_bg_color = (0.29, 0.5, 1, 0.2)
        
        content.add_widget(self.platform_buttons)
        
        # API密钥输入
        self.api_key_field = MDTextField(
            hint_text="输入API密钥",
            helper_text="从平台官网获取API密钥",
            helper_text_mode="persistent",
            size_hint_y=None,
            height=dp(60),
            password=True
        )
        content.add_widget(self.api_key_field)
        
        # Base URL（可选）
        self.base_url_field = MDTextField(
            hint_text="Base URL（可选）",
            helper_text="默认使用官方地址",
            helper_text_mode="persistent",
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(self.base_url_field)
        
        # Model ID（可选）
        self.model_id_field = MDTextField(
            hint_text="模型ID（可选）",
            helper_text="推荐: deepseek-chat（对话模型）。避免使用deepseek-reasoner（推理模型）",
            helper_text_mode="persistent",
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(self.model_id_field)
        
        # 创建对话框
        self.api_config_dialog = MDDialog(
            title="⚙️ API配置",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: self.api_config_dialog.dismiss()
                ),
                MDFlatButton(
                    text="测试连接",
                    on_release=self.test_api_connection
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=self.save_api_config
                )
            ]
        )
        
        # 加载当前配置
        self.load_current_api_config()
        
        self.api_config_dialog.open()
    
    def on_platform_select(self, button):
        """平台选择事件"""
        # 重置所有按钮颜色
        for btn in self.platform_btn_refs.values():
            btn.md_bg_color = (1, 1, 1, 1)
        
        # 高亮选中按钮
        button.md_bg_color = (0.29, 0.5, 1, 0.2)
        self.selected_platform = button.platform_id
        print(f"[INFO] 选择平台: {self.selected_platform}")
    
    def load_current_api_config(self):
        """加载当前API配置"""
        try:
            config = self.db.get_default_api_config()
            if config:
                self.selected_platform = config['platform_type']
                self.api_key_field.text = config['api_key']
                self.base_url_field.text = config.get('base_url', '') or ''
                self.model_id_field.text = config.get('model_id', '') or ''
                
                # 高亮对应平台
                for platform_id, btn in self.platform_btn_refs.items():
                    if platform_id == self.selected_platform:
                        btn.md_bg_color = (0.29, 0.5, 1, 0.2)
                    else:
                        btn.md_bg_color = (1, 1, 1, 1)
                        
                print(f"[OK] 加载已有配置: {self.selected_platform}")
        except Exception as e:
            print(f"[WARN] 未找到已有配置: {e}")
    
    def test_api_connection(self, *args):
        """测试API连接"""
        api_key = self.api_key_field.text.strip()
        if not api_key:
            print("[ERROR] 请先输入API密钥")
            # 创建提示对话框
            error_dialog = MDDialog(
                title="❌ 错误",
                text="请先输入API密钥",
                buttons=[
                    MDRaisedButton(
                        text="确定",
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ]
            )
            error_dialog.open()
            return
        
        print(f"[INFO] 测试连接: {self.selected_platform}")
        print(f"[INFO] API密钥: {api_key[:10]}...")
        
        # 显示测试中对话框
        self.test_dialog = MDDialog(
            title="⏳ 测试中",
            text="正在连接API服务器，请稍候...",
        )
        self.test_dialog.open()
        
        # 异步测试连接
        import threading
        threading.Thread(target=self._test_api_in_background, daemon=True).start()
    
    def _test_api_in_background(self):
        """后台测试API连接"""
        import requests
        
        api_key = self.api_key_field.text.strip()
        base_url = self.base_url_field.text.strip()
        model_id = self.model_id_field.text.strip()
        
        # 设置默认值
        default_configs = {
            'openrouter': {
                'base_url': 'https://openrouter.ai/api/v1',
                'model_id': 'openai/gpt-3.5-turbo'
            },
            'deepseek': {
                'base_url': 'https://api.deepseek.com/v1',
                'model_id': 'deepseek-chat'
            },
            'volcengine': {
                'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
                'model_id': 'ep-xxxxx'
            }
        }
        
        if not base_url:
            base_url = default_configs[self.selected_platform]['base_url']
        if not model_id:
            model_id = default_configs[self.selected_platform]['model_id']
        
        # 构建请求
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model_id,
            'messages': [
                {'role': 'user', 'content': '你好，这是一个测试消息，请简短回复。'}
            ],
            'max_tokens': 50,
            'temperature': 0.7
        }
        
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 主线程更新UI
                from kivy.clock import Clock
                Clock.schedule_once(
                    lambda dt: self._show_test_success(content),
                    0
                )
            else:
                error_msg = f"状态码: {response.status_code}\n{response.text[:200]}"
                from kivy.clock import Clock
                Clock.schedule_once(
                    lambda dt: self._show_test_error(error_msg),
                    0
                )
                
        except requests.Timeout:
            from kivy.clock import Clock
            Clock.schedule_once(
                lambda dt: self._show_test_error("连接超时，请检查网络或API地址"),
                0
            )
        except Exception as e:
            from kivy.clock import Clock
            Clock.schedule_once(
                lambda dt: self._show_test_error(str(e)),
                0
            )
    
    def _show_test_success(self, response_content):
        """显示测试成功"""
        self.test_dialog.dismiss()
        
        success_dialog = MDDialog(
            title="✅ 连接成功！",
            text=f"API响应正常！\n\n测试回复:\n{response_content[:100]}",
            buttons=[
                MDRaisedButton(
                    text="确定",
                    on_release=lambda x: success_dialog.dismiss()
                )
            ]
        )
        success_dialog.open()
        print(f"[OK] API测试成功: {response_content[:50]}")
    
    def _show_test_error(self, error_msg):
        """显示测试失败"""
        self.test_dialog.dismiss()
        
        error_dialog = MDDialog(
            title="❌ 连接失败",
            text=f"API测试失败:\n\n{error_msg}",
            buttons=[
                MDRaisedButton(
                    text="确定",
                    on_release=lambda x: error_dialog.dismiss()
                )
            ]
        )
        error_dialog.open()
        print(f"[ERROR] API测试失败: {error_msg}")
    
    def save_api_config(self, *args):
        """保存API配置"""
        from config.constants import API_PLATFORMS
        
        api_key = self.api_key_field.text.strip()
        
        if not api_key:
            print("[ERROR] API密钥不能为空")
            return
        
        try:
            base_url = self.base_url_field.text.strip()
            model_id = self.model_id_field.text.strip()
            
            # 如果base_url为空，使用平台默认值
            if not base_url and self.selected_platform in API_PLATFORMS:
                base_url = API_PLATFORMS[self.selected_platform].get('base_url', '')
                print(f"[INFO] 使用默认Base URL: {base_url}")
            
            # 保存到数据库
            self.db.save_api_config(
                platform_type=self.selected_platform,
                api_key=api_key,
                base_url=base_url if base_url else None,
                model_id=model_id if model_id else None
            )
            
            print(f"[OK] API配置已保存: {self.selected_platform}")
            print(f"  Base URL: {base_url}")
            print(f"  Model ID: {model_id}")
            self.api_config_dialog.dismiss()
            
        except Exception as e:
            print(f"[ERROR] 保存失败: {e}")
            import traceback
            traceback.print_exc()
    
    def confirm_clear_today_data(self, *args):
        """确认清除今日数据"""
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        
        # 获取今日刷题数量
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(count), 0) FROM study_records WHERE DATE(record_date) = ?",
            (today,)
        )
        today_count = cursor.fetchone()[0]
        
        confirm_dialog = MDDialog(
            title="⚠️ 确认清除",
            text=f"确定要清除今日({today})的刷题数据吗？\n\n今日已刷: {today_count}题\n\n此操作不可恢复！",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="确认清除",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.clear_today_data(confirm_dialog)
                )
            ]
        )
        confirm_dialog.open()
    
    def clear_today_data(self, dialog):
        """清除今日数据"""
        try:
            from datetime import date
            today = date.today().strftime('%Y-%m-%d')
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 获取今日每个科目的刷题数
            cursor.execute("""
                SELECT subject_id, SUM(count) as today_count 
                FROM study_records 
                WHERE DATE(record_date) = ? 
                GROUP BY subject_id
            """, (today,))
            subject_counts = cursor.fetchall()
            
            # 从subjects表中减去今日的count
            for row in subject_counts:
                cursor.execute("""
                    UPDATE subjects 
                    SET total_count = MAX(0, total_count - ?) 
                    WHERE id = ?
                """, (row['today_count'], row['subject_id']))
            
            # 删除今日所有刷题记录
            cursor.execute(
                "DELETE FROM study_records WHERE DATE(record_date) = ?",
                (today,)
            )
            conn.commit()
            
            dialog.dismiss()
            print(f"[OK] 已清除今日({today})数据并更新科目统计")
            
            # 刷新任务列表
            self.load_tasks()
            
        except Exception as e:
            print(f"[ERROR] 清除失败: {e}")
            import traceback
            traceback.print_exc()
    
    def confirm_clear_subject_data(self, *args):
        """确认清除科目数据"""
        subjects = self.db.get_all_subjects()
        
        if not subjects:
            error_dialog = MDDialog(
                title="提示",
                text="当前没有科目数据",
                buttons=[
                    MDRaisedButton(
                        text="确定",
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ]
            )
            error_dialog.open()
            return
        
        # 创建科目选择列表
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None,
            height=dp(min(len(subjects) * 60 + 60, 400))
        )
        
        hint = MDLabel(
            text="选择要清除数据的科目：",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(hint)
        
        # 科目列表
        scroll = MDScrollView(
            size_hint_y=None,
            height=dp(min(len(subjects) * 60, 340))
        )
        
        subject_list = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        subject_list.bind(minimum_height=subject_list.setter('height'))
        
        for subject in subjects:
            btn = MDRaisedButton(
                text=f"{subject['name']} ({subject['total_count']}题)",
                size_hint=(1, None),
                height=dp(50),
                on_release=lambda x, s=subject: self.confirm_clear_single_subject(s, select_dialog)
            )
            subject_list.add_widget(btn)
        
        scroll.add_widget(subject_list)
        content.add_widget(scroll)
        
        select_dialog = MDDialog(
            title="选择科目",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: select_dialog.dismiss()
                )
            ]
        )
        self.subject_select_dialog = select_dialog
        select_dialog.open()
    
    def confirm_clear_single_subject(self, subject, select_dialog):
        """确认清除单个科目"""
        select_dialog.dismiss()
        
        confirm_dialog = MDDialog(
            title="⚠️ 确认清除",
            text=f"确定要清除【{subject['name']}】的所有刷题数据吗？\n\n总题数: {subject['total_count']}题\n\n此操作不可恢复！",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="确认清除",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.clear_subject_data(subject['id'], confirm_dialog)
                )
            ]
        )
        confirm_dialog.open()
    
    def clear_subject_data(self, subject_id, dialog):
        """清除科目数据"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 删除该科目的所有刷题记录
            cursor.execute(
                "DELETE FROM study_records WHERE subject_id = ?",
                (subject_id,)
            )
            
            # 重置科目的total_count为0
            cursor.execute(
                "UPDATE subjects SET total_count = 0 WHERE id = ?",
                (subject_id,)
            )
            
            conn.commit()
            
            dialog.dismiss()
            print(f"[OK] 已清除科目ID={subject_id}的数据并重置计数")
            
            # 刷新任务列表
            self.load_tasks()
            
        except Exception as e:
            print(f"[ERROR] 清除失败: {e}")
            import traceback
            traceback.print_exc()
    
    def confirm_clear_all_data(self, *args):
        """确认清除全部数据"""
        # 获取总题数
        from services.study_service import StudyService
        study_service = StudyService()
        level_info = study_service.get_level_info()
        total_count = level_info['total_count']
        
        confirm_dialog = MDDialog(
            title="⚠️⚠️⚠️ 危险操作",
            text=f"确定要清除全部刷题数据吗？\n\n总题数: {total_count:,}题\n所有科目的刷题记录\n所有日期的刷题历史\n\n此操作不可恢复！！！",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="我已知晓，确认清除",
                    md_bg_color=(0.7, 0.1, 0.1, 1),
                    on_release=lambda x: self.clear_all_data(confirm_dialog)
                )
            ]
        )
        confirm_dialog.open()
    
    def clear_all_data(self, dialog):
        """清除全部数据"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 删除所有刷题记录
            cursor.execute("DELETE FROM study_records")
            
            # 重置所有科目的total_count为0
            cursor.execute("UPDATE subjects SET total_count = 0")
            
            # 清除所有获得的成就（称号荣誉）
            cursor.execute("DELETE FROM user_achievements")
            
            conn.commit()
            
            dialog.dismiss()
            print("[OK] 已清除全部刷题数据、科目计数和所有成就")
            
            # 刷新任务列表
            self.load_tasks()
            
            # 显示成功提示
            success_dialog = MDDialog(
                title="✅ 清除完成",
                text="所有刷题数据已清除\n所有科目计数已重置为0\n所有成就(称号)已清除\n\n可以重新开始刷题",
                buttons=[
                    MDRaisedButton(
                        text="确定",
                        on_release=lambda x: success_dialog.dismiss()
                    )
                ]
            )
            success_dialog.open()
            
        except Exception as e:
            print(f"[ERROR] 清除失败: {e}")
            import traceback
            traceback.print_exc()
    
    def on_enter(self):
        """进入页面时刷新"""
        self.load_tasks()
    
    def open_daily_goal_dialog(self, *args):
        """打开每日目标设置弹窗"""
        # 获取所有科目
        subjects = self.db.get_all_subjects()
        
        if not subjects:
            error_dialog = MDDialog(
                title="提示",
                text="请先添加科目",
                buttons=[MDRaisedButton(text="确定", on_release=lambda x: error_dialog.dismiss())]
            )
            error_dialog.open()
            return
        
        # 创建弹窗内容
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        content.bind(minimum_height=content.setter('height'))
        
        # 标题
        title_label = MDLabel(
            text="设置每日目标（按科目）",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title_label)
        
        # 滚动容器
        scroll = MDScrollView(size_hint=(1, None), height=dp(300))
        subjects_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        subjects_layout.bind(minimum_height=subjects_layout.setter('height'))
        
        # 存储输入框
        self.daily_goal_fields = {}
        
        # 为每个科目创建输入框
        for subject in subjects:
            subject_box = BoxLayout(
                size_hint_y=None,
                height=dp(50),
                spacing=dp(10)
            )
            
            # 科目名称
            name_label = MDLabel(
                text=subject['name'],
                size_hint_x=0.5
            )
            subject_box.add_widget(name_label)
            
            # 目标输入框
            goal_field = MDTextField(
                text=str(subject.get('daily_target', 0)),
                hint_text="每日目标",
                input_filter="int",
                size_hint_x=0.5
            )
            self.daily_goal_fields[subject['id']] = goal_field
            subject_box.add_widget(goal_field)
            
            subjects_layout.add_widget(subject_box)
        
        scroll.add_widget(subjects_layout)
        content.add_widget(scroll)
        
        # 总计标签
        self.daily_total_label = MDLabel(
            text="总计: 0 题",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        content.add_widget(self.daily_total_label)
        
        # 绑定输入框变化事件
        for field in self.daily_goal_fields.values():
            field.bind(text=self.update_daily_total)
        
        # 初始计算总数
        self.update_daily_total()
        
        # 创建对话框
        self.daily_goal_dialog = MDDialog(
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: self.daily_goal_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=self.save_daily_goals_by_subject
                )
            ]
        )
        self.daily_goal_dialog.open()
    
    def update_daily_total(self, *args):
        """更新每日目标总数"""
        total = 0
        for field in self.daily_goal_fields.values():
            try:
                total += int(field.text) if field.text else 0
            except:
                pass
        self.daily_total_label.text = f"总计: {total} 题"
    
    def save_daily_goals_by_subject(self, *args):
        """保存每日目标（按科目）"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            total = 0
            # 更新每个科目的每日目标
            for subject_id, field in self.daily_goal_fields.items():
                goal = int(field.text) if field.text else 0
                total += goal
                cursor.execute(
                    "UPDATE subjects SET daily_target = ? WHERE id = ?",
                    (goal, subject_id)
                )
            
            # 更新用户的每日总目标
            cursor.execute("UPDATE users SET daily_target = ? WHERE id = 1", (total,))
            
            conn.commit()
            
            # 更新按钮显示
            self.daily_goal_label.text = f"题数    {total}"
            
            # 关闭对话框
            self.daily_goal_dialog.dismiss()
            
            print(f"[OK] 已保存每日目标: {total}题")
            
        except Exception as e:
            print(f"[ERROR] 保存失败: {e}")
            import traceback
            traceback.print_exc()
    
    def open_total_goal_dialog(self, *args):
        """打开终极目标设置弹窗"""
        # 获取所有科目
        subjects = self.db.get_all_subjects()
        
        if not subjects:
            error_dialog = MDDialog(
                title="提示",
                text="请先添加科目",
                buttons=[MDRaisedButton(text="确定", on_release=lambda x: error_dialog.dismiss())]
            )
            error_dialog.open()
            return
        
        # 创建弹窗内容
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        content.bind(minimum_height=content.setter('height'))
        
        # 标题
        title_label = MDLabel(
            text="设置终极目标（按科目）",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title_label)
        
        # 滚动容器
        scroll = MDScrollView(size_hint=(1, None), height=dp(300))
        subjects_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        subjects_layout.bind(minimum_height=subjects_layout.setter('height'))
        
        # 存储输入框
        self.total_goal_fields = {}
        
        # 为每个科目创建输入框
        for subject in subjects:
            subject_box = BoxLayout(
                size_hint_y=None,
                height=dp(50),
                spacing=dp(10)
            )
            
            # 科目名称
            name_label = MDLabel(
                text=subject['name'],
                size_hint_x=0.5
            )
            subject_box.add_widget(name_label)
            
            # 目标输入框
            goal_field = MDTextField(
                text=str(subject.get('total_target', 0)),
                hint_text="终极目标",
                input_filter="int",
                size_hint_x=0.5
            )
            self.total_goal_fields[subject['id']] = goal_field
            subject_box.add_widget(goal_field)
            
            subjects_layout.add_widget(subject_box)
        
        scroll.add_widget(subjects_layout)
        content.add_widget(scroll)
        
        # 总计标签
        self.total_total_label = MDLabel(
            text="总计: 0 题",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        content.add_widget(self.total_total_label)
        
        # 绑定输入框变化事件
        for field in self.total_goal_fields.values():
            field.bind(text=self.update_total_total)
        
        # 初始计算总数
        self.update_total_total()
        
        # 创建对话框
        self.total_goal_dialog = MDDialog(
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: self.total_goal_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=self.save_total_goals_by_subject
                )
            ]
        )
        self.total_goal_dialog.open()
    
    def update_total_total(self, *args):
        """更新终极目标总数"""
        total = 0
        for field in self.total_goal_fields.values():
            try:
                total += int(field.text) if field.text else 0
            except:
                pass
        self.total_total_label.text = f"总计: {total} 题"
    
    def save_total_goals_by_subject(self, *args):
        """保存终极目标（按科目）"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            total = 0
            # 更新每个科目的终极目标
            for subject_id, field in self.total_goal_fields.items():
                goal = int(field.text) if field.text else 0
                total += goal
                cursor.execute(
                    "UPDATE subjects SET total_target = ? WHERE id = ?",
                    (goal, subject_id)
                )
            
            # 更新用户的终极总目标
            cursor.execute("UPDATE users SET total_target = ? WHERE id = 1", (total,))
            
            conn.commit()
            
            # 更新按钮显示
            self.total_goal_label.text = f"题数    {total}"
            
            # 关闭对话框
            self.total_goal_dialog.dismiss()
            
            print(f"[OK] 已保存终极目标: {total}题")
            
        except Exception as e:
            print(f"[ERROR] 保存失败: {e}")
            import traceback
            traceback.print_exc()
