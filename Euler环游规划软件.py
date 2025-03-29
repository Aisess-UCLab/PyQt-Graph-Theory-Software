import sys
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, \
    QMessageBox, QFileDialog
import json


class EulerianPathApp(QWidget):
    def __init__(self):
        super().__init__()
        self.graph = nx.MultiGraph()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('图欧拉环路规划软件')
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # 边输入区域
        input_layout = QHBoxLayout()
        self.start_node_input = QLineEdit(self)
        self.start_node_input.setPlaceholderText('请输入起始节点')
        input_layout.addWidget(self.start_node_input)

        self.end_node_input = QLineEdit(self)
        self.end_node_input.setPlaceholderText('请输入终止节点')
        input_layout.addWidget(self.end_node_input)

        self.add_edge_button = QPushButton('添加边', self)
        self.add_edge_button.clicked.connect(self.add_edge)
        input_layout.addWidget(self.add_edge_button)
        layout.addLayout(input_layout)

        # 按钮区域
        self.find_euler_button = QPushButton('查找欧拉环游', self)
        self.find_euler_button.clicked.connect(self.find_eulerian_circuit)
        layout.addWidget(self.find_euler_button)

        self.load_button = QPushButton('加载图', self)
        self.load_button.clicked.connect(self.load_graph)
        layout.addWidget(self.load_button)

        self.save_button = QPushButton('保存图', self)
        self.save_button.clicked.connect(self.save_graph)
        layout.addWidget(self.save_button)

        # 结果显示
        self.result_label = QLabel('结果：', self)
        layout.addWidget(self.result_label)

        # 图形可视化
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.clear_plots()

    def add_edge(self):
        start_node = self.start_node_input.text().strip()
        end_node = self.end_node_input.text().strip()

        if not start_node or not end_node:
            QMessageBox.warning(self, '输入错误', '请填写起始节点和终止节点！')
            return

        self.graph.add_edge(start_node, end_node)
        self.start_node_input.clear()
        self.end_node_input.clear()
        self.update_graph()

    def find_eulerian_circuit(self):
        if not nx.is_eulerian(self.graph):
            QMessageBox.warning(self, '不是欧拉图', '此图不是一个欧拉图，无法完成一笔画！')
            return

        try:
            eulerian_circuit = list(nx.eulerian_circuit(self.graph))
            result = ''
            # 使用字典存储每条边的多个顺序标记
            edge_labels = {}  # 存储边的标签，值为列表
            for idx, (u, v) in enumerate(eulerian_circuit):
                # 按字母顺序存储边（确保唯一性）
                u, v = sorted((u, v))
                if (u, v) not in edge_labels:
                    edge_labels[(u, v)] = []
                edge_labels[(u, v)].append(idx + 1)  # 使用列表来存储顺序号
            result = ' -> '.join(u for u, v in eulerian_circuit)
            self.result_label.setText('欧拉环路：' + result + ' -> ' + eulerian_circuit[0][0])
            # 更新图形显示，传递高亮边和边标签
            self.update_graph_with_labels(eulerian_circuit, edge_labels)
        except nx.NetworkXError as e:
            QMessageBox.warning(self, '错误', f'计算欧拉环游时出错：{e}')

    def load_graph(self):
        filename, _ = QFileDialog.getOpenFileName(self, '打开图文件', '', 'JSON 文件 (*.json)')
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)

                    # 将图转换为多重图
                    G_multigraph = nx.MultiGraph()

                    # 添加节点
                    for node in data['nodes']:
                        G_multigraph.add_node(node['id'])

                    # 添加边，确保多重边被添加
                    for link in data['links']:
                        G_multigraph.add_edge(link['source'], link['target'])
                    self.graph = G_multigraph
                    self.update_graph()
            except Exception as e:
                QMessageBox.warning(self, '错误', f'加载图失败：{e}')

    def save_graph(self):
        filename, _ = QFileDialog.getSaveFileName(self, '保存图文件', '', 'JSON 文件 (*.json)')
        if filename:
            try:
                data = nx.node_link_data(self.graph)
                with open(filename, 'w') as f:
                    json.dump(data, f)
                QMessageBox.information(self, '成功', '图已成功保存！')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'保存图失败：{e}')

    def update_graph_with_labels(self, highlight_edges, edge_labels):
        self.ax.clear()
        self.ax.set_axis_off()  # Hide axis and ticks
        pos = nx.spring_layout(self.graph)  # 使用布局算法定位节点

        nx.draw_networkx_nodes(
            self.graph, pos, node_size=700, node_color='lightblue', ax=self.ax
        )
        nx.draw_networkx_labels(self.graph, pos, font_size=10, font_weight='bold', ax=self.ax)

        # 绘制多重边，去掉偶数条边时的中间直连线
        for u, v in edge_labels:
            edges = list(self.graph[u][v].values())  # 获取多重边信息
            edge_count = len(edges)
            shunxu_index = 0
            for idx in range(edge_count):

                offset = 0.2 * (idx - (edge_count - 1) / 2)  # 偏移值，确保偶数条边对称显示
                connection_style = f'arc3,rad={offset}'  # 设置弧线的弯曲度

                nx.draw_networkx_edges(
                    self.graph, pos,
                    arrows=True,
                    edgelist=[(u, v)],
                    edge_color='gray',
                    style='solid',
                    ax=self.ax,
                    connectionstyle=connection_style
                )

                edge_label = edge_labels.get((u, v), edge_labels.get((u, v), None))[shunxu_index]
                shunxu_index += 1
                # 如果有序号，显示它
                if edge_label:
                    # 获取当前边的所有位置
                    edge_count = len(self.graph[u][v])
                    # 计算边的显示位置
                    label_pos = (pos[u] + pos[v]) / 2 + offset * 0.1  # 标签位置偏移

                    # 通过稍微调整偏移量，避免标签偏离路径
                    label_pos_with_offset = label_pos + np.array([offset * 0.1, 0])  # 可以根据实际情况调整

                    # 手动为每条边添加标签
                    self.ax.text(
                        label_pos_with_offset[0], label_pos_with_offset[1],
                        str(edge_label),
                        color='blue',
                        fontsize=10,
                        fontweight='bold',
                        ha='center', va='center'  # 确保标签居中
                    )
        self.canvas.draw()

    def update_graph(self, highlight_edges=None):
        self.ax.clear()
        self.ax.set_axis_off()  # Hide axis and ticks

        pos = nx.spring_layout(self.graph)  # 使用布局算法定位节点

        nx.draw_networkx_nodes(
            self.graph, pos, node_size=700, node_color='lightblue', ax=self.ax
        )
        nx.draw_networkx_labels(self.graph, pos, font_size=10, font_weight='bold', ax=self.ax)
        # 绘制多重边，去掉偶数条边时的中间直连线
        for u, v in self.graph.edges():
            edges = list(self.graph[u][v].values())  # 获取多重边信息
            edge_count = len(edges)

            for idx in range(edge_count):
                offset = 0.2 * (idx - (edge_count - 1) / 2)  # 偏移值，确保偶数条边对称显示
                connection_style = f'arc3,rad={offset}'  # 设置弧线的弯曲度

                nx.draw_networkx_edges(
                    self.graph, pos,
                    arrows=True,
                    edgelist=[(u, v)],
                    edge_color='gray',
                    style='solid',
                    ax=self.ax,
                    connectionstyle=connection_style
                )

        self.canvas.draw()

    def clear_plots(self):
        self.ax.clear()
        self.ax.set_axis_off()  # Hide axis and ticks
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EulerianPathApp()
    window.show()
    sys.exit(app.exec_())
