import tkinter as tk
from tkinter.messagebox import showinfo
from tkinter.font import Font
from tkinter.ttk import Combobox, Progressbar
from string import hexdigits
import seedFinder
from webbrowser import open_new_tab
from random import randrange

__version__ = 1.0
__max_seed__ = 0x7FFFFFFF

zombie_names = ['普僵', '', '路障', '撑杆', '铁桶', '读报', '铁门', '橄榄', '舞王', '', '', '潜水',
                '冰车', '', '海豚', '小丑', '气球', '矿工', '跳跳', '', '蹦极', '扶梯', '投篮', '白眼', '', '', '', '', '', '', '', '', '红眼']
# 展示出怪的顺序
show_list_de = [2, 3, 4, 5, 6, 8,
                17, 18, 20, 21, 22, 7, 12, 15, 16, 23, 32]
show_list_ne = [2, 3, 4, 5, 6, 8,
                17, 18, 20, 21, 22, 7, 15, 16, 23, 32]
show_list_pe = [2, 3, 4, 5, 6, 8, 11, 14,
                17, 18, 20, 21, 22, 7, 12, 15, 16, 23, 32]
show_list_re = [2, 3, 4, 5, 6,
                18, 20, 21, 22, 7, 12, 15, 16, 23, 32]
# 计算出怪函数


def calc_appear(uid, mode, scene, level, seed):

    new_scene = 'DAY'
    if scene == 'NE':
        new_scene = 'NIGHT'
    elif scene == 'PE/FE':
        new_scene = 'POOL'
    elif scene == 'RE/ME':
        new_scene = 'ROOF'
    return seedFinder.appear(uid, mode, new_scene, level, seed)


