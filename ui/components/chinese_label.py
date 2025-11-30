"""支持中文的Label组件"""
from kivymd.uix.label import MDLabel


class ChineseLabel(MDLabel):
    """自动使用中文字体的Label"""
    
    def __init__(self, **kwargs):
        # 默认使用Roboto字体（已注册为微软雅黑）
        if 'font_name' not in kwargs:
            kwargs['font_name'] = 'Roboto'
        super().__init__(**kwargs)
