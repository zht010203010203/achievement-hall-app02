"""动画工具"""
from kivy.animation import Animation
from kivy.uix.widget import Widget
from typing import Callable


def fade_in(widget: Widget, duration: float = 0.3, callback: Callable = None):
    """淡入动画"""
    widget.opacity = 0
    anim = Animation(opacity=1, duration=duration)
    if callback:
        anim.bind(on_complete=callback)
    anim.start(widget)


def fade_out(widget: Widget, duration: float = 0.3, callback: Callable = None):
    """淡出动画"""
    anim = Animation(opacity=0, duration=duration)
    if callback:
        anim.bind(on_complete=callback)
    anim.start(widget)


def scale_in(widget: Widget, duration: float = 0.3, callback: Callable = None):
    """缩放进入动画"""
    widget.opacity = 0
    widget.scale_x = 0.5
    widget.scale_y = 0.5
    
    anim = Animation(opacity=1, scale_x=1, scale_y=1, duration=duration, t='out_back')
    if callback:
        anim.bind(on_complete=callback)
    anim.start(widget)


def scale_out(widget: Widget, duration: float = 0.2, callback: Callable = None):
    """缩放退出动画"""
    anim = Animation(opacity=0, scale_x=0.5, scale_y=0.5, duration=duration, t='in_back')
    if callback:
        anim.bind(on_complete=callback)
    anim.start(widget)


def slide_in_bottom(widget: Widget, duration: float = 0.3, callback: Callable = None):
    """从底部滑入"""
    original_y = widget.y
    widget.y = -widget.height
    widget.opacity = 0
    
    anim = Animation(y=original_y, opacity=1, duration=duration, t='out_cubic')
    if callback:
        anim.bind(on_complete=callback)
    anim.start(widget)


def slide_out_bottom(widget: Widget, duration: float = 0.2, callback: Callable = None):
    """滑出到底部"""
    anim = Animation(y=-widget.height, opacity=0, duration=duration, t='in_cubic')
    if callback:
        anim.bind(on_complete=callback)
    anim.start(widget)


def pulse(widget: Widget, scale: float = 1.1, duration: float = 0.2):
    """脉冲动画"""
    anim1 = Animation(scale_x=scale, scale_y=scale, duration=duration, t='out_quad')
    anim2 = Animation(scale_x=1, scale_y=1, duration=duration, t='in_quad')
    (anim1 + anim2).start(widget)


def shake(widget: Widget, intensity: float = 10, duration: float = 0.5):
    """抖动动画"""
    original_x = widget.x
    
    anim = (
        Animation(x=original_x + intensity, duration=duration/8) +
        Animation(x=original_x - intensity, duration=duration/4) +
        Animation(x=original_x + intensity/2, duration=duration/4) +
        Animation(x=original_x - intensity/2, duration=duration/4) +
        Animation(x=original_x, duration=duration/8)
    )
    anim.start(widget)


def number_count_up(widget, start: int, end: int, duration: float = 1.0,
                   callback: Callable = None):
    """
    数字滚动动画
    
    Args:
        widget: 需要有 text 属性的组件
        start: 起始数字
        end: 结束数字
        duration: 持续时间
        callback: 完成回调
    """
    from kivy.clock import Clock
    
    steps = 30
    step_duration = duration / steps
    step_value = (end - start) / steps
    
    current_step = [0]
    
    def update(dt):
        current_step[0] += 1
        if current_step[0] <= steps:
            value = int(start + step_value * current_step[0])
            widget.text = f"{value:,}"
        else:
            widget.text = f"{end:,}"
            if callback:
                callback()
            return False
    
    Clock.schedule_interval(update, step_duration)
