import sys
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, \
    QFileDialog, QMessageBox
from PyQt5.QtGui import QColor
import json
import matplotlib

# Set up matplotlib to support Chinese
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # Use SimHei font for Chinese characters
matplotlib.rcParams['axes.unicode_minus'] = False  # Ensure minus signs are shown correctly


class EdgeColoringApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the graph
        self.graph = nx.Graph()

        # UI setup
        self.setWindowTitle('图边着色分析软件')
        self.setGeometry(200, 200, 800, 600)

        # Create layout
        layout = QVBoxLayout()

        # Input for head node, tail node
        input_layout = QHBoxLayout()

        self.head_node_input = QLineEdit(self)
        self.head_node_input.setPlaceholderText('输入头节点')
        input_layout.addWidget(self.head_node_input)

        self.tail_node_input = QLineEdit(self)
        self.tail_node_input.setPlaceholderText('输入尾节点')
        input_layout.addWidget(self.tail_node_input)

        self.add_edge_button = QPushButton('添加边', self)
        self.add_edge_button.clicked.connect(self.add_edge)
        input_layout.addWidget(self.add_edge_button)

        layout.addLayout(input_layout)

        # Input for number of colors
        self.num_colors_input = QLineEdit(self)
        self.num_colors_input.setPlaceholderText('输入边色数')
        layout.addWidget(self.num_colors_input)

        # Load button to visualize graph
        self.load_button = QPushButton('加载图', self)
        self.load_button.clicked.connect(self.load_graph)
        layout.addWidget(self.load_button)

        # Save button to save graph
        self.save_button = QPushButton('保存图', self)
        self.save_button.clicked.connect(self.save_graph)
        layout.addWidget(self.save_button)

        # Button to apply edge coloring
        self.apply_coloring_button = QPushButton('应用边着色', self)
        self.apply_coloring_button.clicked.connect(self.apply_edge_coloring)
        layout.addWidget(self.apply_coloring_button)

        # Create Matplotlib figure and canvas for visualization
        self.fig, self.axs = plt.subplots(1, 2, figsize=(12, 6))  # Create two subplots
        self.canvas = FigureCanvas(self.fig)

        # Create two labels for the titles
        self.title_label_1 = QLabel('原始图', self)
        self.title_label_2 = QLabel('搜索结果', self)

        # Set label font size
        self.title_label_1.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.title_label_2.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Set background color for each region
        self.title_label_1.setAutoFillBackground(True)
        self.title_label_1.setStyleSheet("background-color: lightgrey; font-size: 16px;")
        self.title_label_2.setAutoFillBackground(True)
        self.title_label_2.setStyleSheet("background-color: lightblue; font-size: 16px;")

        # Create layout for the two regions with some space between them
        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.canvas)

        layout.addLayout(graph_layout)

        # Add labels for "Original Graph" and "Search Results"
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label_1)
        title_layout.addWidget(self.title_label_2)
        layout.addLayout(title_layout)

        self.setLayout(layout)

        # Initialize empty graphs (show only titles initially)
        self.clear_plots()

    def add_edge(self):
        # Add an edge to the graph
        head_node = self.head_node_input.text()
        tail_node = self.tail_node_input.text()

        if not head_node or not tail_node:
            self.result_label.setText('请输入合法的头节点和尾节点。')
            return

        self.graph.add_edge(head_node, tail_node)
        self.head_node_input.clear()
        self.tail_node_input.clear()
        self.update_graph_visualization()

    def load_graph(self):
        # Load graph from JSON
        filename, _ = QFileDialog.getOpenFileName(self, '打开图文件', '', 'JSON Files (*.json)')

        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.graph = nx.node_link_graph(data)
                self.update_graph_visualization()

    def save_graph(self):
        # Save graph to JSON
        filename, _ = QFileDialog.getSaveFileName(self, '保存图文件', '', 'JSON Files (*.json)')

        if filename:
            data = nx.node_link_data(self.graph)
            with open(filename, 'w') as f:
                json.dump(data, f)

    from PyQt5.QtWidgets import QMessageBox

    def apply_edge_coloring(self):
        try:
            # 检查是否输入边色数
            num_colors_text = self.num_colors_input.text()
            if not num_colors_text.strip():
                QMessageBox.warning(self, "警告", "请输入边色数！")
                return

            num_colors = int(num_colors_text)
            if num_colors <= 0:
                raise ValueError("边色数必须大于0。")

            # 调用边着色函数
            success = self.edge_coloring(num_colors)
            if not success:
                QMessageBox.warning(self, "警告", "无可行的边着色方案！")
                return

            # 更新着色结果
            self.make_color_result()

        except ValueError as e:
            QMessageBox.warning(self, "错误", f"错误: {e}")

    def edge_coloring(self, num_colors):
        # 初始化边的颜色为未着色
        self.edge_colors = {edge: -1 for edge in self.graph.edges}  # -1 表示未着色

        # 使用贪心算法尝试为边着色
        for edge in self.graph.edges:
            available_colors = [True] * num_colors

            # 检查相邻边的颜色
            for neighbor in self.graph.neighbors(edge[0]):
                if (edge[0], neighbor) in self.edge_colors:
                    color = self.edge_colors[(edge[0], neighbor)]
                    if color != -1:
                        available_colors[color] = False
                if (neighbor, edge[0]) in self.edge_colors:
                    color = self.edge_colors[(neighbor, edge[0])]
                    if color != -1:
                        available_colors[color] = False

            for neighbor in self.graph.neighbors(edge[1]):
                if (edge[1], neighbor) in self.edge_colors:
                    color = self.edge_colors[(edge[1], neighbor)]
                    if color != -1:
                        available_colors[color] = False
                if (neighbor, edge[1]) in self.edge_colors:
                    color = self.edge_colors[(neighbor, edge[1])]
                    if color != -1:
                        available_colors[color] = False

            # 找到可用颜色
            found_color = False
            for color in range(num_colors):
                if available_colors[color]:
                    self.edge_colors[edge] = color
                    found_color = True
                    break

            if not found_color:
                return False  # 无法为某条边找到可用颜色

        return True  # 所有边着色成功

    def make_color_result(self):
        self.axs[1].clear()
        self.axs[1].set_axis_off()  # 隐藏坐标轴

        # 使用 spring 布局安排节点
        pos = nx.spring_layout(self.graph)

        # 提取边的颜色和标签
        edge_colors = [plt.cm.tab20(self.edge_colors.get(e, 0) / 20) for e in self.graph.edges]  # 映射颜色
        edge_labels = {e: self.edge_colors.get(e, 0) for e in self.graph.edges}  # 颜色编号作为标签

        # 绘制图形节点和边
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_size=500,
            node_color='lightblue',
            font_size=10,
            ax=self.axs[1],
            edge_color=edge_colors,
        )

        # 绘制边的标签
        nx.draw_networkx_edge_labels(
            self.graph,
            pos,
            edge_labels=edge_labels,
            font_color="black",  # 标签字体颜色
            font_size=10,
            ax=self.axs[1],
        )

        # 刷新画布
        self.canvas.draw()

    def update_graph_visualization(self):
        # Clear previous plot
        for ax in self.axs:
            ax.clear()

        # Remove any borders, ticks, etc.
        for ax in self.axs:
            ax.set_axis_off()  # Hide axis and ticks

        # Create a layout for nodes
        pos = nx.spring_layout(self.graph)  # Use spring layout for node positioning

        # Draw the graph in the first subplot (原始图)
        nx.draw(self.graph, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=10, ax=self.axs[0])

        # Refresh the canvas to display the new plot
        self.canvas.draw()

    def clear_plots(self):
        # Initialize empty graphs (show only titles initially)
        for ax in self.axs:
            ax.clear()
            ax.set_axis_off()  # Hide axis and ticks
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EdgeColoringApp()
    window.show()
    sys.exit(app.exec_())
