import networkx as nx
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import heapq
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 读取地铁路线图信息，构建图
def read_subway_data(file_path):
    subway_graph = nx.Graph()
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = line.strip().split('，')
            station1, station2, distance = data[0], data[1], float(data[2])
            subway_graph.add_edge(station1, station2, distance=distance)
    return subway_graph

# dijkstra：计算两站点间最短路径,单源最短路算法
def dijkstra(subway_graph, start_station, end_station):
    # 初始化所有节点的距离为无穷大
    distances = {node: float('infinity') for node in subway_graph.nodes}
    distances[start_station] = 0  # 从起始到起始站的距离为0
    predecessors = {node: None for node in subway_graph.nodes}
    # 使用优先队列，用于跟踪节点和它们当前的距离
    priority_queue = [(0, start_station)]
    # Dijkstra算法步骤
    while priority_queue:
        # 已知距离最小的节点
        current_distance, current_station = heapq.heappop(priority_queue)
        # 如果当前距离大于已知距离，则跳过
        if current_distance > distances[current_station]:
            continue
        # 探索当前节点的邻节点
        for neighbor, data in subway_graph[current_station].items():
            weight = data['distance']
            # 计算当前节点到邻节点的总距离
            distance = current_distance + weight
            # 如果找到更短的路径，更新距离和前驱节点
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_station
                heapq.heappush(priority_queue, (distance, neighbor))
    # 从终点到起点重建路径
    path = []
    current_station = end_station
    while current_station is not None:
        path.insert(0, current_station)
        current_station = predecessors[current_station]
    # 检查是否存在从起点到终点的有效路径
    if path[0] == start_station:
        return path, distances[end_station]  # 返回路径和总距离
    else: # 未找到有效路径
        return None, None

# dijkstra：把边权设置为1，两点间最短路径即途径站点数最少的路径
def dijkstra_min_node(subway_graph, start_station, end_station):
    # 把边权设置为1
    for u, v in subway_graph.edges():
        subway_graph[u][v]['distance'] = 1
    # 初始化所有节点的距离为无穷大
    distances = {node: float('infinity') for node in subway_graph.nodes}
    distances[start_station] = 0  # 从起始到起始站的距离为0
    predecessors = {node: None for node in subway_graph.nodes}
    # 使用优先队列，用于跟踪节点和它们当前的距离
    priority_queue = [(0, start_station)]
    while priority_queue:
        # 已知距离最小的节点
        current_distance, current_station = heapq.heappop(priority_queue)
        # 如果当前距离大于已知距离，则跳过
        if current_distance > distances[current_station]:
            continue
        # 探索当前节点的邻节点
        for neighbor, data in subway_graph[current_station].items():
            weight = data['distance']
            # 计算当前节点到邻节点的总距离
            distance = current_distance + weight
            # 如果找到更短的路径，更新距离和前驱节点
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_station
                heapq.heappush(priority_queue, (distance, neighbor))
    # 从终点到起点重建路径
    path = []
    current_station = end_station
    while current_station is not None:
        path.insert(0, current_station)
        current_station = predecessors[current_station]
    # 检查是否存在从起点到终点的有效路径
    if path[0] == start_station:
        return path, distances[end_station]  # 返回路径和总距离
    else:  # 未找到有效路径
        return None, None

