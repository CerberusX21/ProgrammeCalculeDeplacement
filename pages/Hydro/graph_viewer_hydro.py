import math

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np



class GraphViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.graph_data = None

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.checkbox_stress = QCheckBox("Effective Stress")
        self.checkbox_conductivity = QCheckBox("Hydraulic Conductivity")
        self.show_row = QHBoxLayout()

        for checkbox in [self.checkbox_stress, self.checkbox_conductivity]:
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_graph_display)

        layout = QVBoxLayout()
        self.show_row.addWidget(QLabel("Show Graphs:"))
        self.show_row.addWidget(self.checkbox_stress)
        self.show_row.addWidget(self.checkbox_conductivity)
        layout.addLayout(self.show_row)
        layout.addWidget(self.canvas)

        self.coord_label = QLabel("Coordinates:")
        layout.addWidget(self.coord_label)

        self.setLayout(layout)

        self.follow_dots = []
        self.lines = []
        self.axes = []

        self.canvas.mpl_connect("motion_notify_event", self.mouse_move)

    def set_graph_data(self, graph_data):
        self.graph_data = graph_data
        self.update_graph_display()

    def update_graph_display(self):
        if not self.graph_data:
            return

        self.figure.clear()
        self.follow_dots = []
        self.lines = []
        self.axes = []

        cols = sum([
            self.checkbox_stress.isChecked(),
            self.checkbox_conductivity.isChecked()
        ]) or 1

        pos = 1

        if self.checkbox_stress.isChecked():
            ax = self.figure.add_subplot(1, cols, pos)

            sigma_0 = self.graph_data["sigma_0"]
            sigma_v = self.graph_data["sigma_v"]
            ei = self.graph_data["ei"]
            e0 = self.graph_data["e0"]
            cc = self.graph_data["cc"]

          

            e = e0 - cc * math.log10(sigma_v/sigma_0)

            line, = ax.plot([sigma_0, sigma_v], [e0, e], 'k-', marker='o')

            ax.set_title("Effective Stress")
            ax.set_xlabel("Effective Stress (σ') [kPa]")
            ax.set_ylabel("Void Ratio (e)")
            ax.grid(True)

            self.lines.append(line)
            self.axes.append(ax)
            self.follow_dots.append(ax.plot([], [], 'ro')[0])
            pos += 1

        if self.checkbox_conductivity.isChecked():
            ax = self.figure.add_subplot(1, cols, pos)

            xf = self.graph_data["kv0"]
            xi = self.graph_data["result"]
            yf = self.graph_data["e0"]
            ck = self.graph_data["ck"]

            yi = yf + ck * math.log10(xi/xf)

            line, = ax.plot([xi, xf], [yi, yf], 'k-', marker='o')

            ax.set_title("Hydraulic Conductivity")
            ax.set_xlabel("Hydraulic Conductivity (k) [m/s]")
            ax.set_ylabel("Void Ratio (e)")
            ax.grid(True)

            self.lines.append(line)
            self.axes.append(ax)
            self.follow_dots.append(ax.plot([], [], 'ro')[0])

        self.figure.tight_layout()
        self.canvas.draw()

    def mouse_move(self, event):
        if event.inaxes is None or event.xdata is None:
            self.coord_label.setText("Coordinates:")
            for dot in self.follow_dots:
                dot.set_visible(False)
            self.canvas.draw_idle()
            return

        coord_text = "Coordinates:"
        updated = False

        for i, (line, ax, dot) in enumerate(zip(self.lines, self.axes, self.follow_dots)):
            if event.inaxes != ax:
                dot.set_visible(False)
                continue

            xdata = line.get_xdata()
            ydata = line.get_ydata()

            if len(xdata) != 2 or len(ydata) != 2:
                dot.set_visible(False)
                continue

            x0, x1 = xdata
            y0, y1 = ydata

            x_min, x_max = sorted([x0, x1])

            if ax.get_xscale() == "log":
                log_x0, log_x1 = np.log10(x0), np.log10(x1)

                if event.xdata < x_min:
                    x, y = x0, y0
                elif event.xdata > x_max:
                    x, y = x1, y1
                else:
                    log_x = np.log10(event.xdata)
                    alpha = (log_x - log_x0) / (log_x1 - log_x0)
                    y = y0 + alpha * (y1 - y0)
                    x = event.xdata
            else:
                if event.xdata < x_min:
                    x, y = x0, y0
                elif event.xdata > x_max:
                    x, y = x1, y1
                else:
                    alpha = (event.xdata - x0) / (x1 - x0)
                    y = y0 + alpha * (y1 - y0)
                    x = event.xdata

            dot.set_data([x], [y])
            dot.set_visible(True)
            coord_text += f"\nGraph {i + 1}: x = {x:.4g}, y = {y:.4f}"
            updated = True

        self.coord_label.setText(coord_text if updated else "Coordinates:")
        self.canvas.draw_idle()

    def clear_graph(self):
        self.graph_data = None
        self.figure.clear()
        self.canvas.draw()
        self.lines.clear()
        self.axes.clear()
        self.follow_dots.clear()
        self.coord_label.setText("Coordinates:")