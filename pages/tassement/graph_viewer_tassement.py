from typing import Dict, List, Optional, Tuple, Any

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QHBoxLayout, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import math


class GraphViewer(QWidget):
    """A widget for displaying settlement graphs with interactive features."""

    GRAPH_CONFIG = {
        "title": "Void Ratio vs Effective Stress",
        "xlabel": "Effective Stress (σ') [kPa]",
        "ylabel": "Void Ratio (e)",
        "checkbox_label": "Effective Stress"
    }

    def __init__(self):
        super().__init__()
        self.graph_data: Optional[Dict[str, float]] = None
        self.ei_value: Optional[float] = None
        self.is_tassement: bool = False
        self.follow_dots: List[Any] = []
        self.lines: List[Any] = []
        self.axes: List[Any] = []

        self._init_ui()
        self._setup_canvas()
        self._setup_checkboxes()
        self._setup_coord_label()
        self._connect_signals()
        
        # Style principal pour le widget GraphViewer - identique à l'hydraulique
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
        
        # Container pour le canvas avec coins arrondis - identique à l'hydraulique
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
        self.checkbox_stress = QCheckBox(self.GRAPH_CONFIG["checkbox_label"])

        # Create header row - identique à l'hydraulique
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
        
        # Ajouter la checkbox (cochée par défaut)
        self.checkbox_stress.setChecked(True)
        header_layout.addWidget(self.checkbox_stress)
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
        self.canvas.mpl_connect("motion_notify_event", self.mouse_move)

    def set_graph_data(self, graph_data: Dict[str, float]) -> None:
        """Set the data for the graph and update the display."""
        self.graph_data = graph_data
        self.update_graph_display()

    def set_ei_value(self, value: Optional[float]) -> None:
        """Set the initial void ratio value and update display if needed."""
        self.ei_value = value
        if self.graph_data:
            self.update_graph_display()

    def set_is_tassement(self, is_tassement: bool) -> None:
        """Set the settlement mode and update display if needed."""
        self.is_tassement = is_tassement
        if self.graph_data:
            self.update_graph_display()

    def update_graph_display(self) -> None:
        """Update the graph display based on current data and checkbox state."""
        if not self.graph_data or not self.checkbox_stress.isChecked():
            self._clear_figure()
            self.canvas.draw()
            return

        self._clear_figure()
        self._plot_stress_graph()
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()

    def _clear_figure(self) -> None:
        """Clear the figure and reset graph-related lists."""
        self.figure.clear()
        self.follow_dots = []
        self.lines = []
        self.axes = []

    def _plot_stress_graph(self) -> None:
        """Plot the effective stress graph with settlement data."""
        ax = self.figure.add_subplot(1, 1, 1)

        # Extract data points
        sigma0 = self.graph_data.get("sigma0", 20)
        sigma_v = self.graph_data.get("sigma_v", 100)
        e0_star = self.graph_data["E0"]
        cc_star = self.graph_data["Cc"]

        # Calculate plot range
        x_min = sigma0
        x_max = sigma_v * 1.5
        x_vals = np.logspace(np.log10(x_min), np.log10(x_max), 200)
        x_display_min = max(0.1, sigma0 * 0.1)

        # Calculate void ratio values
        y_vals = [e0_star - cc_star * math.log10(s / sigma0) for s in x_vals]
        y_vals = np.clip(y_vals, 0.01, 5)

        # Plot main curve
        line1, = ax.plot(x_vals, y_vals, color='blue', linewidth=2)
        self._configure_axis(ax)
        self._set_axis_limits(ax, x_display_min, x_max, e0_star)
        self._add_graph_elements(ax, line1)

        # Add settlement-specific points and annotations
        self._add_settlement_points(ax, sigma0, sigma_v, e0_star, cc_star)

    def _configure_axis(self, ax: Any) -> None:
        """Configure the axis with titles and grid."""
        ax.set_title(self.GRAPH_CONFIG["title"], pad=10)
        ax.set_xlabel(self.GRAPH_CONFIG["xlabel"], labelpad=8)
        ax.set_ylabel(self.GRAPH_CONFIG["ylabel"], labelpad=8)
        ax.set_xscale("log")
        ax.grid(True, alpha=0.3)

    def _set_axis_limits(self, ax: Any, x_min: float, x_max: float, e0_star: float) -> None:
        """Set the axis limits for the plot."""
        ax.set_xlim(left=x_min, right=x_max)
        y_max = e0_star + 0.5
        if self.ei_value is not None:
            y_max = max(y_max, self.ei_value + 0.3)
        ax.set_ylim(bottom=0, top=y_max)

    def _add_graph_elements(self, ax: Any, line: Any) -> None:
        """Add the line and follow dot to the tracking lists."""
        self.lines.append(line)
        self.axes.append(ax)
        self.follow_dots.append(ax.plot([], [], 'ro')[0])

    def _add_settlement_points(self, ax: Any, sigma0: float, sigma_v: float, 
                             e0_star: float, cc_star: float) -> None:
        """Add settlement-specific points and annotations to the graph."""
        # Add initial point
        ax.plot(sigma0, e0_star, 'bo', markersize=8)
        ax.text(sigma0, e0_star + 0.05, f"(σ₀={sigma0:.1f}, e₀={e0_star:.3f})", 
                color='black', fontweight='bold', ha='center')

        # Add ei point if in settlement mode
        if self.is_tassement and self.ei_value is not None:
            self._add_ei_point(ax, sigma0, e0_star)

        # Add final point if sigma_v is valid
        if sigma_v > 0:
            self._add_final_point(ax, sigma0, sigma_v, e0_star, cc_star)

    def _add_ei_point(self, ax: Any, sigma0: float, e0_star: float) -> None:
        """Add the initial void ratio point to the graph."""
        if abs(self.ei_value - e0_star) < 0.001:
            # ei ≈ e0: point on the curve at sigma0
            ax.plot(sigma0, self.ei_value, 'go', markersize=8)
            ax.text(sigma0 * 1.2, self.ei_value, f"eᵢ={self.ei_value:.3f}", 
                    color='black', fontweight='bold', ha='left')
        else:
            # ei ≠ e0: dotted vertical line from e0 to ei
            ax.plot([sigma0, sigma0], [e0_star, self.ei_value], 
                   color='black', linestyle=':', linewidth=2)
            ax.plot(sigma0, self.ei_value, 'go', markersize=8)
            ax.text(sigma0 * 1.2, self.ei_value, f"eᵢ={self.ei_value:.3f}", 
                    color='black', fontweight='bold', ha='left')

    def _add_final_point(self, ax: Any, sigma0: float, sigma_v: float, 
                        e0_star: float, cc_star: float) -> None:
        """Add the final point to the graph."""
        e_final = e0_star - cc_star * math.log10(sigma_v / sigma0)
        if 0 < e_final < 5:
            ax.plot(sigma_v, e_final, 'ro', markersize=8)
            ax.text(sigma_v, e_final - 0.1, f"(σᵥ={sigma_v:.1f}, e={e_final:.3f})", 
                    color='black', fontweight='bold', ha='center')

    def mouse_move(self, event: Any) -> None:
        """Handle mouse movement over the graph."""
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

            xdata = line.get_xdata()
            ydata = line.get_ydata()

            if len(xdata) < 2 or len(ydata) < 2:
                dot.set_visible(False)
                continue

            distances = np.abs(xdata - event.xdata)
            index = distances.argmin()
            x = xdata[index]
            y = ydata[index]

            dot.set_data([x], [y])
            dot.set_visible(True)
            x_str = f"{x:.4g}".ljust(12)
            self.coord_label.setText(f"Coordinates: x = {x_str}  y = {y:.4f}")
            updated = True

        if not updated:
            self.coord_label.setText("Coordinates: x =             y = ")
        self.canvas.draw_idle()

    def clear_graph(self) -> None:
        """Clear all graph data and reset the display."""
        self.graph_data = None
        self.figure.clear()
        self.canvas.draw()
        self.lines.clear()
        self.axes.clear()
        self.follow_dots.clear()
        self.coord_label.setText("Coordinates: x =             y = ")