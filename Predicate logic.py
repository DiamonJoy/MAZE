# -*- coding: utf-8 -*-
import math
import random
import copy
import time
import sys
import Tkinter
import threading

#地图
tm = [
'##.####.###',
'#.E.#.#E..#',
'#.###.###.#',
'#.#.....#.#',
'#.#####.#.#',
'#.......#.#',
'#########.#',
'#.........#',
'#####.#####',
'#.....#...#',
'#.#####.#.#',
'#.......#.#',
'#######S###']

#存储搜索时的地图
test_map = []

#----------- 开放列表和关闭列表的元素类型，parent用来在成功的时候回溯路径 -----------
class Node_Elem:

    def __init__(self, parent, x, y):
        self.parent = parent # 回溯父节点
        self.x = x           # x坐标
        self.y = y           # y坐标

#----------- 谓词逻辑算法 -----------
class Predicate_logic:
    
    def __init__(self, root, s_x, s_y, w=11, h=13):

        self.s_x = s_x  # 起点x
        self.s_y = s_y  # 起点y
        
        self.open = []  # open表
        self.close = [] # close表
        self.path = []  # path表

        # 创建画布
        self.root = root# 画布根节点
        self.width = w  # 地图w，默认60
        self.height = h # 地图h，默认30
        self.__r = 7    # 半径
        # Tkinter.Canvas
        self.canvas = Tkinter.Canvas(
                root,
                width = self.width*50+100,
                height = self.height*50+100,
                bg = "#EBEBEB",             # 背景白色 
                xscrollincrement = 1,
                yscrollincrement = 1
            )
        self.canvas.pack(expand = Tkinter.YES, fill = Tkinter.BOTH)
        self.title("谓词逻辑迷宫算法(e:开始搜索或退出)")
        self.__bindEvents()
        self.new()

    # 按键响应程序
    def __bindEvents(self):

        self.root.bind("e", self.quite)        # 退出程序

    # 退出程序
    def quite(self, evt):
        self.root.destroy()

    # 更改标题
    def title(self, s):
        self.root.title(s)

    # 初始化
    def new(self):

        node = self.canvas.create_oval(30 - self.__r,
                            20 - self.__r, 30 + self.__r, 20 + self.__r,
                            fill = "#ff0000",
                            outline = "#ffffff",
                            tags = "node",
                        )
        self.canvas.create_text(50,20, 
                            text = u'Wall',
                            fill = 'black'
                        )
        node = self.canvas.create_oval(80 - self.__r,
                            20 - self.__r, 80 + self.__r, 20 + self.__r,
                            fill = "#00ff00",
                            outline = "#ffffff",
                            tags = "node",
                        )
        self.canvas.create_text(100,20,  
                            text = u'Path', 
                            fill = 'black'
                        )
        node = self.canvas.create_oval(130 - self.__r,
                            20 - self.__r, 130 + self.__r, 20 + self.__r,
                            fill = "#AAAAAA",
                            outline = "#ffffff",
                            tags = "node",
                        )
        self.canvas.create_text(170,20,
                            text = u'Searched',
                            fill = 'black'
                        )
                    
        for i in range(self.width):
            for j in range(self.height):
                # 生成障碍节点，半径为self.__r
                if test_map[j][i] == '#':
                    node = self.canvas.create_oval(i*50+50 - self.__r,
                            j*50+50 - self.__r, i*50+50 + self.__r, j*50+50 + self.__r,
                            fill = "#ff0000",      # 填充红色
                            outline = "#ffffff",   # 轮廓白色
                            tags = "node",
                        )
                # 显示起点
                if test_map[j][i] == 'S':
                    node = self.canvas.create_oval(i*50+50 - self.__r,
                            j*50+50 - self.__r, i*50+50 + self.__r, j*50+50 + self.__r,
                            fill = "#00ff00",      # 填充绿色
                            outline = "#ffffff",   # 轮廓白色
                            tags = "node",
                        )
                    self.canvas.create_text(i*50+50,j*50+50+10,  # 使用create_text方法在坐标处绘制文字  
                            text = u'Start',                     # 所绘制文字的内容  
                            fill = 'black'                       # 所绘制文字的颜色为灰色
                        )
                # 显示终点
                if test_map[j][i] == 'E':
                    node = self.canvas.create_oval(i*50+50 - self.__r,
                            j*50+50 - self.__r, i*50+50 + self.__r, j*50+50 + self.__r,
                            fill = "#00ff00",      # 填充绿色
                            outline = "#ffffff",   # 轮廓白色
                            tags = "node",
                        )
                    self.canvas.create_text(i*50+50,j*50+50-20,   # 使用create_text方法在坐标处绘制文字  
                            text = u'End',                        # 所绘制文字的内容  
                            fill = 'black'                        # 所绘制文字的颜色为灰色
                        )
                # 生成路径节点，半径为self.__r
                if test_map[j][i] == '*':
                    node = self.canvas.create_oval(i*50+50 - self.__r,
                            j*50+50 - self.__r, i*50+50 + self.__r, j*50+50 + self.__r,
                            fill = "#0000ff",      # 填充蓝色
                            outline = "#ffffff",   # 轮廓白色
                            tags = "node",
                        )
                # 生成搜索区域，半径为self.__r
                if test_map[j][i] == ' ':
                    node = self.canvas.create_oval(i*50+50 - self.__r,
                            j*50+50 - self.__r, i*50+50 + self.__r, j*50+50 + self.__r,
                            fill = "#AAAAAA",      # 填充白色
                            outline = "#ffffff",   # 轮廓白色
                            tags = "node",
                        )
        
        
    # 查找路径的入口函数
    def find_path(self):
        # 构建开始节点
        p = Node_Elem(None, self.s_x, self.s_y)
        while True:
            # 广度优先扩展节点
            self.extend_round(p)
            # 如果open表为空，则不存在路径，返回
            if not self.open:
                return
            # 取open表的第一个节点
            idx, p = self.get_node()
            # 到达终点，生成路径，返回
            if self.is_target(p):
                self.make_path(p)
                return
            # 把此节点加入close表，并从open表里删除
            self.close.append(p)
            del self.open[idx]

    # 生成路径    
    def make_path(self, p):
        # 从结束点回溯到开始点，开始点的parent == None
        while p:
            self.path.append((p.x, p.y))
            p = p.parent

    # 判断是否为终点
    def is_target(self, i):
        return test_map[i.y][i.x] == 'E'

    # 取open表的一个节点
    def get_node(self):
        for idx, i in enumerate(self.open):
             return idx, i

    # 扩展节点
    def extend_round(self, p):
        # 八个方向移动
        xs = (-1, 0, 1, -1, 1, -1, 0, 1)
        ys = (-1,-1,-1,  0, 0,  1, 1, 1)
        # 上下左右四个方向移动
        xs = (0, -1, 1, 0)
        ys = (-1, 0, 0, 1)
        for x, y in zip(xs, ys):
            new_x, new_y = x + p.x, y + p.y
            # 检查位置是否合法
            if not self.is_valid_coord(new_x, new_y):
                continue
            # 构造新的节点
            node = Node_Elem(p, new_x, new_y)
            # 新节点在关闭列表，则忽略
            if self.node_in_close(node):
                continue
            i = self.node_in_open(node)
            # 新节点在open表
            if i != -1:
                continue
            # 否则加入open表
            self.open.append(node)
    
    # 检查节点是否在close表
    def node_in_close(self, node):
        for i in self.close:
            if node.x == i.x and node.y == i.y:
                return True
        return False
    
    # 检查节点是否在open表，返回序号  
    def node_in_open(self, node):
        for i, n in enumerate(self.open):
            if node.x == n.x and node.y == n.y:
                return i
        return -1

    # 判断位置是否合法，超出边界或者为阻碍    
    def is_valid_coord(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return test_map[y][x] != '#'

    # 搜寻过的位置
    def get_searched(self):
        l = []
        for i in self.open:
            l.append((i.x, i.y))
        for i in self.close:
            l.append((i.x, i.y))
        return l

# 获取起点坐标
def get_start_XY():
    return get_symbol_XY('S')

# 获取终点坐标
def get_end_XY():
    return get_symbol_XY('E')

# 查找特定元素
def get_symbol_XY(s):
    for y, line in enumerate(test_map):
        try:
            x = line.index(s)
        except:
            continue
        else:
            break
    return x, y
        
# 标记路径位置 
def mark_path(l):
    mark_symbol(l, '*')

# 标记已搜索过的位置    
def mark_searched(l):
    mark_symbol(l, ' ')

# 标记函数
def mark_symbol(l, s):
    for x, y in l:
        test_map[y][x] = s

# 标记起点和终点
def mark_start_end(s_x, s_y):
    test_map[s_y][s_x] = 'S'
    
# 将地图字符串转化为表
def tm_to_test_map():
    for line in tm:
        test_map.append(list(line))
        
# 寻找路径        
def find_path():
    s_x, s_y = get_start_XY()
    e_x, e_y = get_end_XY()
    # 广度优先搜索
    logic = Predicate_logic(Tkinter.Tk(), s_x, s_y)
    logic.root.mainloop()
    logic.find_path()
    searched = logic.get_searched()
    path = logic.path
    # 标记已搜索过的位置
    mark_searched(searched)
    # 标记路径位置 
    mark_path(path)
    # 标记起点和终点
    mark_start_end(s_x, s_y)
    print u"路径长度:%d" %(len(path))
    print u"搜索过的区域:%d" %(len(searched))
    logic = Predicate_logic(Tkinter.Tk(), s_x, s_y)
    logic.root.mainloop()
    
#----------- 程序的入口处 -----------
                
if __name__ == '__main__':

    print u""" 
--------------------------------------------------------
    程序：谓词逻辑迷宫问题程序 
    作者：DiamonJoy
    日期：2016-1-11
    语言：Python 2.7 
-------------------------------------------------------- 
    """
    # 载入地图
    tm_to_test_map()
    # 寻找路径
    find_path()