class App(tk.Tk):
    # 主要初始化函数
    def __init__(self):
        super().__init__()
        self.details_window = self.about_window = self.help_window = self.setting_window = self.headers = None
        self.zombie_details = []
        self.seed_span = 1000   # 每次寻找种子总数
        self.seed_start_choice = 2  # 从哪个种子开始找，1代表随机，2代表固定值
        self.seed_start = 0     # 默认从0开始
        self.details_scene = ''  # 上一次详情页的场景（如果不同，关闭后重新渲染）
        self.create_window(f'种子寻找器 v{__version__}', 560, 360, False)
        self.init_fonts()
        self.init_menu()
        self.create_widgets()

    # 创建一个窗口（主窗口和子窗口通用）
    def create_window(self, title, width, height, is_child):
        if is_child:
            child_window = tk.Toplevel(self)
        else:
            child_window = self
        child_window.title(title)
        window_width, window_height = width, height
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        center_x, center_y = int(
            screen_width//2 - window_width // 2), int(screen_height//2 - window_height // 2)
        child_window.geometry(
            f'{window_width}x{window_height}+{center_x}+{center_y}')  # 默认居中显示
        child_window.resizable(False, False)
        child_window.iconbitmap(default='favicon.ico')
        child_window.focus_set()
        return child_window

    # 初始化字体
    def init_fonts(self):
        self.fontStyle = Font(family="微软雅黑", size=12)
        self.fontStyle2 = Font(family="微软雅黑", size=11)
        self.fontStyle3 = Font(family="微软雅黑", size=10)
        self.fontStyle4 = Font(family="微软雅黑", size=8)

    # 初始化菜单
    def init_menu(self):
        self.main_menu = tk.Menu(self)
        self.help_menu = tk.Menu(self.main_menu, tearoff=0)

        self.settings_menu = tk.Menu(self.main_menu, tearoff=0)
        self.settings_menu.add_command(
            label="详细设置", command=self.create_settings_window)
        self.main_menu.add_cascade(label="设置", menu=self.settings_menu)
        self.help_menu.add_command(
            label="使用说明", command=self.create_help_window)
        self.help_menu.add_command(
            label="关于...", command=self.create_about_window)
        self.main_menu.add_cascade(
            label="帮助", menu=self.help_menu)
        self.config(menu=self.main_menu)

    # 获得种子输入框里的种子
    def get_valid_seed(self):
        seed = self.combobox2.get()
        try:
            s = int(seed, 16)
            if s > __max_seed__:
                self.combobox2.focus()
                showinfo('输入有误', f"种子超过了本程序可接受的上限 (0x{__max_seed__:x})")
                return None
            return s
        except:
            self.combobox2.focus()
            showinfo("输入有误", "种子必须是16进制数 (由0~9, A~F组成, 不区分大小写)")
            return None

    # 获得表头
    def get_header(self, show_list):
        headers = ['已完成f数']
        for idx in show_list:
            headers.append(zombie_names[idx])
        return tuple(headers)

    # 更新表格内容（不包括表头）
    def update_table(self, giga_count, total_count):
        self.table.delete(*self.table.get_children())

        # 更新数据
        for _, row in enumerate(self.zombie_details, start=1):
            values = [row[0]]
            for x in range(1, len(row)):
                values.append("○" if row[x] else "")
            self.table.insert(
                "", "end", values=tuple(values))
        self.table_info_str.set(f'共 {total_count} 次选卡, {giga_count} 个红眼关')

    # 创建出怪详情窗口
    def create_details_window(self, only_update_existing_window=False):
        if only_update_existing_window and (self.details_window is None or not self.details_window.winfo_exists()):
            return
        # 先检查输入
        inputs = self.get_inputs()
        if inputs is None:
            return
        seed = self.get_valid_seed()
        if seed is None:
            return
        
        # 计算
        uid, mode, start, span = inputs[0], inputs[1], inputs[2], inputs[3]
        scene = self.scene.get()
        self.zombie_details = []
        total_count = giga_count = 0
        show_list = show_list_de
        if scene == 'NE':
            show_list = show_list_ne
        elif scene == 'PE/FE':
            show_list = show_list_pe
        elif scene == 'RE/ME':
            show_list = show_list_re
        for level in range(int(start) // 2, start // 2 + span):
            havez = calc_appear(uid, mode, scene, level, seed)
            total_count += 1
            if havez[32]:
                giga_count += 1
            new_list = []
            for idx in show_list:
                new_list.append(havez[idx])
            self.zombie_details.append([level*2] + new_list)

        if self.details_window is not None and self.details_window.winfo_exists():
            if scene == self.details_scene:
                self.details_window.deiconify()
                self.details_window.focus_set()
                self.update_table(giga_count, total_count)
                return
            else:
                self.details_window.destroy()

        # 初始化组件
        headers = self.get_header(show_list)
        self.details_scene = scene
        window_width = len(headers)*38+40
        self.details_window = self.create_window(
            '出怪详情', window_width, 410, True)
        self.page = tk.Frame(self.details_window)
        self.page.place(anchor=tk.N, x=window_width // 2, y=20)
        self.table_info_str = tk.StringVar()
        self.table_info = tk.Label(
            self.page, textvariable=self.table_info_str, justify='center', font=self.fontStyle3).grid(row=0, columnspan=len(headers) + 1)
        self.table = tk.ttk.Treeview(
            self.page, height=15, columns=headers, show='headings')
        self.VScroll = tk.ttk.Scrollbar(
            self.page, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=self.VScroll.set)
        self.VScroll.grid(row=1, column=len(headers) + 1, sticky=tk.NS)

        # 设置列宽
        first = True
        for col in headers:
            if first:
                width = 60
                first = False
            else:
                width = 35
            self.table.column(
                col, width=width, anchor='center')
            self.table.heading(col, text=col)
        self.table.grid(row=1, column=0, columnspan=len(headers), sticky=tk.NW)
        self.update_table(giga_count, total_count)

        # 禁止调整列宽
        def handle_click(event):
            if self.table.identify_region(event.x, event.y) == "separator":
                return "break"

        self.table.bind('<Button-1>', handle_click)

    # 创建关于窗口
    def create_about_window(self):
        if self.about_window is not None and self.about_window.winfo_exists():
            self.about_window.deiconify()
            self.about_window.focus_set()
            return

        # tk没有文本框+超链接支持，只好手动拼接
        self.about_window = self.create_window(
            '关于种子寻找器', 420, 250, True)
        label1 = tk.Label(self.about_window,
                          text=f"植物大战僵尸生存无尽模式种子寻找器 v{__version__}\n\n源码:\n\n作者: \n\n开发工具: Python 3.8.0, Tkinter 8.6, PyInstaller 5.3, \n\n\n鸣谢:", justify='left', font=self.fontStyle3)
        label1.place(x=20, y=20)
        label2 = tk.Label(self.about_window, text="https://github.com/Rottenham/seed-finder",
                          fg="blue", cursor="hand2", justify='left', font=self.fontStyle3)
        label2.bind("<Button-1>", lambda e:
                    open_new_tab("https://github.com/Rottenham/seed-finder"))
        label2.place(x=79, y=58)
        label3 = tk.Label(self.about_window, text="Crescendo", fg="blue",
                          cursor="hand2", justify='left', font=self.fontStyle3)
        label3.bind("<Button-1>", lambda e:
                    open_new_tab("https://space.bilibili.com/8252252"))
        label3.place(x=79, y=96)
        label4 = tk.Label(self.about_window, text="Kndy666/zombie_calculator", fg="blue",
                          cursor="hand2", justify='left', font=self.fontStyle3)
        label4.bind("<Button-1>", lambda e:
                    open_new_tab("https://github.com/Kndy666/zombie_calculator"))
        label4.place(x=79, y=192)
        label5 = tk.Label(self.about_window,
                          text="Enigma Virtual Box 9.90", font=self.fontStyle3)
        label5.place(x=79, y=156)

    # 创建帮助窗口
    def create_help_window(self):
        if self.help_window is not None and self.help_window.winfo_exists():
            self.help_window.deiconify()
            self.help_window.focus_set()
            return
        self.help_window = self.create_window('帮助', 420, 250, True)
        label1 = tk.Label(self.help_window,
                          text="使用方法:\n\n1. 填写想要冲关的 flags 范围, 以及其它必要信息\n\n2. 指定难度系数, 0% 代表最简单(红眼关最少), 100% 代表最困难\n    (红眼关最多)\n\n3. 点击 [计算] , 得到结果; 点击 [查看详情] 查看该种子的出怪详情\n\n4. 每次计算时, 程序会提供多个符合条件的类似种子; 玩家也可以\n    自行输入种子并查看详情",
                          font=self.fontStyle3, justify='left')
        label1.place(x=20, y=15)

    # 关掉设置窗口
    def close_settings_window(self):
        self.setting_window.destroy()

    # 提交设置
    def submit_settings(self):
        seed_span_input = self.seed_span_entry.get()
        if len(seed_span_input) == 0:
            showinfo("输入有误", "遍历种子总数为空")
            self.setting_window.focus_set()
            self.seed_span_entry.focus()
            return
        seed_span_input = int(seed_span_input)
        if seed_span_input == 0:
            showinfo("输入有误", "遍历种子总数不可为0")
            self.setting_window.focus_set()
            self.seed_span_entry.focus()
            return
        choice_input = self.seed_start_choice_intvar.get()
        if choice_input == 2:
            seed_start_input = self.fixed_seed_start_entry.get()
            if len(seed_start_input) == 0:
                showinfo("输入有误", "种子起始值为空")
                self.setting_window.focus_set()
                self.fixed_seed_start_entry.focus()
                return
            seed_start_input = int(seed_start_input, 16)
            if seed_span_input + seed_start_input > __max_seed__:
                showinfo(
                    "输入有误", f"起始值加上遍历范围后超过了本程序可接受的种子上限 (0x{__max_seed__:x})")
                self.setting_window.focus_set()
                self.seed_span_entry.focus()
                return
            self.seed_start_choice = choice_input
            self.seed_start = seed_start_input
        else:
            self.seed_start_choice = choice_input
        self.seed_span = seed_span_input
        self.setting_window.destroy()

    # 创建设定窗口
    def create_settings_window(self):
        if self.setting_window is not None and self.setting_window.winfo_exists():
            self.setting_window.deiconify()
            self.setting_window.focus_set()
            return
        self.setting_window = self.create_window('详细设置', 420, 250, True)

        label1 = tk.Label(self.setting_window,
                          text="每次遍历的种子总数:", font=self.fontStyle2)
        label1.place(x=20, y=20)

        self.seed_span_entry = tk.Entry(self.setting_window,
                                        font=self.fontStyle2, width=12, validate='key',
                                        validatecommand=self.get_validate_command(10))
        self.seed_span_entry.insert(tk.INSERT, str(self.seed_span))
        self.seed_span_entry.place(x=210, y=20)

        label2 = tk.Label(self.setting_window,
                          text="从哪个种子开始遍历:", font=self.fontStyle2)
        label2.place(x=20, y=75)

        self.seed_start_choice_intvar = tk.IntVar()
        rb1 = tk.Radiobutton(self.setting_window, text="随机",
                             variable=self.seed_start_choice_intvar, value=1, font=self.fontStyle2)
        rb1.place(x=205,  y=75)
        rb2 = tk.Radiobutton(self.setting_window, text='从固定值开始',
                             variable=self.seed_start_choice_intvar, value=2, font=self.fontStyle2)
        rb2.place(x=205, y=110)
        self.seed_start_choice_intvar.set(self.seed_start_choice)

        self.fixed_seed_start_entry = tk.Entry(self.setting_window,
                                               font=self.fontStyle2, width=12, validate='key',
                                               validatecommand=(self.register(self.check_hex), '%P'), justify='right')
        self.fixed_seed_start_entry.insert(
            tk.INSERT, str(self.get_hex(self.seed_start)))
        self.fixed_seed_start_entry.place(x=230, y=147)

        button1 = tk.Button(
            self.setting_window, text="确定", font=self.fontStyle2, command=self.submit_settings)
        button1.config(height=1, width=7)
        button1.place(x=77, y=200)

        button2 = tk.Button(
            self.setting_window, text="取消", font=self.fontStyle2, command=self.close_settings_window)
        button2.config(height=1, width=7)
        button2.place(x=267, y=200)

    # 主界面的所有组件
    def create_widgets(self):
        # 第一行
        self.label1 = tk.Label(self, text="game", font=self.fontStyle)
        self.label1.place(x=20, y=20)

        self.entry1 = tk.Entry(self, width=3, font=self.fontStyle)
        self.entry1.place(x=75, y=20)
        self.entry1.insert(tk.INSERT, '1')
        self.entry1.config(validate='key',
                           validatecommand=self.get_validate_command(2))

        self.label2 = tk.Label(self, text="_", font=self.fontStyle)
        self.label2.place(x=110, y=20)

        self.entry2 = tk.Entry(self, width=3, font=self.fontStyle)
        self.entry2.place(x=125, y=20)
        self.entry2.insert(tk.INSERT, '13')
        self.entry2.config(validate='key',
                           validatecommand=self.get_validate_command(2))

        self.scene = tk.StringVar(self)
        self.combobox = Combobox(
            self, textvariable=self.scene, value=('DE', 'NE', 'PE/FE', 'RE/ME'), state='readonly', font=self.fontStyle2, width=7)
        self.combobox.place(x=180, y=20)
        self.combobox.current(2)
        self.option_add("*TCombobox*Listbox*Font", self.fontStyle2)

        self.label3 = tk.Label(self, text="起始f数:", font=self.fontStyle)
        self.label3.place(x=285, y=20)

        self.entry3 = tk.Entry(
            self, width=5, font=self.fontStyle, justify='right')
        self.entry3.place(x=360, y=20)
        self.start_flags = tk.StringVar()
        self.entry3.config(validate='key', textvariable=self.start_flags,
                           validatecommand=self.get_validate_command(5, True))
        self.entry3.insert(tk.INSERT, '2022')

        self.label4 = tk.Label(
            self, text="flags completed", font=self.fontStyle)
        self.label4.place(x=415, y=20)

        # 第二行
        self.label5 = tk.Label(self, text="计算跨度:", font=self.fontStyle)
        self.label5.place(x=20, y=70)

        self.entry4 = tk.Entry(self, width=3, font=self.fontStyle)
        self.entry4.place(x=102, y=70)
        self.flags_span = tk.StringVar()
        self.entry4.config(validate='key', textvariable=self.flags_span,
                           validatecommand=self.get_validate_command(2))
        self.entry4.insert(tk.INSERT, '25')

        self.label6 = tk.Label(self, text="次选卡", font=self.fontStyle)
        self.label6.place(x=137, y=70)

        self.label7 = tk.Label(self, text="终止f数:", font=self.fontStyle)
        self.label7.place(x=285, y=70)

        self.label8 = tk.Label(
            self, text="2272", font=self.fontStyle)
        self.label8.place(anchor=tk.NE, x=410, y=70)
        self.start_flags.trace('w', self.update_final_flags)
        self.flags_span.trace('w', self.update_final_flags)

        self.label9 = tk.Label(
            self, text="flags completed", font=self.fontStyle)
        self.label9.place(x=415, y=70)

        # 第三行
        self.label10 = tk.Label(
            self, text="难度系数:", font=self.fontStyle)
        self.label10.place(x=20, y=135)

        self.slider1 = tk.Scale(self, from_=0, to=100,
                                length=400, tickinterval=20, orient=tk.HORIZONTAL)
        self.slider1.set(70)
        self.slider1.place(x=120, y=117)

        tk.Label(self, text="红眼关最少", font=self.fontStyle4).place(x=109, y=174)
        tk.Label(self, text="红眼关最多", font=self.fontStyle4).place(x=477, y=174)

        # 第四行
        self.button1 = tk.Button(
            self, text="计算", font=self.fontStyle, command=self.submit)
        self.button1.config(height=1, width=7)
        self.button1.place(x=75, y=220)

        self.label11 = tk.Label(
            self, text="出怪种子", font=self.fontStyle3)
        self.label11.place(x=250, y=195)

        self.combobox2 = Combobox(
            self, font=self.fontStyle2, width=8, validate='key', validatecommand=(self.register(self.check_hex), '%P'), justify='right')
        self.combobox2.place(x=232, y=226)

        self.button2 = tk.Button(
            self, text="复制", font=self.fontStyle3, command=self.copy_to_clipboard)
        self.button2.config(height=1, width=4)
        self.button2.place(x=229, y=260)

        self.button3 = tk.Button(
            self, text="清除", font=self.fontStyle3, command=self.clear_calc_result)
        self.button3.config(height=1, width=4)
        self.button3.place(x=284, y=260)

        self.button4 = tk.Button(
            self, text="查看详情", font=self.fontStyle, command=self.create_details_window)
        self.button4.config(height=1, width=8)
        self.button4.place(x=399, y=220)

        # 第五行
        self.progress_bar = Progressbar(
            self, orient='horizontal', length=520, mode='determinate')
        self.progress_bar.place(x=20, y=307)
        self.progress = 0

    # 检测所有字符是否属于某个数字集里（10/16进制通用）
    def check_all_digit(self, value, max_digit):
        return len(value) <= int(max_digit) and all(c.isdigit() for c in value)

    # 验证是否为合理的16进制数
    def check_hex(self, value):
        return len(value) <= 8 and all(c in hexdigits for c in value)

    # 验证是否全部为数字
    def validate(self, value, max_num, allow_zero):
        if len(value) == 0:
            return True
        if not self.check_all_digit(value, max_num):
            return False
        if not allow_zero and value[0] == '0':
            return False
        return True

    # 返回常见的数字验证命令
    def get_validate_command(self, max_num, allow_zero=False):
        return (self.register(self.validate), '%P', max_num, allow_zero)

    # 根据起始f数、计算跨度，更新最终f数
    def update_final_flags(self, *args):
        start = self.start_flags.get()
        span = self.flags_span.get()
        if len(start) == 0:
            start = '0'
        if len(span) == 0:
            span = '0'
        final = int(start) + int(span) * 2
        self.label8.config(text='')
        self.label8.config(text=str(final))

    # 复制到剪切板
    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.combobox2.get().rstrip())

    # 清除种子输入框、进度条归零
    def clear_calc_result(self):
        self.combobox2.set('')
        self.update_progress_if_necessary(0)

    # 检查计算输入是否都合法
    def get_inputs(self):
        uid = self.entry1.get()
        if len(uid) == 0:
            self.entry1.focus()
            showinfo("输入有误", "用户序号为空")
            return None
        mode = self.entry2.get()
        if len(mode) == 0:
            self.entry2.focus()
            showinfo("输入有误", "游戏模式为空")
            return None
        start = self.entry3.get()
        if len(start) == 0:
            self.entry3.focus()
            showinfo("输入有误", "起始f数为空")
            return None
        if int(start) % 2 != 0:
            self.entry3.focus()
            showinfo("输入有误", "起始f数应当为偶数")
            return None
        span = self.entry4.get()
        if len(span) == 0:
            self.entry4.focus()
            showinfo("输入有误", "计算跨度为空")
            return None
        return (int(uid), int(mode), int(start), int(span))

    # 提交至计算
    def submit(self):
        inputs = self.get_inputs()
        if inputs is None:
            return
        uid, mode, start, span = inputs[0], inputs[1], inputs[2], inputs[3]
        scene = self.scene.get()
        hardness = int(self.slider1.get())
        self.calculate(uid, mode, scene,
                       start, span, hardness)

    # 更新进度条
    def update_progress_if_necessary(self, new_val):
        if new_val < 0:
            new_val = 0
        if new_val > 100:
            new_val = 100
        if self.progress != new_val:
            self.progress = new_val
            self.progress_bar['value'] = new_val
            self.update()   # 防止程序无响应

    # 获得百分比段
    def get_percentile(self, input_size, output_size, percentile):
        if input_size <= output_size:
            return 0, input_size
        start = int(input_size * percentile / 100)
        if start + output_size > input_size:
            return input_size - output_size, input_size
        return start, start + output_size

    # 开启/禁用所有输入框
    def toggle_all_entries(self, enable):
        if enable:
            self.entry1['state'] = 'normal'
            self.entry2['state'] = 'normal'
            self.entry3['state'] = 'normal'
            self.entry4['state'] = 'normal'
            self.combobox['state'] = 'normal'
            self.combobox2['state'] = 'normal'
            self.slider1['state'] = 'normal'
            self.button1['state'] = 'normal'
            self.button2['state'] = 'normal'
            self.button3['state'] = 'normal'
            self.button4['state'] = 'normal'
            self.button1['text'] = '计算'
        else:
            self.entry1['state'] = 'disabled'
            self.entry2['state'] = 'disabled'
            self.entry3['state'] = 'disabled'
            self.entry4['state'] = 'disabled'
            self.combobox['state'] = 'disabled'
            self.combobox2['state'] = 'disabled'
            self.slider1['state'] = 'disabled'
            self.button1['state'] = 'disabled'
            self.button2['state'] = 'disabled'
            self.button3['state'] = 'disabled'
            self.button4['state'] = 'disabled'
            self.button1['text'] = '计算中...'

    # 获得某int的hex表示（填充至8位）
    def get_hex(self, num):
        return f'{num:x}'.zfill(8)

    # 计算主函数
    # 遍历一段种子范围，根据设定的难度系数返回符合条件的种子
    def calculate(self, uid, mode, scene, start, span, hardness, output_size=5):
        self.update_progress_if_necessary(0)
        seed_start = self.seed_start
        if self.seed_start_choice == 1:  # 随机开始模式
            seed_start = randrange(__max_seed__ - self.seed_span + 1)
        seed_end = seed_start + self.seed_span
        finished, total = 0, self.seed_span
        result = []
        self.toggle_all_entries(False)
        for seed in range(seed_start, seed_end):
            giga_count = 0
            for level in range(start // 2, start // 2 + span):
                havez = calc_appear(uid, mode, scene, level, seed)
                if havez[32]:
                    giga_count += 1
            result.append((giga_count, seed))
            finished += 1
            temp = int(100 * finished / total)
            self.update_progress_if_necessary(temp)
        result = sorted(result)
        start, end = self.get_percentile(len(result), output_size, hardness)
        seed_list = [self.get_hex(x[1]) for x in result[start:end]]
        self.combobox2['values'] = tuple(seed_list)
        self.combobox2.current(0)
        self.toggle_all_entries(True)
        self.create_details_window(True)


if __name__ == '__main__':
    root = App()
    root.mainloop()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    finally:
        root.mainloop()

# pyinstaller seed_finder.spec
