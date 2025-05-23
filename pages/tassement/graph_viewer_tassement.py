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
        print(f"[DEBUG] Valeurs reçues : Ck={graph_data.get('Ck')}, Cc={graph_data.get('Cc')}, E0={graph_data.get('E0')}, kv0={graph_data.get('kv0')}")
        self.update_graph_display()

    def set_ei_value(self, value):
        self.ei_value = value

    def set_is_tassement(self, is_tassement: bool):
        self.is_tassement = is_tassement

    def update_graph_display(self):
        if not self.graph_data:
            return

        self.figure.clear()
        self.follow_dots = []
        self.lines = []
        self.axes = []

        # Détermine combien de graphiques afficher
        show_stress = self.checkbox_stress.isChecked()
        show_conductivity = self.checkbox_conductivity.isChecked()
        
        if not show_stress and not show_conductivity:
            self.canvas.draw()
            return
            
        cols = sum([show_stress, show_conductivity])
        pos = 1

        # Variables communes
        try:
            sigma0 = self.graph_data.get("sigma0", self.graph_data.get("result", 20))
            sigma_v = self.graph_data.get("sigma_v", self.graph_data.get("kv0", 100))
            e0_star = self.graph_data["E0"]
            cc_star = self.graph_data["Cc"]
        except KeyError as e:
            print(f"GraphViewer: Donnée manquante: {e}")
            return

        # -------- Courbe 1 (Effective stress)--------
        if show_stress:
            ax1 = self.figure.add_subplot(1, cols, pos)
            pos += 1
          
            x_vals = np.logspace(np.log10(max(sigma0 * 0.1, 1)), np.log10(sigma_v * 2), 200)
            # FORMULE : e = e0* - Cc* * log10(σ'/σ0) [SIGNE NÉGATIF]
            y_vals = [e0_star - cc_star * math.log10(s / sigma0) for s in x_vals]
            y_vals = np.clip(y_vals, 0.01, 5)

            line1, = ax1.plot(x_vals, y_vals, label="e vs σ'", color='blue', linewidth=2)
            ax1.set_title("Void Ratio vs Effective Stress")
            ax1.set_xlabel("Effective Stress (σ') [kPa]")
            ax1.set_ylabel("Void Ratio (e)")
            ax1.set_xscale("log")
            ax1.set_xlim(left=max(sigma0 * 0.1, 1), right=sigma_v * 2)
            ax1.set_ylim(bottom=0, top=e0_star + 0.5)
            ax1.grid(True, alpha=0.3)

            # Point de projection pour σ'v
            if sigma_v > 0:
                e_at_sigma_v = e0_star - cc_star * math.log10(sigma_v / sigma0)
                if 0 < e_at_sigma_v < 5:
                    # Ligne verticale de projection
                    ax1.axvline(x=sigma_v, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
                    # Point sur la courbe
                    ax1.plot(sigma_v, e_at_sigma_v, 'ro', markersize=8)
                    # Ligne horizontale pour projection vers le deuxième graphique
                    ax1.axhline(y=e_at_sigma_v, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
                    
                    # Affichage de la valeur σ'v
                    ax1.text(sigma_v, ax1.get_ylim()[1] * 0.9, f"σ'v = {sigma_v:.1f} kPa", 
                            color='red', fontweight='bold', ha='center', 
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

            self.lines.append(line1)
            self.axes.append(ax1)
            self.follow_dots.append(ax1.plot([], [], 'ro')[0])

        # -------- Courbe 2  (Hydraulic Conductivity)  --------
        if show_conductivity:
            # Vérifier les données nécessaires
            required_keys = ["kv0", "result"]
            if not all(k in self.graph_data for k in required_keys):
                print("GraphViewer: Données manquantes pour conductivité hydraulique.")
                if show_stress:
                    self.canvas.draw()
                return

            kv0 = self.graph_data["kv0"]
            kv_result = self.graph_data["result"]
            ck_star = self.graph_data.get("Ck", cc_star)

            ax2 = self.figure.add_subplot(1, cols, pos)
            
            # CORRECTION : COURBE POSITIVE selon votre document
            # Plus kv est grand, plus e est grand (relation positive)
            kv_min = max(kv0 * 0.001, 1e-12)
            kv_max = min(kv0 * 1000, 1e-3)
            x_vals = np.logspace(np.log10(kv_min), np.log10(kv_max), 200)
            
            # FORMULE CORRIGÉE : e = e0* + Ck* * log10(kv/kv0) [SIGNE POSITIF]
            y_vals = [e0_star + ck_star * math.log10(k / kv0) for k in x_vals]
            y_vals = np.clip(y_vals, 0.01, e0_star + 2)

            line2, = ax2.plot(x_vals, y_vals, label="e vs kv", color='green', linewidth=2)
            ax2.set_title("Void Ratio vs Hydraulic Conductivity")
            ax2.set_xlabel("Hydraulic Conductivity (kv) [m/s]")
            ax2.set_ylabel("Void Ratio (e)")
            ax2.set_xscale("log")
            ax2.set_xlim(left=kv_min, right=kv_max)
            ax2.set_ylim(bottom=0, top=e0_star + 2)
            ax2.grid(True, alpha=0.3)

       
            if show_stress and sigma_v > 0:
               
                e_at_sigma_v = e0_star - cc_star * math.log10(sigma_v / sigma0)
                
                if 0 < e_at_sigma_v < e0_star + 2:
                    
                    ax2.axhline(y=e_at_sigma_v, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
                    
                   
                    # Depuis e = e0* + Ck* * log10(kv*/kv0)
                    # Donc : kv* = kv0 * 10^((e - e0*) / Ck*)
                    exponent = (e_at_sigma_v - e0_star) / ck_star
                    kv_star = kv0 * (10 ** exponent)
                    
                    
                    if kv_min <= kv_star <= kv_max:
                        # 4. Ligne verticale vers kv*
                        ax2.axvline(x=kv_star, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
                        # Point sur la courbe
                        ax2.plot(kv_star, e_at_sigma_v, 'ro', markersize=8)
                        
                        # 5. Affichage de la valeur kv*
                        ax2.text(kv_star, ax2.get_ylim()[0] + (ax2.get_ylim()[1] - ax2.get_ylim()[0]) * 0.1, 
                                f"kv* = {kv_star:.2e} m/s", 
                                color='red', fontweight='bold', ha='center', rotation=90,
                                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

            # Marquer les points de référence
            # Point kv0, e0*
            if kv_min <= kv0 <= kv_max:
                ax2.plot(kv0, e0_star, 'go', markersize=6, alpha=0.7)
                ax2.text(kv0 * 1.1, e0_star, f"kv0 = {kv0:.2e}\ne0* = {e0_star:.3f}", 
                        color='green', fontsize=8, va='center',
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgreen", alpha=0.7))

            self.lines.append(line2)
            self.axes.append(ax2)
            self.follow_dots.append(ax2.plot([], [], 'ro')[0])
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