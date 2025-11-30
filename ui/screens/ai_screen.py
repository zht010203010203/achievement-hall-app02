"""AI陪伴页面"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label  # 使用Kivy原生Label
from kivy.metrics import dp

from services.ai_service import AIService
from utils.date_helper import format_relative_time
from datetime import datetime


class AIScreen(MDScreen):
    """AI陪伴页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'ai'
        self.ai_service = AIService()
        self.current_identity_id = None  # 当前选中的身份ID
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        # 主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),  # 减小padding适应手机
            spacing=dp(12)  # 调整间距
        )
        
        # 标题
        title = MDLabel(
            text="AI陪伴",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(title)
        
        # 身份切换面板
        identity_panel = self.create_identity_panel()
        main_layout.add_widget(identity_panel)
        
        # 滚动视图
        scroll = MDScrollView()
        
        # 鼓励历史布局
        self.history_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(12),  # 增加卡片间距
            size_hint_y=None,
            padding=[dp(10), dp(10), dp(10), dp(10)]  # 增加padding
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        scroll.add_widget(self.history_layout)
        main_layout.add_widget(scroll)
        
        # 主动请求按钮
        request_btn = MDRaisedButton(
            text="主动请求鼓励",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(0.29, 0.5, 1, 1),
            on_release=self.request_encouragement
        )
        main_layout.add_widget(request_btn)
        
        # 加载历史
        self.load_history()
        
        self.add_widget(main_layout)
    
    def create_identity_panel(self):
        """创建身份管理面板"""
        panel = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            padding=dp(15),
            radius=[dp(15)]
        )
        
        # 标题栏
        title_box = BoxLayout(
            size_hint_y=None,
            height=dp(35)
        )
        
        title = MDLabel(
            text="AI身份",
            font_style="Subtitle1",
            size_hint_x=0.7,
            bold=True
        )
        title_box.add_widget(title)
        
        # 添加身份按钮
        add_btn = MDIconButton(
            icon="plus-circle",
            on_release=self.show_add_identity_dialog
        )
        title_box.add_widget(add_btn)
        
        panel.add_widget(title_box)
        
        # 身份列表（可滚动）
        self.identity_scroll = MDScrollView(
            size_hint_y=None,
            height=dp(150)
        )
        
        self.identity_list = BoxLayout(
            orientation='vertical',
            spacing=dp(8),  # 增加间距
            size_hint_y=None,
            padding=[dp(5), dp(5), dp(5), dp(5)]  # 添加内边距
        )
        self.identity_list.bind(minimum_height=self.identity_list.setter('height'))
        
        self.identity_scroll.add_widget(self.identity_list)
        panel.add_widget(self.identity_scroll)
        
        # 加载身份列表
        self.load_identities()
        
        # 固定面板高度为200dp，内容可滚动
        panel.height = dp(200)
        
        return panel
    
    def load_history(self):
        """加载鼓励历史"""
        # 清空现有历史
        self.history_layout.clear_widgets()
        
        # 只获取最新3条历史记录
        history = self.ai_service.db.get_ai_encouragement_history(limit=3)
        
        if not history:
            # 显示空状态
            empty_label = MDLabel(
                text="暂无AI鼓励记录\n点击下方按钮获取鼓励吧！",
                font_style="Body2",
                halign="center",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(100)
            )
            self.history_layout.add_widget(empty_label)
            return
        
        # 显示历史记录
        for record in history:
            card = self.create_encouragement_card(record)
            self.history_layout.add_widget(card)
    
    def create_encouragement_card(self, record):
        """创建鼓励卡片"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            padding=dp(18),  # 增加padding
            spacing=dp(8),  # 添加内部间距
            radius=[dp(12)],
            size_hint_y=None,
            md_bg_color=(1, 1, 1, 1)  # 白色背景
        )
        
        # 标题行
        title_layout = BoxLayout(
            size_hint_y=None,
            height=dp(30)
        )
        
        # 身份名称
        identity_name = MDLabel(
            text=f"{record.get('identity_name', 'AI')}",
            font_style="Subtitle2",
            size_hint_x=0.7
        )
        title_layout.add_widget(identity_name)
        
        # 时间
        created_at = datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
        time_text = format_relative_time(created_at)
        
        time_label = MDLabel(
            text=time_text,
            font_style="Caption",
            halign="right",
            theme_text_color="Hint",
            size_hint_x=0.3
        )
        title_layout.add_widget(time_label)
        
        card.add_widget(title_layout)
        
        # 鼓励内容（使用Kivy原生Label，完整显示）
        content = Label(
            text=record['content'],
            font_name='ChineseFont',  # 使用中文字体
            font_size='15sp',
            size_hint_y=None,
            color=(0, 0, 0, 1),  # 黑色文字
            padding=[dp(5), dp(5)],  # 内边距
            text_size=(None, None),  # 初始化
            markup=False,
            halign='left',
            valign='top'
        )
        
        # 绑定宽度变化时更新text_size（自动换行）
        def update_text_width(instance, width):
            # 设置text_size宽度为卡片宽度减去padding
            instance.text_size = (width - dp(40), None)
        
        # 绑定texture_size变化时更新高度
        def update_text_height(instance, texture_size):
            instance.height = texture_size[1] + dp(10)
        
        content.bind(width=update_text_width)
        content.bind(texture_size=update_text_height)
        
        card.add_widget(content)
        
        # 动态计算卡片高度
        def update_card_height(instance, height):
            card.height = dp(40) + height + dp(20)
        
        content.bind(height=update_card_height)
        
        # 初始高度
        card.height = dp(150)
        
        return card
    
    def load_identities(self):
        """加载AI身份列表"""
        self.identity_list.clear_widgets()
        
        identities = self.ai_service.db.get_all_ai_identities()
        
        # 如果没有选中身份，默认选中第一个
        if not self.current_identity_id and identities:
            self.current_identity_id = identities[0]['id']
        
        for identity in identities:
            item = self.create_identity_item(identity)
            self.identity_list.add_widget(item)
    
    def create_identity_item(self, identity):
        """创建身份项"""
        is_selected = (identity['id'] == self.current_identity_id)
        
        # 外层容器
        container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(78),
            padding=[0, dp(3), 0, dp(3)]
        )
        
        item = MDCard(
            orientation='horizontal',  # 改为水平布局
            size_hint=(1, None),
            height=dp(72),
            padding=dp(12),
            spacing=dp(10),
            radius=[dp(10)],
            md_bg_color=(0.29, 0.5, 1, 0.15) if is_selected else (0.95, 0.95, 0.95, 1)
        )
        
        # 左侧：身份信息
        info_box = BoxLayout(
            orientation='vertical',
            size_hint_x=0.55  # 占55%宽度
        )
        
        # 名称
        name_label = MDLabel(
            text=f"{'[当前] ' if is_selected else ''}{identity['name']}",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(28)
        )
        info_box.add_widget(name_label)
        
        # 描述（仅显示简短信息）
        desc_text = identity.get('description', '自定义AI助手')
        if len(desc_text) > 12:
            desc_text = desc_text[:12] + '...'
        
        desc_label = MDLabel(
            text=desc_text,
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(20)
        )
        info_box.add_widget(desc_label)
        
        item.add_widget(info_box)
        
        # 中间：选择按钮
        if not is_selected:
            select_btn = MDFlatButton(
                text="选择",
                size_hint_x=None,
                width=dp(60),
                font_size='13sp',
                on_release=lambda x: self.select_identity(identity['id'])
            )
            item.add_widget(select_btn)
        else:
            # 占位，保持布局一致
            item.add_widget(BoxLayout(size_hint_x=None, width=dp(60)))
        
        # 右侧：编辑和删除按钮（靠右对齐）
        action_box = BoxLayout(
            size_hint_x=None,
            width=dp(80),
            spacing=dp(2)
        )
        
        # 编辑按钮
        edit_btn = MDIconButton(
            icon="pencil",
            size_hint_x=None,
            width=dp(38),
            on_release=lambda x: self.show_edit_identity_dialog(identity)
        )
        action_box.add_widget(edit_btn)
        
        # 删除按钮
        delete_btn = MDIconButton(
            icon="delete",
            size_hint_x=None,
            width=dp(38),
            on_release=lambda x: self.delete_identity(identity['id'], identity['name'])
        )
        action_box.add_widget(delete_btn)
        
        item.add_widget(action_box)
        
        container.add_widget(item)
        return container
    
    def select_identity(self, identity_id):
        """选择AI身份"""
        self.current_identity_id = identity_id
        self.load_identities()  # 刷新显示
        
        # 获取身份名称
        identities = self.ai_service.db.get_all_ai_identities()
        identity = next((i for i in identities if i['id'] == identity_id), None)
        if identity:
            print(f"[OK] 已选择AI身份: {identity['name']}")
    
    def show_add_identity_dialog(self, *args):
        """显示添加身份对话框"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
            height=dp(420)
        )
        
        # 提示标签
        hint_label = MDLabel(
            text="提示：分两步定义您的AI助手",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(hint_label)
        
        # 第一步：身份名称
        name_hint = MDLabel(
            text="1. 身份名称（如：女朋友、导师、朋友）",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(25)
        )
        content.add_widget(name_hint)
        
        self.identity_name_field = MDTextField(
            hint_text="输入身份名称",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(self.identity_name_field)
        
        # 第二步：详细描述
        desc_hint = MDLabel(
            text="2. 详细描述（性格、说话风格、行为特点等）",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(25)
        )
        content.add_widget(desc_hint)
        
        self.identity_description_field = MDTextField(
            hint_text="例如：温柔体贴，说话甜美可爱，会关心我的学习进度...",
            multiline=True,
            mode="rectangle",
            size_hint_y=None,
            height=dp(200)
        )
        content.add_widget(self.identity_description_field)
        
        self.add_identity_dialog = MDDialog(
            title="添加自定义AI身份",
            type="custom",
            content_cls=content,
            size_hint=(0.95, None),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: self.add_identity_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=self.save_new_identity
                )
            ]
        )
        self.add_identity_dialog.open()
    
    def save_new_identity(self, *args):
        """保存新身份"""
        name = self.identity_name_field.text.strip()
        description = self.identity_description_field.text.strip()
        
        # 验证输入
        if not name:
            print("[ERROR] 请输入身份名称")
            return
        
        if not description:
            print("[ERROR] 请输入详细描述")
            return
        
        # 构建完整的系统提示词
        system_prompt = f"你是{name}。{description}"
        
        try:
            self.ai_service.db.add_ai_identity(
                name=name,
                description=description[:50] + "..." if len(description) > 50 else description,  # 简短描述
                system_prompt=system_prompt,
                color_primary="#E91E63",  # 粉色
                tone_style="自定义"
            )
            
            print(f"[OK] 已添加自定义身份: {name}")
            self.load_identities()  # 刷新列表
            self.add_identity_dialog.dismiss()
            
        except Exception as e:
            print(f"[ERROR] 添加失败: {e}")
    
    def show_edit_identity_dialog(self, identity):
        """显示编辑身份对话框"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(15),
            size_hint_y=None,
            height=dp(400)
        )
        
        # 提示标签
        hint_label = MDLabel(
            text=f"提示：编辑【{identity['name']}】\n\n修改下方的描述内容：",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(hint_label)
        
        # 编辑文本框（显示原有内容）
        original_prompt = identity.get('system_prompt', '')
        self.edit_identity_field = MDTextField(
            text=original_prompt,
            hint_text="在这里修改AI助手的描述...",
            multiline=True,
            size_hint_y=None,
            height=dp(280)
        )
        content.add_widget(self.edit_identity_field)
        
        self.edit_dialog = MDDialog(
            title="编辑AI身份",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: self.edit_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=lambda x: self.update_identity(identity['id'])
                )
            ]
        )
        self.edit_dialog.open()
    
    def update_identity(self, identity_id):
        """更新身份信息"""
        new_text = self.edit_identity_field.text.strip()
        
        if not new_text:
            print("[ERROR] 内容不能为空")
            return
        
        try:
            # 更新数据库
            self.ai_service.db.update_ai_identity(
                identity_id=identity_id,
                system_prompt=new_text
            )
            
            print(f"[OK] 已更新AI身份: ID={identity_id}")
            self.load_identities()  # 刷新列表
            self.edit_dialog.dismiss()
            
        except Exception as e:
            print(f"[ERROR] 更新失败: {e}")
    
    def delete_identity(self, identity_id, identity_name):
        """删除身份"""
        # 至少保留一个身份
        identities = self.ai_service.db.get_all_ai_identities()
        if len(identities) <= 1:
            print("[WARN] 至少需要保留一个AI身份")
            return
        
        # 确认对话框
        confirm_dialog = MDDialog(
            title="确认删除",
            text=f"确定要删除【{identity_name}】吗？",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="删除",
                    on_release=lambda x: self.do_delete_identity(identity_id, confirm_dialog)
                )
            ]
        )
        confirm_dialog.open()
    
    def do_delete_identity(self, identity_id, dialog):
        """执行删除"""
        try:
            # 如果删除的是当前选中的，需要重新选择
            if identity_id == self.current_identity_id:
                identities = self.ai_service.db.get_all_ai_identities()
                for identity in identities:
                    if identity['id'] != identity_id:
                        self.current_identity_id = identity['id']
                        break
            
            # 调用数据库删除方法
            self.ai_service.db.delete_ai_identity(identity_id)
            
            print(f"[OK] 已删除身份: {identity_id}")
            self.load_identities()
            dialog.dismiss()
            
        except Exception as e:
            print(f"[ERROR] 删除失败: {e}")
    
    def request_encouragement(self, *args):
        """主动请求鼓励"""
        # 显示加载提示
        print("[INFO] AI正在思考中...")
        
        # 异步请求（使用当前选中的身份）
        def callback(result, error):
            if error:
                print(f"[ERROR] 请求失败: {error}")
            else:
                print("[OK] 收到AI鼓励！")
                self.load_history()
        
        try:
            self.ai_service.request_encouragement_async(
                trigger_scene='manual_request',
                callback=callback,
                identity_id=self.current_identity_id  # 使用当前选中的身份
            )
        except Exception as e:
            print(f"[WARN] 未配置API: {str(e)}")
    
    def on_enter(self):
        """进入页面时刷新"""
        self.load_history()
