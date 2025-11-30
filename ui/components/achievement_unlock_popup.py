"""成就解锁弹窗组件"""
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock


class AchievementUnlockPopup:
    """成就解锁弹窗"""
    
    def __init__(self):
        self.dialog = None
    
    def show(self, achievement, on_dismiss=None):
        """
        显示成就解锁弹窗
        
        Args:
            achievement: 成就信息字典
            on_dismiss: 关闭回调函数
        """
        from config.constants import ACHIEVEMENT_RARITY
        
        # 获取成就信息
        name = achievement['name']
        description = achievement['description']
        icon = achievement.get('icon', '🏆')
        rarity = achievement.get('rarity', 'BRONZE')
        count = achievement.get('count', 1)
        is_first = achievement.get('is_first', True)
        repeatable = achievement.get('repeatable', False)
        
        # 获取稀有度信息
        rarity_info = ACHIEVEMENT_RARITY.get(rarity, {'name': '青铜', 'icon': '🥉'})
        rarity_name = rarity_info['name']
        rarity_icon = rarity_info['icon']
        
        # 创建内容布局
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
            height=dp(280)
        )
        
        # 添加金色背景和闪光效果
        with content.canvas.before:
            Color(1, 0.95, 0.7, 0.3)  # 淡金色背景
            self.bg_rect = Rectangle(size=content.size, pos=content.pos)
        
        content.bind(size=self._update_rect, pos=self._update_rect)
        
        # 大图标（带动画）
        icon_label = Label(
            text=icon,
            font_size=dp(80),
            size_hint=(1, None),
            height=dp(100),
            color=(1, 0.84, 0, 1)  # 金色
        )
        content.add_widget(icon_label)
        
        # 成就标题
        if repeatable and not is_first:
            title_text = f"🎉 {name} ×{count}"
        else:
            title_text = f"🎉 恭喜解锁成就！"
        
        title_label = Label(
            text=title_text,
            font_size=dp(20),
            bold=True,
            size_hint=(1, None),
            height=dp(30),
            color=(1, 0.6, 0, 1)  # 橙色
        )
        content.add_widget(title_label)
        
        # 成就名称和稀有度
        name_text = f"{rarity_icon} {name}"
        if repeatable and count > 1:
            name_text += f" (第{count}次)"
        
        name_label = Label(
            text=name_text,
            font_size=dp(18),
            size_hint=(1, None),
            height=dp(30),
            color=(0.2, 0.2, 0.2, 1)
        )
        content.add_widget(name_label)
        
        # 成就描述
        desc_label = Label(
            text=description,
            font_size=dp(14),
            size_hint=(1, None),
            height=dp(40),
            color=(0.4, 0.4, 0.4, 1),
            halign='center'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        content.add_widget(desc_label)
        
        # 鼓励语
        if is_first:
            encourage_text = "✨ 太棒了！继续保持！"
        else:
            encourage_text = f"💪 再接再厉！已达成{count}次！"
        
        encourage_label = Label(
            text=encourage_text,
            font_size=dp(16),
            size_hint=(1, None),
            height=dp(30),
            color=(0.2, 0.6, 0.9, 1),
            bold=True
        )
        content.add_widget(encourage_label)
        
        # 创建对话框
        self.dialog = MDDialog(
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),
            buttons=[
                MDRaisedButton(
                    text="太好了！",
                    md_bg_color=(1, 0.6, 0, 1),
                    on_release=lambda x: self._dismiss_with_animation(on_dismiss)
                )
            ]
        )
        
        # 显示对话框
        self.dialog.open()
        
        # 添加图标放大动画
        self._animate_icon(icon_label)
        
        # 添加闪光效果
        Clock.schedule_once(lambda dt: self._add_sparkle_effect(content), 0.1)
    
    def _update_rect(self, instance, value):
        """更新背景矩形"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size = instance.size
            self.bg_rect.pos = instance.pos
    
    def _animate_icon(self, icon_label):
        """图标放大动画"""
        # 从小到大弹出
        icon_label.opacity = 0
        icon_label.font_size = dp(40)
        
        anim = Animation(
            opacity=1,
            font_size=dp(80),
            duration=0.5,
            t='out_elastic'
        )
        anim.start(icon_label)
    
    def _add_sparkle_effect(self, content):
        """添加闪光效果"""
        # 简单的闪光动画
        with content.canvas.after:
            Color(1, 1, 0, 0.5)  # 黄色闪光
            sparkle_rect = Rectangle(size=content.size, pos=content.pos)
        
        # 闪光淡出动画
        def fade_sparkle(dt):
            with content.canvas.after:
                Color(1, 1, 0, 0)
                sparkle_rect.size = content.size
        
        Clock.schedule_once(fade_sparkle, 0.3)
    
    def _dismiss_with_animation(self, callback=None):
        """关闭弹窗（带动画）"""
        if self.dialog:
            self.dialog.dismiss()
            if callback:
                callback()
