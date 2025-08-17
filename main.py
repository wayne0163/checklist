# main.py
from kivy.config import Config
Config.set('kivy', 'window_icon', '')
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard

import os, sqlite3, datetime, textwrap

# ============== 你的 12 条清单（题干 + 说明） ==============
QUESTIONS = [
    {
        "q": "1.大盘环境是否有利于本次操作？",
        "hint": "大盘是震荡/上涨/下跌？是否存在系统性风险或极端走势；宏观政策是否支持？"
    },
    {
        "q": "2.近期是否存在干扰操作的重大事件？",
        "hint": "未来半个月内是否有财报/政策/股东大会/解禁/地缘风险等影响波动的事件？"
    },
    {
        "q": "3.所属行业处于强势还是弱势？",
        "hint": "板块资金流向如何？所处位置（历史低/高位）与景气度如何？是否有明确驱动？"
    },
    {
        "q": "4.技术结构与期望盈亏比是否支持本次操作？",
        "hint": "位置（低/高位）、形态（启动/加速/平台/破位）是否与方向一致；盈亏比是否>=2.5:1？"
    },
    {
        "q": "5.成交量与资金流向是否验证趋势？",
        "hint": "近期是否出现放量上涨/下跌、量价背离或主力资金明显进出迹象？"
    },
    {
        "q": "6.是否完成了个股基本面确认？",
        "hint": "是否查阅最近一期财报、核心公告或研究摘要；是否排除明显雷点？"
    },
    {
        "q": "7.是否明确了操作级别与持仓计划？",
        "hint": "本操作属于试探性加减仓，还是做T，有无思考过可能做错方向？"
    },
    {
        "q": "8.交易周期是否匹配你的策略边界？",
        "hint": "标的波动与节奏是否适合中短期（7–120天）确定你不是想长做短或者想短做长。"
    },
    {
        "q": "9.仓位与持仓结构是否合理？",
        "hint": "执行后单票是否过重；整体维持4–8只；行业/个股相关性是否过高？"
    },
    {
        "q": "10.退出标准与执行细节是否清晰？",
        "hint": "是否写下止盈/止损/时间止损；下单方式（限价/市价）、节奏（一次性/分批）明确？"
    },
    {
        "q": "11.是否已做好执行计划？",
        "hint": "本次决策及执行是一次性操作还是分批进行，操作时间是否可以推迟到收盘前或者明天开盘？"
    },
    {
        "q": "12.当前情绪与外部噪音是否不会干扰执行？",
        "hint": "确定你不是被短期消息、群体情绪、他人观点影响才要计划本次执行并复盘。"
    },
]

DB_NAME = "checklist.db"

def md_escape(text: str) -> str:
    return (text or "").replace("\r", "").strip()

