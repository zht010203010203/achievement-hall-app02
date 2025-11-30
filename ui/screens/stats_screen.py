"""统计页面"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label  # 原生Label
from kivymd.uix.behaviors import HoverBehavior
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line

from services.stats_service import StatsService


class HoverableDayBox(HoverBehavior, BoxLayout):
    """可悬停的日期单元格"""
    
    def __init__(self, day, count, date_color, count_color, bg_color, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(5)  # 增大padding
        
        self.day = day
        self.count = count
        self.date_color = date_color
        self.count_color = count_color
        self.bg_color = bg_color
        
        # 创建标签 - 确保垂直居中
        self.label = MDLabel(
            text=str(day),
            font_size="15sp",  # 稍大一点
            halign="center",
            valign="middle",  # 使用middle
            theme_text_color="Custom",
            text_color=date_color
        )
        self.label.bind(size=self.label.setter('text_size'))  # 让valign生效
        
        # 只添加label，让它自动居中
        self.add_widget(self.label)
        
        # 背景
        with self.canvas.before:
            self.bg_color_instruction = Color(*bg_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_enter(self, *args):
        """鼠标进入时显示题数"""
        if self.count > 0:
            self.label.text = str(self.count)  # 直接显示数字，不加括号
            self.label.font_size = "13sp"  # 可以稍大一点
            self.label.text_color = self.count_color
        else:
            # 未打卡时显示横线
            self.label.text = "-"
            self.label.font_size = "13sp"
            self.label.text_color = self.count_color
    
    def on_leave(self, *args):
        """鼠标离开时显示日期"""
        self.label.text = str(self.day)
        self.label.font_size = "15sp"
        self.label.text_color = self.date_color


class StatsScreen(MDScreen):
    """统计页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'stats'
        
        # 初始化服务
        self.stats_service = StatsService()
        
        # 构建UI
        self.build_ui()
    
    def on_enter(self):
        """每次进入页面时刷新数据"""
        print("[INFO] 进入成长轨迹页面，刷新数据...")
        # 重新构建UI以刷新所有数据
        self.clear_widgets()
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        # 滚动视图
        scroll = MDScrollView()
        
        # 主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20),
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # 标题
        title = MDLabel(
            text="成长轨迹",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        main_layout.add_widget(title)
        
        # 学习日历（热力图）
        heatmap_card = self.create_heatmap_card()
        main_layout.add_widget(heatmap_card)
        
        # 趋势分析
        trend_card = self.create_trend_card()
        main_layout.add_widget(trend_card)
        
        # 统计卡片
        stats_cards = self.create_stats_cards()
        main_layout.add_widget(stats_cards)
        
        scroll.add_widget(main_layout)
        self.add_widget(scroll)
    
    def create_heatmap_card(self):
        """创建热力图卡片 - 只显示最近一个月"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(260),  # 增加高度以容纳连续打卡和颜色说明
            padding=dp(15),
            radius=[dp(15)]
        )
        
        # 标题行（包含连续打卡天数）
        title_layout = BoxLayout(
            size_hint_y=None,
            height=dp(35)
        )
        
        # 改为可点击的按钮
        title_btn = MDFlatButton(
            text="学习日历",
            font_style="Subtitle1",
            size_hint_x=0.6,
            on_release=self.open_full_calendar_dialog
        )
        title_layout.add_widget(title_btn)
        
        # 连续打卡天数
        overview = self.stats_service.get_overview_stats()
        
        streak_label = MDLabel(
            text=f"连续打卡 {overview.get('streak_days', 0)} 天",
            font_style="Caption",
            halign="right",
            theme_text_color="Primary",
            size_hint_x=0.4
        )
        title_layout.add_widget(streak_label)
        
        card.add_widget(title_layout)
        
        # 热力图网格 - 只显示最近30天
        heatmap_grid = GridLayout(
            cols=7,  # 一周7天
            spacing=dp(6),  # 增加间距
            size_hint_y=None,
            height=dp(150),
            padding=[dp(5), 0]
        )
        
        # 获取热力图数据
        heatmap_data = self.stats_service.get_heatmap_data()
        
        # 只显示最近30天
        recent_30_days = heatmap_data[-30:]
        
        # 调试：打印关键信息
        from datetime import date
        today = date.today()
        print(f"[DEBUG] 今天日期：{today}")
        print(f"[DEBUG] 热力图数据范围：{recent_30_days[0]['date']} 到 {recent_30_days[-1]['date']}")
        print(f"[DEBUG] 最近5天数据：")
        for day in recent_30_days[-5:]:
            print(f"  {day['date']}: {day['count']}题, level={day['level']}, 星期{day['weekday']}")
        
        # 计算需要补齐的天数（让第一天对齐到正确的星期）
        first_day_weekday = recent_30_days[0]['weekday']  # 0=周一, 6=周日
        # 前面需要留空的格子数
        empty_cells_before = first_day_weekday
        
        # 添加前置空白单元格
        for _ in range(empty_cells_before):
            empty_widget = BoxLayout()
            heatmap_grid.add_widget(empty_widget)
        
        # 显示每个日期方块
        for i, day_data in enumerate(recent_30_days):
            day_widget = BoxLayout()
            
            # 判断是否是今天
            is_today = day_data['date'] == str(today)
            
            # 根据level设置颜色
            level = day_data['level']
            # 0 - 未打卡（浅灰）
            # 1 - 打卡未完成目标（淡蓝）
            # 2 - 完成目标（深蓝）
            colors = [
                (0.90, 0.90, 0.90, 1),  # level 0 - 未打卡（浅灰）
                (0.70, 0.85, 1, 1),     # level 1 - 打卡未完成（淡蓝）
                (0.18, 0.45, 0.95, 1)   # level 2 - 完成目标（深蓝）
            ]
            
            # 确保level在范围内
            color = colors[min(level, 2)]
            
            with day_widget.canvas:
                # 填充颜色
                Color(*color)
                rect = Rectangle(pos=day_widget.pos, size=day_widget.size)
                
                # 如果是今天，添加边框
                if is_today:
                    Color(1, 0.5, 0, 1)  # 橙色边框
                    border = Line(rectangle=(day_widget.x, day_widget.y, day_widget.width, day_widget.height), width=1.5)
            
            # 绑定位置和大小更新
            if is_today:
                def update_rect_with_border(instance, value, rect=rect, border=border):
                    rect.pos = instance.pos
                    rect.size = instance.size
                    border.rectangle = (instance.x, instance.y, instance.width, instance.height)
                day_widget.bind(pos=update_rect_with_border, size=update_rect_with_border)
            else:
                def update_rect(instance, value, rect=rect):
                    rect.pos = instance.pos
                    rect.size = instance.size
                day_widget.bind(pos=update_rect, size=update_rect)
            
            heatmap_grid.add_widget(day_widget)
        
        card.add_widget(heatmap_grid)
        
        # 添加颜色说明
        legend_layout = BoxLayout(
            size_hint_y=None,
            height=dp(25),
            spacing=dp(15),
            padding=[dp(10), dp(5), dp(10), 0]
        )
        
        # 灰色 - 未打卡
        legend1 = BoxLayout(size_hint_x=None, width=dp(80), spacing=dp(5))
        legend1_box = BoxLayout(size_hint=(None, None), size=(dp(12), dp(12)))
        with legend1_box.canvas:
            Color(0.90, 0.90, 0.90, 1)
            Rectangle(pos=legend1_box.pos, size=legend1_box.size)
        legend1_box.bind(pos=lambda i, v: setattr(legend1_box.canvas.children[-1], 'pos', i.pos))
        legend1.add_widget(legend1_box)
        legend1.add_widget(MDLabel(text="未打卡", font_size='10sp'))
        legend_layout.add_widget(legend1)
        
        # 淡蓝 - 打卡未完成
        legend2 = BoxLayout(size_hint_x=None, width=dp(80), spacing=dp(5))
        legend2_box = BoxLayout(size_hint=(None, None), size=(dp(12), dp(12)))
        with legend2_box.canvas:
            Color(0.70, 0.85, 1, 1)
            Rectangle(pos=legend2_box.pos, size=legend2_box.size)
        legend2_box.bind(pos=lambda i, v: setattr(legend2_box.canvas.children[-1], 'pos', i.pos))
        legend2.add_widget(legend2_box)
        legend2.add_widget(MDLabel(text="未完成", font_size='10sp'))
        legend_layout.add_widget(legend2)
        
        # 深蓝 - 完成目标
        legend3 = BoxLayout(size_hint_x=None, width=dp(80), spacing=dp(5))
        legend3_box = BoxLayout(size_hint=(None, None), size=(dp(12), dp(12)))
        with legend3_box.canvas:
            Color(0.18, 0.45, 0.95, 1)
            Rectangle(pos=legend3_box.pos, size=legend3_box.size)
        legend3_box.bind(pos=lambda i, v: setattr(legend3_box.canvas.children[-1], 'pos', i.pos))
        legend3.add_widget(legend3_box)
        legend3.add_widget(MDLabel(text="已完成", font_size='10sp'))
        legend_layout.add_widget(legend3)
        
        card.add_widget(legend_layout)
        
        return card
    
    def create_trend_card(self):
        """创建趋势卡片 - 本周刷题统计"""
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(220),
            padding=dp(15),
            radius=[dp(15)]
        )
        
        # 标题
        title = MDLabel(
            text="本周刷题统计",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title)
        
        # 获取本周数据
        weekly = self.stats_service.get_weekly_trend()
        
        # 调试日志：打印本周数据
        print(f"[DEBUG] 本周刷题数据：")
        for day in weekly['daily_data']:
            print(f"  {day['weekday_cn']}: {day['count']}题")
        
        # 主图表区域（包含Y轴和柱状图）
        chart_main = BoxLayout(
            size_hint_y=None,
            height=dp(150),
            spacing=dp(5)
        )
        
        # Y轴智能计算（至少200，如果有更大数据则向上取整）
        max_count = max([d['count'] for d in weekly['daily_data']]) if weekly['daily_data'] else 0
        
        if max_count <= 200:
            y_max = 200
        elif max_count <= 300:
            y_max = 300
        elif max_count <= 500:
            y_max = 500
        else:
            # 向上取整到100的倍数
            y_max = ((max_count + 99) // 100) * 100
        
        # Y轴刻度标签（固定宽度）
        y_axis = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(40)  # 足够显示3位数
        )
        
        # 显示4个刻度（从上到下）
        for i in range(4, -1, -1):
            tick_value = (y_max * i) // 4
            tick_label = MDLabel(
                text=str(tick_value),
                font_style="Caption",
                halign="right",
                size_hint_y=1
            )
            y_axis.add_widget(tick_label)
        
        chart_main.add_widget(y_axis)
        
        # 柱状图区域
        chart_container = BoxLayout(
            orientation='vertical',
            size_hint_x=1
        )
        
        # 柱状图（高度固定为98，为数字标签留出空间）
        bars_layout = BoxLayout(
            size_hint_y=None,
            height=dp(98),
            spacing=dp(8)
        )
        
        for day_data in weekly['daily_data']:
            bar_column = BoxLayout(
                orientation='vertical',
                size_hint_x=1
            )
            
            count = day_data['count']
            
            # 柱子容器（包含柱子和数字）
            bar_container = BoxLayout(
                orientation='vertical'
            )
            
            if count == 0:
                # 没有数据，完全空白
                empty_spacer = BoxLayout()
                bar_container.add_widget(empty_spacer)
            else:
                # 计算柱子高度（相对于y_max，确保不超过100%）
                bar_ratio = min(count / y_max, 1.0)
                label_height = 18  # 数字标签高度
                
                # 1. 先添加上方空白（把数字和柱子一起往下推）
                spacer_ratio = 1 - bar_ratio - (label_height / 98)  # 98是柱状图总高度
                if spacer_ratio > 0:
                    spacer = BoxLayout(
                        size_hint_y=spacer_ratio
                    )
                    bar_container.add_widget(spacer)
                
                # 2. 然后添加数字标签（紧贴柱子顶部）
                count_label = Label(
                    text=str(count),
                    font_name='ChineseFont',  # 使用中文字体
                    font_size='10sp',  # 缩小字体
                    halign="center",
                    valign="bottom",  # 底部对齐，贴近柱子
                    color=(0, 0, 0, 0.87),
                    size_hint_y=None,
                    height=dp(label_height)
                )
                bar_container.add_widget(count_label)
                
                # 3. 最后添加柱子本身
                bar = BoxLayout(
                    size_hint_y=bar_ratio
                )
                
                # 今天用深蓝色
                color = (0.18, 0.45, 0.95, 1) if day_data['is_today'] else (0.55, 0.75, 1, 1)
                
                with bar.canvas:
                    Color(*color)
                    bar_rect = Rectangle(pos=bar.pos, size=bar.size)
                
                def update_bar_rect(instance, value, rect=bar_rect):
                    rect.pos = instance.pos
                    rect.size = instance.size
                
                bar.bind(pos=update_bar_rect, size=update_bar_rect)
                bar_container.add_widget(bar)
            
            bar_column.add_widget(bar_container)
            bars_layout.add_widget(bar_column)
        
        chart_container.add_widget(bars_layout)
        
        # X轴标签（星期）
        week_labels = BoxLayout(
            size_hint_y=None,
            height=dp(20),
            spacing=dp(8)
        )
        
        for day_data in weekly['daily_data']:
            label = MDLabel(
                text=day_data['weekday_cn'],
                font_style="Caption",
                halign="center",
                size_hint_x=1
            )
            week_labels.add_widget(label)
        
        chart_container.add_widget(week_labels)
        chart_main.add_widget(chart_container)
        card.add_widget(chart_main)
        
        return card
    
    def create_stats_cards(self):
        """创建AI智能报告按钮"""
        from kivymd.uix.button import MDRaisedButton
        
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(220),
            padding=dp(20),
            radius=[dp(15)]
        )
        
        # 标题
        title = MDLabel(
            text="📊 AI智能报告",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(35)
        )
        card.add_widget(title)
        
        # 说明
        desc = MDLabel(
            text="AI为你分析学习数据，生成专属总结报告",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(desc)
        
        # 按钮容器
        btn_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(135)
        )
        
        # 周报按钮
        week_btn = MDRaisedButton(
            text="📅 本周报告",
            size_hint=(1, None),
            height=dp(45),
            md_bg_color=(0.2, 0.6, 0.9, 1),  # 蓝色
            on_release=lambda x: self.generate_report('week')
        )
        btn_layout.add_widget(week_btn)
        
        # 月报按钮
        month_btn = MDRaisedButton(
            text="📆 本月报告",
            size_hint=(1, None),
            height=dp(45),
            md_bg_color=(0.3, 0.7, 0.4, 1),  # 绿色
            on_release=lambda x: self.generate_report('month')
        )
        btn_layout.add_widget(month_btn)
        
        # 年报按钮
        year_btn = MDRaisedButton(
            text="📖 年度报告",
            size_hint=(1, None),
            height=dp(45),
            md_bg_color=(0.9, 0.5, 0.2, 1),  # 橙色
            on_release=lambda x: self.generate_report('year')
        )
        btn_layout.add_widget(year_btn)
        
        card.add_widget(btn_layout)
        
        return card
    
    def generate_report(self, report_type):
        """生成AI报告"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton, MDRaisedButton
        
        # 标题映射
        title_map = {
            'week': '本周',
            'month': '本月',
            'year': '今年'
        }
        
        # 显示加载提示
        loading_dialog = MDDialog(
            title="📝 正在生成报告...",
            text=f"AI小助手正在帮你回顾{title_map[report_type]}的学习情况\n请稍等片刻～",
            auto_dismiss=False
        )
        loading_dialog.open()
        
        # 异步生成报告
        import threading
        from kivy.clock import Clock
        
        def _generate():
            try:
                # 收集数据
                data = self._collect_report_data(report_type)
                
                # 调用AI生成报告
                report_text = self._call_ai_for_report(report_type, data)
                
                # 关闭加载对话框并显示报告
                Clock.schedule_once(lambda dt: self._show_report(loading_dialog, report_type, report_text), 0)
                
            except Exception as err:
                error_msg = str(err)
                Clock.schedule_once(lambda dt: self._show_error(loading_dialog, error_msg), 0)
        
        thread = threading.Thread(target=_generate)
        thread.start()
    
    def _collect_report_data(self, report_type):
        """收集报告数据"""
        from datetime import datetime, timedelta
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 确定时间范围
        now = datetime.now()
        if report_type == 'week':
            start_date = (now - timedelta(days=6)).strftime('%Y-%m-%d')
            title = "本周"
        elif report_type == 'month':
            start_date = now.replace(day=1).strftime('%Y-%m-%d')
            title = "本月"
        else:  # year
            start_date = now.replace(month=1, day=1).strftime('%Y-%m-%d')
            title = f"{now.year}年"
        
        end_date = now.strftime('%Y-%m-%d')
        
        # 统计总题数
        cursor.execute("""
            SELECT COALESCE(SUM(count), 0) as total
            FROM study_records
            WHERE DATE(record_date) BETWEEN ? AND ?
        """, (start_date, end_date))
        total_count = cursor.fetchone()['total']
        
        # 每天的刷题数
        cursor.execute("""
            SELECT DATE(record_date) as date, SUM(count) as count
            FROM study_records
            WHERE DATE(record_date) BETWEEN ? AND ?
            GROUP BY DATE(record_date)
            ORDER BY date
        """, (start_date, end_date))
        daily_data = cursor.fetchall()
        
        # 每个科目的刷题数
        cursor.execute("""
            SELECT s.name, SUM(sr.count) as count
            FROM study_records sr
            JOIN subjects s ON sr.subject_id = s.id
            WHERE DATE(sr.record_date) BETWEEN ? AND ?
            GROUP BY s.name
            ORDER BY count DESC
        """, (start_date, end_date))
        subject_data = cursor.fetchall()
        
        # 打卡天数
        study_days = len(daily_data)
        
        # 计算平均每日刷题
        if report_type == 'week':
            total_days = 7
        elif report_type == 'month':
            total_days = now.day
        else:  # year
            total_days = (now - now.replace(month=1, day=1)).days + 1
        
        avg_daily = total_count / total_days if total_days > 0 else 0
        
        return {
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'total_count': total_count,
            'study_days': study_days,
            'total_days': total_days,
            'avg_daily': avg_daily,
            'daily_data': [dict(row) for row in daily_data],
            'subject_data': [dict(row) for row in subject_data]
        }
    
    def _call_ai_for_report(self, report_type, data):
        """调用AI生成报告"""
        from services.ai_service import AIService
        
        ai_service = AIService()
        
        # 构建提示词
        prompt = self._build_report_prompt(report_type, data)
        
        # 调用AI
        try:
            report = ai_service.call_ai_api(prompt=prompt)
            return report
        except Exception as e:
            print(f"[ERROR] AI报告生成失败: {e}")
            import traceback
            traceback.print_exc()
            return f"AI服务暂时不可用，请检查API配置。\n\n数据摘要：\n{self._generate_simple_report(data)}"
    
    def _build_report_prompt(self, report_type, data):
        """构建AI提示词"""
        title = data['title']
        total = data['total_count']
        study_days = data['study_days']
        total_days = data['total_days']
        avg = data['avg_daily']
        
        # 构建日期详情
        if data['daily_data']:
            daily_detail = "\n".join([
                f"  - {d['date']}: {d['count']}题"
                for d in data['daily_data'][-10:]  # 最近10天
            ])
        else:
            daily_detail = "  暂无刷题记录"
        
        # 构建科目详情
        if data['subject_data']:
            subject_detail = "\n".join([
                f"  - {s['name']}: {s['count']}题"
                for s in data['subject_data'][:5]  # 前5个科目
            ])
        else:
            subject_detail = "  暂无科目数据"
        
        prompt = f"""请直接生成一份{title}的学习报告，不要有任何推理过程和解释。

用户数据：
时间范围：{data['start_date']} ~ {data['end_date']}
总刷题数：{total}题
打卡天数：{study_days}/{total_days}天
日均刷题：{avg:.1f}题

每日详情：
{daily_detail}

科目分布：
{subject_detail}

请严格按照以下格式直接输出最终报告：

📊 数据回顾

（用3-4句话客观描述数据）

💬 小伙伴想对你说

（用温暖的语气像朋友一样鼓励用户，包括肯定亮点、温柔提醒、给出2-3条建议、鼓励结尾）

要求：
1. 语气温暖亲切，像知心朋友
2. 可适当使用emoji
3. 总字数300-400字
4. 直接输出报告内容，不要有"好的""明白了"等开场白
5. 不要输出推理过程"""
        return prompt
    
    def _generate_simple_report(self, data):
        """生成简单报告（AI不可用时的备用方案）"""
        # 计算打卡率
        attendance_rate = (data['study_days'] / data['total_days'] * 100) if data['total_days'] > 0 else 0
        
        # 鼓励语
        if attendance_rate >= 80:
            encouragement = "哇，打卡率超高！你真的很自律，继续保持这个节奏，一定会有很大收获的！💪"
        elif attendance_rate >= 50:
            encouragement = "打卡率还不错！再坚持一下，养成每天刷题的习惯，你会越来越强的！✨"
        else:
            encouragement = "咱们一起加油！每天坚持一点点，养成习惯就好了。别着急，慢慢来，相信自己！🌟"
        
        return f"""📊 数据回顾

{data['title']}你一共刷了{data['total_count']}题，打卡了{data['study_days']}天（打卡率{attendance_rate:.0f}%），平均每天{data['avg_daily']:.1f}题。

💬 小伙伴想对你说

{encouragement}

记得给自己定个小目标，比如每天至少刷20题，坚持下去就是胜利！我会一直陪着你的～😊"""
    
    def _show_report(self, loading_dialog, report_type, report_text):
        """显示报告"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDRaisedButton
        from kivymd.uix.scrollview import MDScrollView
        
        loading_dialog.dismiss()
        
        # 创建可滚动的内容
        scroll = MDScrollView(
            size_hint=(1, None),
            height=dp(450)
        )
        
        # 创建内容容器
        content_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(20),
            spacing=dp(10)
        )
        content_box.bind(minimum_height=content_box.setter('height'))
        
        # 使用MDLabel以获得更好的文字渲染和自动换行
        content = MDLabel(
            text=report_text,
            size_hint_y=None,
            font_size=dp(16),
            theme_text_color="Custom",
            text_color=(0.15, 0.15, 0.15, 1),
            markup=False
        )
        # 绑定高度到文字大小
        content.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        
        content_box.add_widget(content)
        scroll.add_widget(content_box)
        
        # 标题映射
        title_map = {
            'week': '📅 本周学习报告',
            'month': '📆 本月学习报告',
            'year': '📖 年度学习报告'
        }
        
        report_dialog = MDDialog(
            title=title_map[report_type],
            type="custom",
            content_cls=scroll,
            size_hint=(0.95, None),
            buttons=[
                MDRaisedButton(
                    text="好的，我会继续加油！",
                    md_bg_color=(0.2, 0.6, 0.9, 1),
                    on_release=lambda x: report_dialog.dismiss()
                )
            ]
        )
        report_dialog.open()
    
    def _show_error(self, loading_dialog, error_msg):
        """显示错误"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDRaisedButton
        
        loading_dialog.dismiss()
        
        # 友好的错误提示
        friendly_msg = "抱歉，AI小助手暂时走神了～"
        
        if "API" in error_msg or "配置" in error_msg:
            friendly_msg += "\n\n可能是还没配置AI服务，去设置页看看吧！"
        elif "网络" in error_msg:
            friendly_msg += "\n\n好像网络有点问题，稍后再试试？"
        else:
            friendly_msg += "\n\n遇到了一点小状况，稍后再试试吧～"
        
        error_dialog = MDDialog(
            title="😅 出了点小问题",
            text=friendly_msg,
            buttons=[
                MDRaisedButton(
                    text="好的",
                    md_bg_color=(0.3, 0.7, 0.4, 1),
                    on_release=lambda x: error_dialog.dismiss()
                )
            ]
        )
        error_dialog.open()
    
    def on_enter(self):
        """进入页面时刷新"""
        pass  # 数据已在构建时加载
    
    def open_full_calendar_dialog(self, *args):
        """打开完整日历弹窗"""
        from datetime import datetime, timedelta
        
        # 获取所有刷题记录
        conn = self.stats_service.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(record_date) as date, SUM(count) as count
            FROM study_records
            GROUP BY DATE(record_date)
            ORDER BY date DESC
        """)
        all_records = {row['date']: row['count'] for row in cursor.fetchall()}
        
        print(f"[DEBUG] 日历弹窗：找到 {len(all_records)} 天的记录")
        
        # 创建包装容器
        wrapper = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(500)
        )
        
        # 创建滚动视图
        scroll = MDScrollView()
        
        # 创建滚动内容  
        main_content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10)
        )
        main_content.bind(minimum_height=main_content.setter('height'))
        
        if not all_records:
            # 没有记录时的提示
            empty_label = MDLabel(
                text="还没有刷题记录哦~\n快去刷题吧！💪",
                font_style="H6",
                halign="center",
                size_hint_y=None,
                height=dp(100)
            )
            main_content.add_widget(empty_label)
        else:
            # 获取最早和最晚的记录日期
            earliest_date = min(all_records.keys())
            latest_date = max(all_records.keys())
            
            earliest = datetime.strptime(earliest_date, '%Y-%m-%d')
            latest = datetime.strptime(latest_date, '%Y-%m-%d')
            
            # 从最新月份到最早月份
            current = latest.replace(day=1)
            end = earliest.replace(day=1)
            
            while current >= end:
                # 创建每个月的日历卡片
                month_card = self.create_month_calendar_card(current, all_records)
                main_content.add_widget(month_card)
                
                # 移动到上个月
                if current.month == 1:
                    current = current.replace(year=current.year - 1, month=12)
                else:
                    current = current.replace(month=current.month - 1)
        
        # 组装视图
        scroll.add_widget(main_content)
        wrapper.add_widget(scroll)
        
        # 创建对话框
        self.calendar_dialog = MDDialog(
            title="📅 完整学习日历",
            type="custom",
            content_cls=wrapper,
            buttons=[
                MDRaisedButton(
                    text="关闭",
                    on_release=lambda x: self.calendar_dialog.dismiss()
                )
            ]
        )
        self.calendar_dialog.open()
    
    def create_month_calendar_card(self, month_date, all_records):
        """创建单个月份的日历卡片"""
        from datetime import datetime, timedelta
        import calendar
        
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(370),  # 增大卡片高度
            padding=dp(15),
            radius=[dp(15)]
        )
        
        # 月份标题
        year_month = month_date.strftime('%Y年%m月')
        
        # 计算这个月的统计
        month_str = month_date.strftime('%Y-%m')
        month_total = sum(count for date, count in all_records.items() if date.startswith(month_str))
        month_days = sum(1 for date in all_records.keys() if date.startswith(month_str))
        
        title_layout = BoxLayout(
            size_hint_y=None,
            height=dp(40)
        )
        
        title = MDLabel(
            text=f"{year_month}",
            font_style="H6",
            size_hint_x=0.5
        )
        title_layout.add_widget(title)
        
        stats = MDLabel(
            text=f"打卡{month_days}天  刷题{month_total}题",
            font_style="Caption",
            halign="right",
            theme_text_color="Secondary",
            size_hint_x=0.5
        )
        title_layout.add_widget(stats)
        
        card.add_widget(title_layout)
        
        # 星期标题
        weekday_layout = BoxLayout(
            size_hint_y=None,
            height=dp(25),
            spacing=dp(3)
        )
        
        for day in ['一', '二', '三', '四', '五', '六', '日']:
            weekday_label = MDLabel(
                text=day,
                font_style="Caption",
                halign="center",
                theme_text_color="Secondary"
            )
            weekday_layout.add_widget(weekday_label)
        
        card.add_widget(weekday_layout)
        
        # 日历网格（增大以容纳悬浮内容）
        calendar_grid = GridLayout(
            cols=7,
            spacing=dp(5),  # 增大间距
            size_hint_y=None,
            height=dp(240)  # 增大高度
        )
        
        # 获取这个月的天数和第一天是星期几
        year = month_date.year
        month = month_date.month
        first_weekday = calendar.monthrange(year, month)[0]  # 0=周一, 6=周日
        days_in_month = calendar.monthrange(year, month)[1]
        
        # 添加前面的空白
        for _ in range(first_weekday):
            calendar_grid.add_widget(BoxLayout())
        
        # 添加每一天
        for day in range(1, days_in_month + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            count = all_records.get(date_str, 0)
            
            # 确定状态和颜色
            level = 0 if count == 0 else (1 if count < 20 else 2)
            
            # 背景颜色
            bg_colors = [
                (0.95, 0.95, 0.95, 1),  # 未打卡 - 浅灰
                (0.70, 0.85, 1, 1),     # 打卡未完成 - 淡蓝
                (0.18, 0.45, 0.95, 1)   # 完成目标 - 深蓝
            ]
            
            # 根据背景色设置文字颜色
            if level == 0:  # 未打卡
                date_color = (0.3, 0.3, 0.3, 1)  # 深灰色日期
                count_color = (0.6, 0.6, 0.6, 1)  # 更浅的灰色题数
            elif level == 1:  # 打卡未完成
                date_color = (0.1, 0.3, 0.7, 1)  # 深蓝色日期
                count_color = (0.15, 0.35, 0.75, 1)  # 略浅的蓝色题数
            else:  # 完成目标
                date_color = (1, 1, 1, 1)  # 白色日期
                count_color = (0.85, 0.92, 1, 1)  # 略暗的淡白色题数
            
            # 创建可悬停的日期单元格
            day_box = HoverableDayBox(
                day=day,
                count=count,
                date_color=date_color,
                count_color=count_color,
                bg_color=bg_colors[level]
            )
            
            calendar_grid.add_widget(day_box)
        
        card.add_widget(calendar_grid)
        
        return card
