import math
from typing import Dict, List, Optional, Tuple, Any

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QHBoxLayout, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class GraphViewer(QWidget):
    """A widget for displaying hydraulic graphs with interactive features."""

    GRAPH_CONFIGS = {
        "stress": {
            "title": "Effective Stress",
            "xlabel": "Effective Stress (σ') [kPa]",
            "ylabel": "Void Ratio (e)",
            "checkbox_label": "Effective Stress"
        },
        "conductivity": {
            "title": "Hydraulic Conductivity",
            "xlabel": "Hydraulic Conductivity (k) [m/s]",
            "ylabel": "Void Ratio (e)",
            "checkbox_label": "Hydraulic Conductivity"
        }
    }

    def __init__(self):
        super().__init__()
        self.graph_data: Optional[Dict[str, float]] = None
        self.follow_dots: List[Any] = []
        self.lines: List[Any] = []
        self.axes: List[Any] = []

        self._init_ui()
        self._setup_canvas()
        self._setup_checkboxes()
        self._setup_coord_label()
        self._connect_signals()
        
        # Style principal pour le widget GraphViewer
        self.setStyleSheet("""
            GraphViewer {
                background-color: #007bff;
                border-radius: 16px;
                padding: 8px;
            }
            
            QLabel {
                color: white;
                font-family: "Segoe UI";
                font-size: 14px;
                font-weight: 500;
            }

            QLabel#coordLabel {
                color: black;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-family: "Segoe UI";
                padding: 4px;
                font-size: 12px;
            }

            QCheckBox {
                color: white;
                font-weight: 500;
                font-size: 14px;
                font-family: "Segoe UI";
                spacing: 6px;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 6px;
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.6);
            }

            QCheckBox::indicator:checked {
                background-color: #ffffff;
                border: 2px solid #ffffff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0iIzAwN2JmZiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }

            QCheckBox::indicator:hover {
                border: 2px solid rgba(255, 255, 255, 0.8);
                background-color: rgba(255, 255, 255, 0.5);
            }

            QCheckBox::indicator:pressed {
                background-color: rgba(255, 255, 255, 0.7);
            }
        """)

    def _init_ui(self) -> None:
        """Initialize the main UI layout."""
        self.layout = QVBoxLayout()
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _setup_canvas(self) -> None:
        """Set up the matplotlib canvas."""
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Container pour le canvas avec coins arrondis
        self.canvas_container = QWidget()
        self.canvas_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #dee2e6;
            }
        """)
        
        canvas_layout = QVBoxLayout(self.canvas_container)
        canvas_layout.setContentsMargins(1, 1, 1, 1)
        canvas_layout.setSpacing(0)
        canvas_layout.addWidget(self.canvas)

    def _setup_checkboxes(self) -> None:
        """Set up the graph selection checkboxes."""
        self.checkbox_stress = QCheckBox(self.GRAPH_CONFIGS["stress"]["checkbox_label"])
        self.checkbox_conductivity = QCheckBox(self.GRAPH_CONFIGS["conductivity"]["checkbox_label"])

        # Create header row
        header_widget = QWidget()
        header_widget.setFixedHeight(35)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 0, 8, 0)
        header_layout.setSpacing(16)
        
        # Label "Show Graphs:"
        show_label = QLabel("Show Graphs:")
        show_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: 600;
                font-size: 14px;
            }
        """)
        
        header_layout.addWidget(show_label)
        
        # Ajouter les checkboxes
        for checkbox in [self.checkbox_stress, self.checkbox_conductivity]:
            checkbox.setChecked(True)  # Cochées par défaut
            header_layout.addWidget(checkbox)
            
        header_layout.addStretch()
        
        # Ajouter le header et le canvas au layout principal
        self.layout.addWidget(header_widget)
        self.layout.addWidget(self.canvas_container)

    def _setup_coord_label(self) -> None:
        """Set up the coordinate display label."""
        self.coord_label = QLabel("Coordinates: x =             y = ")
        self.coord_label.setFixedHeight(28)
        self.coord_label.setObjectName("coordLabel")
        self.coord_label.setStyleSheet("""
            QLabel#coordLabel {
                color: black;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-family: "Segoe UI";
                padding: 4px;
                font-size: 12px;
            }
        """)
        self.coord_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.coord_label)

    def _connect_signals(self) -> None:
        """Connect widget signals to their handlers."""
        self.checkbox_stress.stateChanged.connect(self.update_graph_display)
        self.checkbox_conductivity.stateChanged.connect(self.update_graph_display)
        self.canvas.mpl_connect("motion_notify_event", self.mouse_move)

    def set_graph_data(self, graph_data: Dict[str, float]) -> None:
        """Set the data for the graphs and update the display."""
        self.graph_data = graph_data
        self.update_graph_display()

    def update_graph_display(self) -> None:
        """Update the graph display based on current data and checkbox states."""
        if not self.graph_data:
            return

        self._clear_figure()
        cols = self._get_active_columns()
        pos = 1

        if self.checkbox_stress.isChecked():
            self._plot_stress_graph(pos, cols)
            pos += 1

        if self.checkbox_conductivity.isChecked():
            self._plot_conductivity_graph(pos, cols)

        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()

    def _clear_figure(self) -> None:
        """Clear the figure and reset graph-related lists."""
        self.figure.clear()
        self.follow_dots = []
        self.lines = []
        self.axes = []

    def _get_active_columns(self) -> int:
        """Calculate number of active columns based on checkbox states."""
        return sum([
            self.checkbox_stress.isChecked(),
            self.checkbox_conductivity.isChecked()
        ]) or 1

    def _plot_stress_graph(self, pos: int, cols: int) -> None:
        """Plot the effective stress graph."""
        ax = self.figure.add_subplot(1, cols, pos)
        config = self.GRAPH_CONFIGS["stress"]

        sigma_0 = self.graph_data["sigma_0"]
        sigma_v = self.graph_data["sigma_v"]
        e0 = self.graph_data["e0"]
        cc = self.graph_data["cc"]

        e = e0 - cc * math.log10(sigma_v/sigma_0)
        line, = ax.plot([sigma_0, sigma_v], [e0, e], 'k-', marker='o')

        self._configure_axis(ax, config)
        self._add_graph_elements(ax, line)

    def _plot_conductivity_graph(self, pos: int, cols: int) -> None:
        """Plot the hydraulic conductivity graph."""
        ax = self.figure.add_subplot(1, cols, pos)
        config = self.GRAPH_CONFIGS["conductivity"]

        xf = self.graph_data["kv0"]
        xi = self.graph_data["result"]
        yf = self.graph_data["e0"]
        ck = self.graph_data["ck"]

        yi = yf + ck * math.log10(xi/xf)
        line, = ax.plot([xi, xf], [yi, yf], 'k-', marker='o')

        self._configure_axis(ax, config)
        self._add_graph_elements(ax, line)

    def _configure_axis(self, ax: Any, config: Dict[str, str]) -> None:
        """Configure the axis with titles and grid."""
        ax.set_title(config["title"], pad=10)
        ax.set_xlabel(config["xlabel"], labelpad=8)
        ax.set_ylabel(config["ylabel"], labelpad=8)
        ax.grid(True, alpha=0.3)

    def _add_graph_elements(self, ax: Any, line: Any) -> None:
        """Add the line and follow dot to the tracking lists."""
        self.lines.append(line)
        self.axes.append(ax)
        self.follow_dots.append(ax.plot([], [], 'ro')[0])

    def mouse_move(self, event: Any) -> None:
        """Handle mouse movement over the graphs."""
        if not self._is_valid_mouse_event(event):
            self._reset_coordinate_display()
            return

        self._update_coordinate_display(event)

    def _is_valid_mouse_event(self, event: Any) -> bool:
        """Check if the mouse event is valid for coordinate tracking."""
        return event.inaxes is not None and event.xdata is not None

    def _reset_coordinate_display(self) -> None:
        """Reset the coordinate display to default state."""
        self.coord_label.setText("Coordinates: x =             y = ")
        for dot in self.follow_dots:
            dot.set_visible(False)
        self.canvas.draw_idle()

    def _update_coordinate_display(self, event: Any) -> None:
        """Update the coordinate display based on mouse position."""
        updated = False

        for line, ax, dot in zip(self.lines, self.axes, self.follow_dots):
            if event.inaxes != ax:
                dot.set_visible(False)
                continue

            x, y = self._calculate_point_on_line(event, line, ax)
            if x is not None and y is not None:
                dot.set_data([x], [y])
                dot.set_visible(True)
                x_str = f"{x:.4g}".ljust(12)
                self.coord_label.setText(f"Coordinates: x = {x_str}  y = {y:.4f}")
                updated = True
                break

        if not updated:
            self.coord_label.setText("Coordinates: x = --            y = --")
        self.canvas.draw_idle()

    def _calculate_point_on_line(self, event: Any, line: Any, ax: Any) -> Tuple[Optional[float], Optional[float]]:
        """Calculate the point on the line closest to the mouse position."""
        xdata = line.get_xdata()
        ydata = line.get_ydata()

        if len(xdata) != 2 or len(ydata) != 2:
            return None, None

        x0, x1 = xdata
        y0, y1 = ydata
        x_min, x_max = sorted([x0, x1])

        if ax.get_xscale() == "log":
            return self._calculate_log_scale_point(event.xdata, x0, x1, y0, y1, x_min, x_max)
        return self._calculate_linear_scale_point(event.xdata, x0, x1, y0, y1, x_min, x_max)

    def _calculate_log_scale_point(self, x: float, x0: float, x1: float, y0: float, y1: float,
                                 x_min: float, x_max: float) -> Tuple[float, float]:
        """Calculate point coordinates for logarithmic scale."""
        if x < x_min:
            return x0, y0
        if x > x_max:
            return x1, y1

        log_x0, log_x1 = np.log10(x0), np.log10(x1)
        log_x = np.log10(x)
        alpha = (log_x - log_x0) / (log_x1 - log_x0)
        y = y0 + alpha * (y1 - y0)
        return x, y

    def _calculate_linear_scale_point(self, x: float, x0: float, x1: float, y0: float, y1: float,
                                    x_min: float, x_max: float) -> Tuple[float, float]:
        """Calculate point coordinates for linear scale."""
        if x < x_min:
            return x0, y0
        if x > x_max:
            return x1, y1

        alpha = (x - x0) / (x1 - x0)
        y = y0 + alpha * (y1 - y0)
        return x, y

    def clear_graph(self) -> None:
        """Clear all graph data and reset the display."""
        self.graph_data = None
        self.figure.clear()
        self.canvas.draw()
        self.lines.clear()
        self.axes.clear()
        self.follow_dots.clear()
        self.coord_label.setText("Coordinates: x =             y = ")