class DB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entries(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                date TEXT,
                stock_name TEXT,
                stock_code TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS answers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER,
                q_no INTEGER,
                result TEXT,      -- 'Y'/'N'/'NA'
                note TEXT,
                FOREIGN KEY(entry_id) REFERENCES entries(id)
            )
        """)
        self.conn.commit()

    def new_entry(self, title, date, stock_name, stock_code):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO entries(title, date, stock_name, stock_code) VALUES(?,?,?,?)",
                    (title, date, stock_name, stock_code))
        self.conn.commit()
        return cur.lastrowid

    def save_answer(self, entry_id, q_no, result, note):
        # upsert by entry_id + q_no
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM answers WHERE entry_id=? AND q_no=?", (entry_id, q_no))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE answers SET result=?, note=? WHERE id=?",
                        (result, note, row[0]))
        else:
            cur.execute("INSERT INTO answers(entry_id, q_no, result, note) VALUES(?,?,?,?)",
                        (entry_id, q_no, result, note))
        self.conn.commit()

    def load_entry(self, entry_id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, date, stock_name, stock_code FROM entries WHERE id=?", (entry_id,))
        entry = cur.fetchone()
        cur.execute("SELECT q_no, result, note FROM answers WHERE entry_id=? ORDER BY q_no", (entry_id,))
        answers = cur.fetchall()
        return entry, answers

class StartScreen(Screen):
    def on_pre_enter(self, *a):
        self.ids.name.text = ""
        self.ids.code.text = ""
        self.ids.date.text = datetime.date.today().isoformat()
        self.ids.title_lbl.text = "标题将自动生成"

    def gen_title(self, *a):
        stock_name = self.ids.name.text.strip()
        stock_code = self.ids.code.text.strip()
        date = self.ids.date.text.strip() or datetime.date.today().isoformat()
        if not stock_name or not stock_code:
            self.dialog("请先填写股票名称与代码")
            return
        title = f"{date}_{stock_name}_{stock_code}"
        self.ids.title_lbl.text = title

    def next(self, *a):
        stock_name = self.ids.name.text.strip()
        stock_code = self.ids.code.text.strip()
        date = self.ids.date.text.strip() or datetime.date.today().isoformat()
        if not stock_name or not stock_code:
            self.dialog("请先填写股票名称与代码")
            return
        title = f"{date}_{stock_name}_{stock_code}"
        app = MDApp.get_running_app()
        app.entry_id = app.db.new_entry(title, date, stock_name, stock_code)
        app.title_cache = title
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "q"

    def dialog(self, msg):
        MDDialog(title="提示", text=msg, buttons=[MDFlatButton(text="好", on_release=lambda *_: self.dismiss_dialog())]).open()
    def dismiss_dialog(self, *a):
        for w in MDApp.get_running_app().root_window.children:
            pass  # 简化：MDDialog会自动关闭

class QuestionScreen(Screen):
    def on_pre_enter(self, *a):
        app = MDApp.get_running_app()
        if not hasattr(app, "q_index"):
            app.q_index = 0
            app.answers = {}  # q_index -> {"result":"Y/N/NA", "note":""}
        self.render()

    def render(self):
        app = MDApp.get_running_app()
        i = app.q_index
        data = QUESTIONS[i]
        self.ids.card.clear_widgets()

        card = MDCard(orientation="vertical", padding=dp(12), spacing=dp(8))
        card.add_widget(MDLabel(text=f"{i+1}. {data['q']}", bold=True, font_style="H6"))
        card.add_widget(MDLabel(text=data['hint'], theme_text_color="Secondary"))
        seg = MDSegmentedControl()
        for lab, val in [("符合", "Y"), ("不符合", "N"), ("跳过", "NA")]:
            item = MDSegmentedControlItem(text=lab, on_release=lambda inst, val=val: self.on_seg(val))
            seg.add_widget(item)
        card.add_widget(seg)
        note = MDTextField(
            hint_text="备注（可选）",
            multiline=True,
            size_hint_y=None,
            height=dp(120),
            mode="fill",
        )
        self.note_widget = note
        # 回显
        old = app.answers.get(i, {})
        if old:
            # 选择回显简化：不恢复 segmented 的选中，仅恢复备注
            note.text = old.get("note", "")
        self.ids.card.add_widget(card)
        self.ids.card.add_widget(note)
        self.ids.progress.text = f"{i+1}/{len(QUESTIONS)}"

    def on_seg(self, val):
        self.selected = val

    def save_current(self):
        app = MDApp.get_running_app()
        i = app.q_index
        result = getattr(self, "selected", "NA")
        note = self.note_widget.text if hasattr(self, "note_widget") else ""
        app.answers[i] = {"result": result, "note": note}
        # 保存到数据库
        app.db.save_answer(app.entry_id, i, result, note)

    def prev(self):
        app = MDApp.get_running_app()
        if app.q_index == 0:
            return
        self.save_current()
        app.q_index -= 1
        self.render()

    def next(self):
        app = MDApp.get_running_app()
        self.save_current()
        if app.q_index < len(QUESTIONS) - 1:
            app.q_index += 1
            self.render()
        else:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "review"

class ReviewScreen(Screen):
    def on_pre_enter(self, *a):
        app = MDApp.get_running_app()
        self.ids.summary.clear_widgets()
        title = getattr(app, "title_cache", "未命名")
        self.ids.title_lbl.text = title

        # 加一个简要统计
        y = sum(1 for v in app.answers.values() if v.get("result") == "Y")
        n = sum(1 for v in app.answers.values() if v.get("result") == "N")
        na = len(QUESTIONS) - y - n
        self.ids.summary.add_widget(MDLabel(text=f"符合: {y}，不符合: {n}，跳过: {na}"))

    def export_md(self):
        app = MDApp.get_running_app()
        entry, answers = app.db.load_entry(app.entry_id)
        # entry: (id, title, date, name, code)
        if not entry:
            self.dialog("未找到记录")
            return
        _, title, date, stock_name, stock_code = entry

        lines = [f"# 📋 中短期股票交易执行前清单（单次记录）",
                 f"- **标题**：{md_escape(title)}",
                 f"- **日期**：{md_escape(date)}",
                 f"- **标的**：{md_escape(stock_name)}（{md_escape(stock_code)}）",
                 ""]

        for i, q in enumerate(QUESTIONS):
            # 找答案
            rec = next((r for r in answers if r[0] == i), None)
            res = rec[1] if rec else "NA"
            note = rec[2] if rec else ""
            check = "x" if res == "Y" else " "  # 仅把“符合”当作勾选
            lines.append(f"- [${check}] **{i+1}. {q['q']}**")
            lines.append(f"  说明：{q['hint']}")
            if note:
                lines.append(f"  备注：{md_escape(note)}")
            else:
                lines.append(f"  备注：")
            lines.append("")

        content = "\n".join(lines)

        # 写入到 App 私有目录（然后用系统“分享”导出）
        base = App.get_running_app().user_data_dir
        os.makedirs(os.path.join(base, "exports"), exist_ok=True)
        filename = f"{title}.md".replace("/", "_")
        path = os.path.join(base, "exports", filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        # 调系统分享（Android 上会弹出分享面板，用户可保存到下载/发送给其他 App）
        try:
            from plyer import share
            share.share(title="导出清单", message=title, filepath=path)
        except Exception:
            self.dialog(f"已导出到：\n{path}\n（如在 Android 上未弹出分享面板，可手动拷出该文件）")

    def dialog(self, msg):
        MDDialog(title="提示", text=msg, buttons=[MDFlatButton(text="好", on_release=lambda *_: None)]).open()

class Root(MDBoxLayout):
    pass

class ChecklistApp(MDApp):
    def build(self):
        self.title = "交易前清单"
        Window.softinput_mode = "below_target"
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.db = DB(os.path.join(self.user_data_dir, DB_NAME))

        sm = ScreenManager()
        start = StartScreen(name="start")
        q = QuestionScreen(name="q")
        rev = ReviewScreen(name="review")

        # 组装界面
        start_layout = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        start_layout.add_widget(MDLabel(text="填写基本信息", bold=True, font_style="H5"))
        name = MDTextField(hint_text="股票名称（必填）", id="name", mode="fill")
        code = MDTextField(hint_text="股票代码（必填）", id="code", mode="fill")
        date = MDTextField(hint_text="日期（默认今日）", id="date", mode="fill")
        title_lbl = MDLabel(text="标题将自动生成", id="title_lbl", theme_text_color="Secondary")
        btn_row = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(48))
        gen_btn = MDRectangleFlatButton(text="生成标题", on_release=start.gen_title)
        next_btn = MDRaisedButton(text="开始", on_release=start.next)
        btn_row.add_widget(gen_btn); btn_row.add_widget(next_btn)
        start_layout.add_widget(name); start_layout.add_widget(code); start_layout.add_widget(date)
        start_layout.add_widget(title_lbl); start_layout.add_widget(btn_row)
        start.add_widget(start_layout)

        q_layout = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        progress = MDLabel(text="1/12", id="progress", theme_text_color="Secondary")
        q_layout.add_widget(progress)
        scroll = ScrollView()
        card_box = MDBoxLayout(orientation="vertical", id="card", padding=dp(0), size_hint_y=None)
        card_box.bind(minimum_height=card_box.setter('height'))
        scroll.add_widget(card_box)
        q_layout.add_widget(scroll)
        nav = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(48))
        prev_btn = MDRectangleFlatButton(text="上一题", on_release=lambda *_: q.prev())
        next_btn2 = MDRaisedButton(text="下一题", on_release=lambda *_: q.next())
        nav.add_widget(prev_btn); nav.add_widget(next_btn2)
        q_layout.add_widget(nav)
        q.add_widget(q_layout)

        rev_layout = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        rev_layout.add_widget(MDLabel(text="完成与导出", font_style="H5", bold=True))
        rev_layout.add_widget(MDLabel(text="条目：", id="title_lbl", theme_text_color="Secondary"))
        rev_layout.add_widget(MDLabel(text="概要", theme_text_color="Secondary"))
        rev_layout.add_widget(MDBoxLayout(id="summary"))
        actions = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(48))
        export_btn = MDRaisedButton(text="导出为 Markdown", on_release=lambda *_: rev.export_md())
        actions.add_widget(export_btn)
        rev_layout.add_widget(actions)
        rev.add_widget(rev_layout)

        sm.add_widget(start); sm.add_widget(q); sm.add_widget(rev)
        return sm

if __name__ == "__main__":
    ChecklistApp().run()