# UI界面
class SubwayUI(tk.Tk):
    def __init__(self, subway_graph):
        super().__init__()
        self.title("广州地铁路线查询系统")
        self.geometry("700x500")
        self.resizable(False, False)  # 设置窗口大小不可调整
        self.subway_graph = subway_graph
        # 输入框
        self.label1 = tk.Label(self, text="起始站点:")
        self.label1.place(x=22, y=20, width=97, height=30)
        self.entry1 = tk.Entry(self)
        self.entry1.place(x=139, y=20, width=138, height=30)
        self.label2 = tk.Label(self, text="目标站点:")
        self.label2.place(x=22, y=72, width=97, height=30)
        self.entry2 = tk.Entry(self)
        self.entry2.place(x=139, y=72, width=138, height=30)
        # 查询按钮
        self.button = tk.Button(self, text="查询路径方案", command=self.query_path)
        self.button.place(x=130, y=120, width=83, height=36)
        # 图片
        original_image = Image.open("img.png")
        original_image.thumbnail((320, 320), Image.BICUBIC)
        global tk_image
        tk_image = ImageTk.PhotoImage(original_image) # 将PIL图像转换为Tkinter PhotoImage对象
        self.img = tk.Label(self, image=tk_image) # 创建标签并显示图像
        self.img.place(x=10, y=165, width=320, height=320)
        # 消息提示
        self.label3 = tk.Label(self, text="目前仅支持一号线、二号线、三号线的查询。")
        self.label3.place(x=0, y=460, width=300, height=30)
        # 添加垂直分割线
        self.separator = ttk.Separator(self, orient="vertical")
        self.separator.place(x=350, y=0, relheight=1)
        # 划分右半区
        self.right_frame = tk.Frame(self, bg="lightgray")
        self.right_frame.place(x=351, y=0, relwidth=1, relheight=1)
        # 输出结果部分
        self.result_empty1 = tk.Message(self.right_frame, text="", width=300, bg="lightgray")
        self.result_empty1.pack(expand=False, side="top", anchor="w")
        self.result_label1 = tk.Message(self.right_frame, text="",width=300, bg="lightgray")
        self.result_label1.pack(expand=False, side="top", anchor="w")
        self.result_empty2 = tk.Message(self.right_frame, text="", width=300, bg="lightgray")
        self.result_empty2.pack(expand=False, side="top", anchor="w")
        self.result_label2 = tk.Message(self.right_frame, text="",width=300, bg="lightgray")
        self.result_label2.pack(expand=False, side="top", anchor="w")
        # 退出按钮
        self.button = tk.Button(self, text="退出", command=self.exit_system)
        self.button.place(x=630, y=450, width=50, height=36)

    # 查询按钮事件
    def query_path(self):
        start_station = self.entry1.get().strip()
        end_station = self.entry2.get().strip()
        # 判断输入合法性
        if start_station not in subway_graph or end_station not in subway_graph or not start_station or not end_station:
            messagebox.showwarning("提示", "起始站点或目标站点不存在，请重新输入。")
            self.entry1.delete(0, 'end') # 清空输入框
            self.entry2.delete(0, 'end')
            return
        # 最短路径
        shortest_path, shortest_length = dijkstra(self.subway_graph, start_station, end_station)
        if shortest_path is None:
            messagebox.showwarning("提示", f"{start_station} 到 {end_station} 不可达，请重新输入。")
            self.entry1.delete(0, 'end') # 清空输入框
            self.entry2.delete(0, 'end')
            return
        else:
            result_str = f"最短路径方案: \n\n{' -> '.join(shortest_path)}\n\n路径长度: {shortest_length:.2f} km\n\n预计耗时：{(shortest_length/35+len(shortest_path)*0.03):.2f} h\n\n"
            self.result_label1.config(text=result_str,bg="white")
        # 最少站点路径
        shortest_node_path, shortest_node_length = dijkstra_min_node(subway_graph, start_station, end_station)
        if shortest_node_path is None:
            messagebox.showwarning("提示", f"{start_station} 到 {end_station} 不可达，请重新输入。")
            self.entry1.delete(0, 'end') # 清空输入框
            self.entry2.delete(0, 'end')
            return
        else:
            result_str = f"最少站点方案: \n\n{' -> '.join(shortest_node_path)}\n\n站点数量：{shortest_node_length+1}站\n\n"
            self.result_label2.config(text=result_str,bg="white")

    # 退出按钮事件
    def exit_system(self):
        result = messagebox.askyesno("确认退出", "确定要退出系统吗？") # 提示用户是否真的要退出系统
        if result:
            self.destroy()  # 关闭主窗口

if __name__ == "__main__":
    # 加载地图数据
    subway_file_path = "subway_data.txt"
    subway_graph = read_subway_data(subway_file_path)
    # 创建UI界面
    UI = SubwayUI(subway_graph)
    UI.mainloop()
