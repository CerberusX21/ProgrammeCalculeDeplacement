from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
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
            start_x = self.graph_data["result"]
            end_x = self.graph_data["kv0"]
            start_y = self.graph_data["E0"]
            slope = -1 / self.graph_data["Cc"]
            end_y = start_y + slope * (end_x - start_x)

            x_vals = [start_x, end_x]
            y_vals = [start_y, end_y]

            line, = ax.plot(x_vals, y_vals, marker='o')
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
            start_x = self.graph_data["result"]
            end_x = self.graph_data["kv0"]
            end_y = self.graph_data["E0"]
            slope = 1 / self.graph_data["Ck"]
            start_y = end_y - slope * (end_x - start_x)

            x_vals = [start_x, end_x]
            y_vals = [start_y, end_y]

            line, = ax.plot(x_vals, y_vals, marker='o')
            ax.set_title("Hydraulic Conductivity")
            ax.set_xlabel("Hydraulic Conductivity (kv) [m/s]")
            ax.set_ylabel("Void Ratio (e)")
            ax.set_xscale("log")
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
                    x = x0
                    y = y0
                elif event.xdata > x_max:
                    x = x1
                    y = y1
                else:
                    log_x = np.log10(event.xdata)
                    alpha = (log_x - log_x0) / (log_x1 - log_x0)
                    y = y0 + alpha * (y1 - y0)
                    x = event.xdata
            else:
                if event.xdata < x_min:
                    x = x0
                    y = y0
                elif event.xdata > x_max:
                    x = x1
                    y = y1
                else:
                    alpha = (event.xdata - x0) / (x1 - x0)
                    y = y0 + alpha * (y1 - y0)
                    x = event.xdata

            dot.set_data([x], [y])
            dot.set_visible(True)
            coord_text += f"\nGraph {i + 1}: x = {x:.4g}, y = {y:.4f}"
            updated = True

        if updated:
            self.coord_label.setText(coord_text)
        else:
            self.coord_label.setText("Coordinates:")

        self.canvas.draw_idle()
