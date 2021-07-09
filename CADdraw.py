import tkinter
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk
import csv
from pyautocad import Autocad, APoint


class CADdraw:
    def __init__(self):
        # 准备存储csv文件的名称、X坐标、Y坐标、高程数组
        self.name = []
        self.Xarray = []
        self.Yarray = []
        self.Harray = []

        # 生成主窗口对象、标题、指定主框体大小
        self.root = tkinter.Tk()
        self.root.title('CAD自动画图工具')
        self.root.geometry('400x200')

        # 创建标签,并且添加到主窗口中
        label_choseCsvFile = tkinter.Label(self.root, text='选择csv文件')
        label_choseCsvFile.place(x=10, y=20)
        # 创建文本框、路径变量
        self.path = tkinter.StringVar()
        text_path = tkinter.Entry(self.root, borderwidth=True, width=35, textvariable=self.path)
        text_path.place(x=90, y=20)

        # 创建按钮，并且添加到主窗口中
        btn_skim = tkinter.Button(self.root, text='浏览', command=self.get_csv_file_path)
        btn_skim.place(x=350, y=15)
        self.btn_draw = tkinter.Button(self.root, text='开始绘制', command=self.draw)
        self.btn_draw.place(x=180, y=150)

        # 创建标签 并且添加到主窗口中
        label_drawType = tkinter.Label(self.root, text='绘制类型')
        label_drawType.place(x=10, y=60)

        # 下拉框
        self.drawType = tkinter.StringVar()
        com_drawType = ttk.Combobox(self.root, textvariable=self.drawType)
        com_drawType.place(x=90, y=60)
        # 设置下拉数据
        com_drawType["value"] = ("直线", "点")
        # 设置默认值
        com_drawType.current(0)

        # 创建标签 并且添加到主窗口中
        label_dataFiltering = tkinter.Label(self.root, text='数据筛选')
        label_dataFiltering.place(x=10, y=90)

        # 下拉框
        self.filtering = tkinter.StringVar()
        self.com = ttk.Combobox(self.root, textvariable=self.filtering)
        self.com.place(x=90, y=90)
        # 设置下拉数据
        self.com["value"] = ("所有", "从...至...")
        # 设置默认值
        self.com.current(0)
        self.com.bind("<<ComboboxSelected>>", self.from_to)

        self.label_from = tkinter.Label(self.root, text='从')
        self.label_to = tkinter.Label(self.root, text='至')
        self.text_form = tkinter.Entry(self.root, borderwidth=True, width=30)
        self.text_to = tkinter.Entry(self.root, borderwidth=True, width=30)

        # 选择标记高层的多选框和字高
        self.x_checkbutton = 10
        self.y_checkbutton = 120
        self.fontHeight = tkinter.IntVar()
        self.checkbutton = tkinter.Checkbutton(self.root, text='标注高层', variable=self.fontHeight, onvalue=1, offvalue=0, command=self.selection)
        self.checkbutton.place(x=self.x_checkbutton, y=self.y_checkbutton)
        self.label_fontHeight = tkinter.Label(self.root, text='字高')
        self.fontHeightNum = tkinter.StringVar()
        self.text_fontHeight = tkinter.Entry(self.root, borderwidth=True, width=10, textvariable=self.fontHeightNum)
        self.fontHeightNum.set(1)

        #显示菜单栏
        menubar = tkinter.Menu(self.root)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='帮助', menu=filemenu)
        # menubar.add_cascade(label='关于', menu=filemenu)
        filemenu.add_command(label='帮助信息', command=self.help)
        filemenu.add_command(label='关于', command=self.about)

        self.root.config(menu=menubar)

        # 保持主窗口一直消息循环中
        self.root.mainloop()

    # 获取csv文件路径
    def get_csv_file_path(self):
        filename = tkinter.filedialog.askopenfilename(filetypes=[("csv格式", "csv")])
        self.path.set(filename)

    # 开始绘制——调用4个函数
    def draw(self):
        path = self.path.get()
        if path:
            self.csv_obj = self.connect_cad(path)

            try:
                self.read_csv_data(self.csv_obj['reader'])
            except Exception as e:
                tkinter.messagebox.showerror('错误', '读取csv文件内容错误！值必须为数值类型！')
                print(e)
                return

            try:
                self.drawing(self.csv_obj['acad'])
                tkinter.messagebox.showinfo('结果', '绘制成功！')
            except Exception as e:
                tkinter.messagebox.showerror('错误', '绘制失败！')
            # 关闭文件！
            self.csv_obj['csv_file'].close()

        else:
            tkinter.messagebox.showerror('错误', '文件名不能为空！')

    # 连接CAD，返回csv_obj
    def connect_cad(self, path):
        self.acad = Autocad(create_if_not_exists=True)
        csv_file = open(path, 'r', newline='')
        reader = csv.reader(csv_file)
        return {'acad': self.acad, 'reader': reader, 'csv_file': csv_file}

    # 读取csv文件数据，保存到数组中，返回读取的数组长度
    def read_csv_data(self, reader):
        # 如果数组里为空才开始读取并添加数据
        if len(self.Xarray) == 0:
            for row in reader:
                self.name.append(row[0])
                self.Xarray.append(float(row[1]))
                self.Yarray.append(float(row[2]))
                self.Harray.append(row[3])
            length = len(self.Xarray)

        # 否则直接读取数组长度
        else:
            length = len(self.Xarray)
        return length

    def drawing(self, acad):
        length = self.read_csv_data(self.csv_obj['reader'])
        beginning = 0
        ending = length
        if self.drawType.get() == "直线" and self.filtering.get() == "所有":
            for i in range(length + 1):
                try:
                    P1 = APoint(self.Yarray[i], self.Xarray[i])
                    P2 = APoint(self.Yarray[i + 1], self.Xarray[i + 1])
                except Exception as e:
                    continue
                acad.model.AddLine(P1, P2)
                if self.fontHeight.get() == 1:
                    self.add_height(self.Harray[i], P1, float(self.fontHeightNum.get()))

        elif (self.drawType.get() == "点" and self.filtering.get() == "所有"):
            for i in range(length):
                P = APoint(self.Yarray[i], self.Xarray[i])
                acad.model.AddPoint(P)
                if self.fontHeight.get() == 1:
                    self.add_height(self.Harray[i], P, float(self.fontHeightNum.get()))
        
        elif self.drawType.get() == "直线" and self.filtering.get() == "从...至...":
            text_from = self.text_form.get()
            text_to = self.text_to.get()

            for x in range(length):
                if (self.name[x] == text_from):
                    beginning = x
                elif (self.name[x] == text_to):
                    ending = x
                else:
                    pass

            for i in range(beginning, ending + 1):
                try:
                    P1 = APoint(self.Yarray[i], self.Xarray[i])
                    P2 = APoint(self.Yarray[i + 1], self.Xarray[i + 1])
                except Exception as e:
                    continue
                acad.model.AddLine(P1, P2)
                if self.fontHeight.get() == 1:
                    self.add_height(self.Harray[i], P1, float(self.fontHeightNum.get()))

        else: #self.drawType.get() == "点" and self.filtering.get() == "从...至...":
            text_from = self.text_form.get()
            text_to = self.text_to.get()
            for x in range(length):
                if self.name[x] == text_from:
                    beginning = x

                elif self.name[x] == text_to:
                    ending = x
                    print(ending)

                else:
                    pass

            for i in range(beginning, ending):
                P = APoint(self.Yarray[i], self.Xarray[i])
                acad.model.AddPoint(P)
                if self.fontHeight.get() == 1:
                    self.add_height(self.Harray[i], P, float(self.fontHeightNum.get()))

    # 选择从...至...的选项后再绘制上去的组件
    def from_to(self, event):
        if self.com.get() == '从...至...':
            self.root.geometry('400x250')  # 指定主框体大小；
            self.btn_draw.place(x=180, y=210)
            # 创建标签 并且添加到主窗口中
            self.label_from.place(x=90, y=120)
            # 创建文本框
            self.text_form.place(x=120, y=120)

            # 创建标签 并且添加到主窗口中
            self.label_to.place(x=90, y=150)
            # 创建文本框
            self.text_to.place(x=120, y=150)

            # 字高
            self.x_checkbutton = 10
            self.y_checkbutton = 180
            self.checkbutton.place(x=self.x_checkbutton, y=self.y_checkbutton)

        else:
            self.label_from.place_forget()
            self.label_to.place_forget()
            self.text_form.place_forget()
            self.text_to.place_forget()
            self.root.geometry('400x200')  # 指定主框体大小；
            self.btn_draw.place(x=180, y=150)
            # 字高
            self.x_checkbutton = 10
            self.y_checkbutton = 120
            self.checkbutton.place(x=self.x_checkbutton, y=self.y_checkbutton)

    def selection(self):
        if self.fontHeight.get() == 1:
            self.label_fontHeight.place(x=self.x_checkbutton + 90, y=self.y_checkbutton + 2)
            self.text_fontHeight.place(x=self.x_checkbutton + 125, y=self.y_checkbutton + 3)
        else:
            self.label_fontHeight.place_forget()
            self.text_fontHeight.place_forget()

    def add_height(self, text, p, fontHeight):
        self.acad.model.AddText(text, p, fontHeight)

    # 显示帮助信息
    def help(self):
        helpInfo = "帮助信息：\n1、点击浏览按钮选择csv文件，目前仅支持csv格式文件，其它格式功能暂未开发。\n2、绘制类型中，选择‘直线’" \
                   "绘制线段，选择‘点’，仅标记出相应的点。\n3、数据筛选选项中，选择‘所有’将把文件中所有的点绘制在图上，选择‘从...至...’则将指定" \
                   "数据绘制在图上，注意数据需为连续数据。\n4、勾选标记高层后，将在点附近标记其相应高层。\n5、建议先打开CAD软件再启动本脚本，" \
                   "此脚本将会在当前CAD活动窗口中绘图。"
        tkinter.messagebox.showinfo('帮助', helpInfo)

    def about(self):
        aboutInfo = "作者：\n@西南大学SWU园艺园林学院——何柳旭\n" \
                    "Author: @By Leo Santiago, College of horticulture and landscape architecture, Southwest University.\n" \
                    "Version 1.0.0 base on python pyautocad and tkinter.\n" \
                    "Date at July 8.\n" \
                    "If you have any problem or advise, please visit me at my github."

        tkinter.messagebox.showinfo('帮助', aboutInfo)
cad = CADdraw()

