from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import math

class GraphViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.graph_data = None
        self.ei_value = None
        self.is_tassement = False

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.checkbox_stress = QCheckBox("Effective Stress")
        self.show_row = QHBoxLayout()

        # Configuration des checkboxes
        self.checkbox_stress.setChecked(True)
        self.checkbox_stress.stateChanged.connect(self.update_graph_display)

        layout = QVBoxLayout()
        self.show_row.addWidget(QLabel("Show Graphs:"))
        self.show_row.addWidget(self.checkbox_stress)
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

    def set_ei_value(self, value):
        self.ei_value = value
        # Redessiner le graphique si les données sont déjà disponibles
        if self.graph_data:
            self.update_graph_display()

    def set_is_tassement(self, is_tassement: bool):
        self.is_tassement = is_tassement
        # Redessiner le graphique si nécessaire
        if self.graph_data:
            self.update_graph_display()

    def update_graph_display(self):
        if not self.graph_data:
            return

        self.figure.clear()
        self.follow_dots = []
        self.lines = []
        self.axes = []

        # Détermine combien de graphiques afficher
        show_stress = self.checkbox_stress.isChecked()
        
        if not show_stress:
            self.canvas.draw()
            return
            
        cols = 1  # Seulement le graphique de effective stress
        pos = 1

        # Variables communes
        try:
            sigma0 = self.graph_data.get("sigma0", 20)  # Contrainte initiale
            sigma_v = self.graph_data.get("sigma_v", 100)  # Contrainte finale
            e0_star = self.graph_data["E0"]  # Indice des vides initial
            cc_star = self.graph_data["Cc"]  # Coefficient de compression
        except KeyError as e:
            return

        # -------- Courbe Effective stress --------
        if show_stress:
            ax1 = self.figure.add_subplot(1, cols, pos)
          
            # Définir la plage d'x : commencer à sigma0, aller jusqu'à sigma_v * 1.5
            x_min = sigma0  # La courbe commence à sigma0
            x_max = sigma_v * 1.5
            x_vals = np.logspace(np.log10(x_min), np.log10(x_max), 200)
            
            # Définir les limites d'affichage de l'axe (peut commencer à 0 ou une valeur plus faible)
            x_display_min = max(0.1, sigma0 * 0.1)  # Pour l'affichage de l'axe
            
            # FORMULE : e = e0* - Cc* * log10(σ'/σ0)
            # Le point (sigma0, e0*) est sur la courbe
            # Le point (sigma_v, e_final) est aussi sur la courbe
            y_vals = [e0_star - cc_star * math.log10(s / sigma0) for s in x_vals]
            y_vals = np.clip(y_vals, 0.01, 5)

            line1, = ax1.plot(x_vals, y_vals, color='blue', linewidth=2)
            ax1.set_title("Void Ratio vs Effective Stress")
            ax1.set_xlabel("Effective Stress (σ') [kPa]")
            ax1.set_ylabel("Void Ratio (e)")
            ax1.set_xscale("log")
            ax1.set_xlim(left=x_display_min, right=x_max)
            
            # Calculer la valeur maximale pour l'axe Y
            y_max = e0_star + 0.5
            if self.ei_value is not None:
                y_max = max(y_max, self.ei_value + 0.3)
            ax1.set_ylim(bottom=0, top=y_max)
            ax1.grid(True, alpha=0.3)

            # Affichage du point ei si on est en mode tassement et que ei est défini
            if self.is_tassement and self.ei_value is not None:
                if abs(self.ei_value - e0_star) < 0.001:
                    # ei ≈ e0 : point sur la courbe à sigma0
                    ax1.plot(sigma0, self.ei_value, 'go', markersize=8)
                    ax1.text(sigma0 * 1.2, self.ei_value, f"eᵢ={self.ei_value:.3f}", 
                            color='black', fontweight='bold', ha='left')
                else:
                    # ei ≠ e0 : ligne pointillée verticale depuis e0 jusqu'à ei
                    ax1.plot([sigma0, sigma0], [e0_star, self.ei_value], color='black', linestyle=':', linewidth=2)
                    ax1.plot(sigma0, self.ei_value, 'go', markersize=8)
                    ax1.text(sigma0 * 1.2, self.ei_value, f"eᵢ={self.ei_value:.3f}", 
                            color='black', fontweight='bold', ha='left')

            # Point de départ : (sigma0, e0)
            ax1.plot(sigma0, e0_star, 'bo', markersize=8)
            ax1.text(sigma0, e0_star + 0.05, f"(σ₀={sigma0:.1f}, e₀={e0_star:.3f})", 
                    color='black', fontweight='bold', ha='center')

            # Point final : (sigma_v, e_final)
            if sigma_v > 0:
                e_final = e0_star - cc_star * math.log10(sigma_v / sigma0)
                if 0 < e_final < 5:
                    # Point sur la courbe
                    ax1.plot(sigma_v, e_final, 'ro', markersize=8)
                
                    
                    # Affichage des valeurs
                    ax1.text(sigma_v, e_final - 0.1, f"(σᵥ={sigma_v:.1f}, e={e_final:.3f})", 
                            color='black', fontweight='bold', ha='center')

            self.lines.append(line1)
            self.axes.append(ax1)
            self.follow_dots.append(ax1.plot([], [], 'ro')[0])
        
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

            if len(xdata) < 2 or len(ydata) < 2:
                dot.set_visible(False)
                continue

            distances = np.abs(xdata - event.xdata)
            index = distances.argmin()
            x = xdata[index]
            y = ydata[index]

            dot.set_data([x], [y])
            dot.set_visible(True)
            coord_text += f"\nGraph {i + 1}: x = {x:.4g}, y = {y:.4f}"
            updated = True

        self.coord_label.setText(coord_text if updated else "Coordinates:")
        self.canvas.draw_idle()

    def clear_graph(self):
        self.graph_data = None
        self.figure.clear()
        self.canvas.draw_idle()
        self.coord_label.setText("Coordinates:")
        self.follow_dots = []
        self.lines = []
        self.axes = []