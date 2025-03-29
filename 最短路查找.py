import sys
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QColor
import json

# Set up matplotlib to support Chinese
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # Use SimHei font for Chinese characters
matplotlib.rcParams['axes.unicode_minus'] = False  # Ensure minus signs are shown correctly


class ShortestPathApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the graph
        self.graph = nx.Graph()

        # UI setup
        self.setWindowTitle('加权图最短路径查找软件')
        self.setGeometry(200, 200, 800, 600)

        # Create layout
        layout = QVBoxLayout()

        # Input for head node, tail node and weight
        input_layout = QHBoxLayout()

        self.head_node_input = QLineEdit(self)
        self.head_node_input.setPlaceholderText('输入头节点')
        input_layout.addWidget(self.head_node_input)

        self.tail_node_input = QLineEdit(self)
        self.tail_node_input.setPlaceholderText('输入尾节点')
        input_layout.addWidget(self.tail_node_input)

        self.weight_input = QLineEdit(self)
        self.weight_input.setPlaceholderText('输入边的权重')
        input_layout.addWidget(self.weight_input)

        self.add_edge_button = QPushButton('添加边', self)
        self.add_edge_button.clicked.connect(self.add_edge)
        input_layout.addWidget(self.add_edge_button)

        layout.addLayout(input_layout)

        # Load button to visualize graph
        self.load_button = QPushButton('加载图', self)
        self.load_button.clicked.connect(self.load_graph)
        layout.addWidget(self.load_button)

        # Save button to save graph
        self.save_button = QPushButton('保存图', self)
        self.save_button.clicked.connect(self.save_graph)
        layout.addWidget(self.save_button)

        # Inputs for start and end nodes
        self.start_node_input = QLineEdit(self)
        self.start_node_input.setPlaceholderText('输入起始节点')
        layout.addWidget(self.start_node_input)

        self.end_node_input = QLineEdit(self)
        self.end_node_input.setPlaceholderText('输入终点节点')
        layout.addWidget(self.end_node_input)

        # Button to find shortest path
        self.find_path_button = QPushButton('寻找最短路径', self)
        self.find_path_button.clicked.connect(self.find_shortest_path)
        layout.addWidget(self.find_path_button)

        # Result display
        self.result_label = QLabel('结果: ', self)
        layout.addWidget(self.result_label)

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
        try:
            head_node = self.head_node_input.text()
            tail_node = self.tail_node_input.text()
            weight = float(self.weight_input.text())

            if head_node and tail_node and isinstance(weight, (int, float)):
                self.graph.add_edge(head_node, tail_node, weight=weight)
                self.head_node_input.clear()
                self.tail_node_input.clear()
                self.weight_input.clear()
                self.update_graph_visualization()
            else:
                self.result_label.setText('请输入合法的头节点、尾节点和权重。')
        except ValueError:
            self.result_label.setText('权重格式无效，请输入有效的数字。')

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
            self.result_label.setText(f'图已保存至 {filename}')

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

        # Draw edge labels (weights) in the first subplot
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, ax=self.axs[0])

        # Refresh the canvas to display the new plot
        self.canvas.draw()

    def find_shortest_path(self):
        # Get start and end nodes
        start_node = self.start_node_input.text()
        end_node = self.end_node_input.text()

        if start_node not in self.graph or end_node not in self.graph:
            self.result_label.setText('起始节点或终点节点不在图中。')
            return

        # Find the shortest path using Dijkstra's algorithm
        try:
            path = nx.dijkstra_path(self.graph, source=start_node, target=end_node, weight='weight')
            distance = nx.dijkstra_path_length(self.graph, source=start_node, target=end_node, weight='weight')

            self.result_label.setText(f'最短路径: {path}, 距离: {distance}')

            # Clear the result graph before drawing the new one
            self.axs[1].clear()

            # Redraw the graph in the second subplot (搜索结果)
            pos = nx.spring_layout(self.graph)
            nx.draw(self.graph, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=10,
                    ax=self.axs[1])

            # Highlight edges in the shortest path
            edges_to_highlight = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            nx.draw_networkx_edges(self.graph, pos, edgelist=edges_to_highlight, edge_color='red', width=2,
                                   ax=self.axs[1])

            # Draw edge labels again to make sure they are visible
            edge_labels = nx.get_edge_attributes(self.graph, 'weight')
            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, ax=self.axs[1])

            # Refresh the canvas to display the highlighted path
            self.canvas.draw()

        except nx.NetworkXNoPath:
            self.result_label.setText(f'从 {start_node} 到 {end_node} 没有路径。')

    def clear_plots(self):
        # Initialize empty graphs (show only titles initially)
        for ax in self.axs:
            ax.clear()
            ax.set_axis_off()  # Hide axis and ticks
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShortestPathApp()
    window.show()
    sys.exit(app.exec_())
