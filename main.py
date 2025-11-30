"""成就殿堂 - 主程序入口"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.lang import Builder

from config.settings import APP_NAME, APP_VERSION
from database.db_manager import DatabaseManager

# 注册中文字体
try:
    FONT_PATH = "C:/Windows/Fonts/"
    
    # Kivy对TTC格式支持不好，改用TTF格式的黑体
    # 优先尝试simhei.ttf（黑体，TTF格式）
    import os
    if os.path.exists(FONT_PATH + 'simhei.ttf'):
        font_file = 'simhei.ttf'
        print("[INFO] 使用黑体(simhei.ttf)")
    elif os.path.exists(FONT_PATH + 'simsun.ttc'):
        font_file = 'simsun.ttc'
        print("[INFO] 使用宋体(simsun.ttc)")
    else:
        font_file = 'msyh.ttc'
        print("[INFO] 使用微软雅黑(msyh.ttc)")
    
    # 注册中文字体为独立名称，不覆盖系统字体
    LabelBase.register(
        name='ChineseFont',
        fn_regular=FONT_PATH + font_file,
        fn_bold=FONT_PATH + font_file,
        fn_italic=FONT_PATH + font_file,
        fn_bolditalic=FONT_PATH + font_file
    )
    print(f"[OK] 中文字体注册成功: ChineseFont -> {font_file}")
except Exception as e:
    print(f"[ERROR] 字体注册失败: {e}")

# 导入需要patch的组件
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.uix.label import Label  # Kivy原生Label

# Patch MDLabel类，强制使用中文字体（优先中文显示）
_original_mdlabel_init = MDLabel.__init__

def _patched_mdlabel_init(self, **kwargs):
    _original_mdlabel_init(self, **kwargs)
    # 初始化后强制设置中文字体
    self.font_name = 'ChineseFont'
    
    # 绑定font_style变化事件，确保font_name不被覆盖
    def _keep_chinese_font(*args):
        if self.font_name != 'ChineseFont':
            self.font_name = 'ChineseFont'
    
    self.bind(font_style=_keep_chinese_font)

MDLabel.__init__ = _patched_mdlabel_init

# Patch MDTextField类
_original_mdtextfield_init = MDTextField.__init__
def _patched_mdtextfield_init(self, **kwargs):
    kwargs['font_name'] = 'ChineseFont'
    _original_mdtextfield_init(self, **kwargs)
MDTextField.__init__ = _patched_mdtextfield_init

# Patch MDRaisedButton类
_original_mdraised_init = MDRaisedButton.__init__
def _patched_mdraised_init(self, **kwargs):
    _original_mdraised_init(self, **kwargs)
    self.font_name = 'ChineseFont'
    
    def _keep_chinese_font_btn(*args):
        if self.font_name != 'ChineseFont':
            self.font_name = 'ChineseFont'
    
    self.bind(font_style=_keep_chinese_font_btn)
MDRaisedButton.__init__ = _patched_mdraised_init

# Patch MDFlatButton类
_original_mdflat_init = MDFlatButton.__init__
def _patched_mdflat_init(self, **kwargs):
    _original_mdflat_init(self, **kwargs)
    self.font_name = 'ChineseFont'
    
    def _keep_chinese_font_btn(*args):
        if self.font_name != 'ChineseFont':
            self.font_name = 'ChineseFont'
    
    self.bind(font_style=_keep_chinese_font_btn)
MDFlatButton.__init__ = _patched_mdflat_init

# Patch Kivy原生Label类
_original_label_init = Label.__init__
def _patched_label_init(self, **kwargs):
    # 如果没有指定font_name，使用ChineseFont
    if 'font_name' not in kwargs:
        kwargs['font_name'] = 'ChineseFont'
    _original_label_init(self, **kwargs)
Label.__init__ = _patched_label_init

print("[OK] KivyMD和Kivy组件已强制使用ChineseFont（包括H4等样式）")

# 导入所有页面
from ui.screens.home_screen import HomeScreen
from ui.screens.record_screen import RecordScreen
from ui.screens.stats_screen import StatsScreen
from ui.screens.achievement_screen import AchievementScreen
from ui.screens.ai_screen import AIScreen
from ui.screens.settings_screen import SettingsScreen


# 定义可点击的图片按钮类
class ImageButton(ButtonBehavior, Image):
    """可点击的图片按钮"""
    pass


class AchievementApp(MDApp):
    """成就殿堂应用主类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APP_NAME
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Light"
        
        # 不要修改theme_cls.font_styles，这会破坏图标字体
        # 改为在具体组件中通过patch指定字体
        
        # 初始化数据库
        self.db = DatabaseManager()
        
        # 屏幕管理器
        self.screen_manager = None
    
    def build(self):
        """构建应用界面"""
        # 设置窗口大小（开发时使用，打包后会自适应）
        Window.size = (360, 640)
        
        # 创建主布局
        main_layout = MDBoxLayout(orientation='vertical')
        
        # 创建屏幕管理器
        self.screen_manager = MDScreenManager()
        
        # 添加所有页面到屏幕管理器（直接使用Screen实例，不要二次包装）
        self.page_widgets = {}
        
        self.page_widgets['home'] = HomeScreen()
        self.screen_manager.add_widget(self.page_widgets['home'])
        
        self.page_widgets['record'] = RecordScreen()
        self.screen_manager.add_widget(self.page_widgets['record'])
        
        self.page_widgets['stats'] = StatsScreen()
        self.screen_manager.add_widget(self.page_widgets['stats'])
        
        self.page_widgets['achievement'] = AchievementScreen()
        self.screen_manager.add_widget(self.page_widgets['achievement'])
        
        self.page_widgets['ai'] = AIScreen()
        self.screen_manager.add_widget(self.page_widgets['ai'])
        
        self.page_widgets['settings'] = SettingsScreen()
        self.screen_manager.add_widget(self.page_widgets['settings'])
        
        # 创建底部导航栏
        bottom_bar = MDBoxLayout(
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=(1, 1, 1, 1),
            padding=[0, 0, 0, 0]
        )
        
        # 导航按钮配置（使用图片替代图标）
        nav_buttons = [
            ('home', 'assets/icons/home.png', '殿堂'),
            ('record', 'assets/icons/record.png', '刷题'),
            ('stats', 'assets/icons/stats.png', '统计'),
            ('achievement', 'assets/icons/achievement.png', '成就'),
            ('ai', 'assets/icons/ai.png', 'AI'),
            ('settings', 'assets/icons/settings.png', '设置')
        ]
        
        # 创建导航按钮（使用图片）
        temp_icon_map = {
            'home': 'home',
            'record': 'target',
            'stats': 'chart-bar',
            'achievement': 'trophy',
            'ai': 'robot',
            'settings': 'cog'
        }
        
        for screen_name, icon_path, text in nav_buttons:
            # 创建按钮布局
            btn_layout = BoxLayout(
                orientation='vertical',
                size_hint_x=1
            )
            
            # 检查图片是否存在
            if os.path.exists(icon_path):
                # 使用图片按钮
                btn = ImageButton(
                    source=icon_path,
                    size_hint=(None, None),
                    size=(dp(32), dp(32)),
                    pos_hint={'center_x': 0.5}
                )
                btn.bind(on_release=lambda x, s=screen_name: self.switch_screen(s))
                btn_layout.add_widget(btn)
            else:
                # 临时使用MDIconButton（图标字体可能不显示）
                btn = MDIconButton(
                    icon=temp_icon_map.get(screen_name, 'help'),
                    on_release=lambda x, s=screen_name: self.switch_screen(s)
                )
                btn_layout.add_widget(btn)
            
            bottom_bar.add_widget(btn_layout)
        
        # 组装主布局
        main_layout.add_widget(self.screen_manager)
        main_layout.add_widget(bottom_bar)
        
        return main_layout
    
    def switch_screen(self, screen_name):
        """切换屏幕并刷新数据"""
        self.screen_manager.current = screen_name
        
        # 触发页面刷新
        page_widget = self.page_widgets.get(screen_name)
        if page_widget and hasattr(page_widget, 'on_enter'):
            try:
                page_widget.on_enter()
            except Exception as e:
                print(f"[WARN] 页面刷新失败 {screen_name}: {e}")
    
    def on_start(self):
        """应用启动时调用"""
        print(f"✅ {APP_NAME} v{APP_VERSION} 启动成功！")
        print(f"📊 数据库路径: {self.db.db_path}")
        
        # 检查数据库初始化
        try:
            total_count = self.db.get_total_count()
            print(f"📚 当前总题数: {total_count}")
        except Exception as e:
            print(f"❌ 数据库错误: {e}")
    
    def on_stop(self):
        """应用关闭时调用"""
        if self.db:
            self.db.close()
        print(f"👋 {APP_NAME} 已关闭")


if __name__ == '__main__':
    AchievementApp().run()
