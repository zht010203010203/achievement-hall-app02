"""超炫酷成就解锁动画"""
from kivy.uix.modalview import ModalView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
import random
import math


class AchievementUnlockAnimation(ModalView):
    """成就解锁动画弹窗"""
    
    def __init__(self, achievement_data, **kwargs):
        super().__init__(**kwargs)
        
        # 配置弹窗样式
        self.auto_dismiss = False
        self.background = ''
        self.background_color = (0, 0, 0, 0)  # 初始透明
        self.size_hint = (1, 1)
        
        # 成就数据
        self.achievement = achievement_data
        
        # 根据稀有度设置颜色
        self.rarity_colors = {
            '青铜': (0.8, 0.5, 0.2, 1),      # 棕色
            '白银': (0.75, 0.75, 0.75, 1),   # 银色
            '黄金': (1, 0.84, 0, 1),          # 金色
            '钻石': (0.4, 0.7, 1, 1),         # 钻石蓝
            '传说': (0.7, 0.3, 1, 1)          # 紫色
        }
        
        # 获取稀有度颜色
        rarity = achievement_data.get('rarity', '青铜')
        self.main_color = self.rarity_colors.get(rarity, (1, 0.84, 0, 1))
        
        # 粒子系统
        self.particles = []
        
        # 构建UI
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        # 主容器
        container = FloatLayout()
        
        # 1. 背景遮罩（会动画渐入）
        with container.canvas.before:
            self.bg_color = Color(0, 0, 0, 0)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=lambda *x: setattr(self.bg_rect, 'pos', self.pos))
        self.bind(size=lambda *x: setattr(self.bg_rect, 'size', self.size))
        
        # 2. 光芒效果层
        self.glow_layer = FloatLayout(
            size_hint=(None, None),
            size=(dp(300), dp(300)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # 创建多个旋转光芒
        for i in range(6):
            glow = FloatLayout(
                size_hint=(None, None),
                size=(dp(300), dp(300)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            
            angle = i * 60
            with glow.canvas:
                Color(*self.main_color[:3], 0.3)
                # 创建光线（使用Line绘制）
                x1 = dp(150)
                y1 = dp(150)
                x2 = x1 + dp(100) * math.cos(math.radians(angle))
                y2 = y1 + dp(100) * math.sin(math.radians(angle))
                Line(points=[x1, y1, x2, y2], width=dp(3))
            
            self.glow_layer.add_widget(glow)
        
        container.add_widget(self.glow_layer)
        
        # 3. 成就卡片
        self.card = MDCard(
            size_hint=(None, None),
            size=(dp(300), dp(200)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            md_bg_color=(1, 1, 1, 0.95),
            radius=[dp(20)],
            elevation=10,
            opacity=0  # 初始不可见
        )
        
        # 卡片内容布局
        card_layout = FloatLayout()
        
        # 稀有度光环（圆形光晕）
        with card_layout.canvas.before:
            Color(*self.main_color[:3], 0.2)
            self.halo = Ellipse(
                pos=(dp(100), dp(50)),
                size=(dp(100), dp(100))
            )
        
        # 成就名称
        self.name_label = MDLabel(
            text=self.achievement['name'],
            font_style='H5',
            halign='center',
            pos_hint={'center_x': 0.5, 'top': 0.85},
            size_hint=(0.9, None),
            height=dp(50),
            opacity=0  # 初始不可见
        )
        card_layout.add_widget(self.name_label)
        
        # 稀有度标签
        self.rarity_label = MDLabel(
            text=f"✨ {self.achievement.get('rarity', '青铜')} ✨",
            font_style='H6',
            halign='center',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            theme_text_color='Custom',
            text_color=self.main_color,
            opacity=0
        )
        card_layout.add_widget(self.rarity_label)
        
        # 成就描述
        self.desc_label = MDLabel(
            text=self.achievement.get('description', ''),
            font_style='Body2',
            halign='center',
            pos_hint={'center_x': 0.5, 'top': 0.3},
            size_hint=(0.85, None),
            height=dp(40),
            opacity=0  # 初始不可见
        )
        card_layout.add_widget(self.desc_label)
        
        self.card.add_widget(card_layout)
        container.add_widget(self.card)
        
        # 4. 粒子容器
        self.particle_layer = FloatLayout()
        container.add_widget(self.particle_layer)
        
        self.add_widget(container)
    
    def start_animation(self):
        """开始播放动画"""
        # 0.0s - 背景遮罩渐入
        anim_bg = Animation(a=0.7, duration=0.3)
        anim_bg.start(self.bg_color)
        
        # 0.1s - 粒子爆炸
        Clock.schedule_once(lambda dt: self.create_particle_burst(), 0.1)
        
        # 0.2s - 光芒旋转开始
        Clock.schedule_once(lambda dt: self.start_glow_rotation(), 0.2)
        
        # 0.3s - 卡片弹性放大入场
        Clock.schedule_once(lambda dt: self.animate_card_entrance(), 0.3)
        
        # 0.6s - 成就名称飞入
        Clock.schedule_once(lambda dt: self.animate_name(), 0.6)
        
        # 0.7s - 稀有度标签
        Clock.schedule_once(lambda dt: self.animate_rarity(), 0.7)
        
        # 0.8s - 描述渐入
        Clock.schedule_once(lambda dt: self.animate_description(), 0.8)
        
        # 1.0s - 星星飘落
        Clock.schedule_once(lambda dt: self.create_star_fall(), 1.0)
        
        # 3.5s - 自动关闭
        Clock.schedule_once(lambda dt: self.dismiss_with_animation(), 3.5)
    
    def create_particle_burst(self):
        """创建粒子爆炸效果"""
        particle_count = 30
        
        for _ in range(particle_count):
            particle = Label(
                text='✨',
                font_size=dp(random.randint(20, 40)),
                size_hint=(None, None),
                size=(dp(30), dp(30)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                opacity=1
            )
            
            # 随机方向和距离
            angle = random.uniform(0, 360)
            distance = random.uniform(100, 250)
            end_x = 0.5 + (distance / self.width) * math.cos(math.radians(angle))
            end_y = 0.5 + (distance / self.height) * math.sin(math.radians(angle))
            
            # 动画：向外扩散并淡出
            anim = Animation(
                pos_hint={'center_x': end_x, 'center_y': end_y},
                opacity=0,
                duration=0.8,
                t='out_quad'
            )
            anim.bind(on_complete=lambda *x: self.particle_layer.remove_widget(particle))
            
            self.particle_layer.add_widget(particle)
            anim.start(particle)
    
    def start_glow_rotation(self):
        """开始光芒旋转"""
        # 注意：FloatLayout不支持rotation属性
        # 改为使用缩放和透明度动画代替旋转效果
        anim = Animation(opacity=0.8, duration=1, t='in_out_sine')
        anim += Animation(opacity=0.5, duration=1, t='in_out_sine')
        anim.repeat = True
        try:
            anim.start(self.glow_layer)
        except Exception as e:
            print(f"[WARN] 光芒动画失败: {e}")
    
    def animate_card_entrance(self):
        """卡片弹性入场"""
        # 从小到大弹性放大
        self.card.size = (dp(50), dp(30))
        self.card.opacity = 1
        
        anim = Animation(
            size=(dp(300), dp(200)),
            duration=0.6,
            t='out_elastic'  # 弹性缓动
        )
        anim.start(self.card)
        
        # 光环跟随
        anim_halo = Animation(
            size=(dp(100), dp(100)),
            duration=0.5,
            t='out_back'
        )
        anim_halo.start(self)  # 需要触发重绘
    
    def animate_name(self):
        """成就名称飞入"""
        # 从上方飞入
        self.name_label.pos_hint = {'center_x': 0.5, 'top': 1.5}
        self.name_label.opacity = 1
        
        anim = Animation(
            pos_hint={'center_x': 0.5, 'top': 0.85},
            duration=0.4,
            t='out_back'
        )
        anim.start(self.name_label)
    
    def animate_rarity(self):
        """稀有度标签动画"""
        # 放大淡入
        self.rarity_label.opacity = 0
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.rarity_label)
    
    def animate_description(self):
        """描述渐入"""
        anim = Animation(opacity=1, duration=0.4)
        anim.start(self.desc_label)
    
    def create_star_fall(self):
        """创建星星飘落效果"""
        for _ in range(15):
            star = Label(
                text=random.choice(['⭐', '✨', '💫']),
                font_size=dp(random.randint(15, 30)),
                size_hint=(None, None),
                size=(dp(30), dp(30)),
                pos_hint={
                    'center_x': random.uniform(0.2, 0.8),
                    'center_y': 1.2
                },
                opacity=0.8
            )
            
            # 飘落动画
            end_y = random.uniform(-0.2, 0.2)
            anim = Animation(
                pos_hint={'center_x': star.pos_hint['center_x'], 'center_y': end_y},
                opacity=0,
                duration=random.uniform(1.5, 2.5),
                t='in_quad'
            )
            anim.bind(on_complete=lambda *x: self.particle_layer.remove_widget(star))
            
            self.particle_layer.add_widget(star)
            
            # 延迟启动，制造连续飘落效果
            Clock.schedule_once(
                lambda dt, a=anim, s=star: a.start(s),
                random.uniform(0, 0.5)
            )
    
    def dismiss_with_animation(self):
        """带动画的关闭"""
        # 卡片缩小
        anim_card = Animation(
            size=(dp(50), dp(30)),
            opacity=0,
            duration=0.3,
            t='in_back'
        )
        anim_card.start(self.card)
        
        # 背景淡出
        anim_bg = Animation(a=0, duration=0.3)
        anim_bg.bind(on_complete=lambda *x: self.dismiss())
        anim_bg.start(self.bg_color)
    
    def on_touch_down(self, touch):
        """点击任意位置关闭"""
        if self.collide_point(*touch.pos):
            self.dismiss_with_animation()
            return True
        return super().on_touch_down(touch)


def show_achievement_unlock(achievement_data):
    """显示成就解锁动画的便捷函数"""
    from ui.components.achievement_unlock_popup import AchievementUnlockPopup
    popup = AchievementUnlockPopup()
    popup.show(achievement_data)
