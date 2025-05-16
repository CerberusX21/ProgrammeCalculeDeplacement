from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QLabel, QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QFormLayout, QGroupBox, QCheckBox, QSlider, QTabWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys

from FormulaClay import FormulaClay
from FormulaD50ff import FormulaD50ff
from FormulaLiquid import FormulaLiquid
from formule_ei_tassement import EI_Tassement
from formule_ip_ir_tassement import ClassificationSol
from formule_cc_tassement import CalculCcStar
from formule_e0_tassement import CalculE0Tassement
from formule_sigma0 import CalculSigma0
from formule_calculer_tassement import CalculTassements
from formule_indice_des_vides import CalculIndiceDesVides

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soil Analysis Tool")
        self.resize(1200, 500)

        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                color: #212529;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-weight: 600;
                color: #333;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 6px 30px 6px 10px;
                min-width: 120px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0d6efd;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border-left: 1px solid #ced4da;
                background-color: #f1f1f1;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: url(":/qt-project.org/styles/commonstyle/images/arrowdown-16.png");
                margin-right: 6px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
            QLabel#ResultLabel {
                background-color: #ffffff;
                border: 1px solid #0d6efd;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
                color: #0d6efd;
                min-height: 40px;
                max-height: 100px;
                qproperty-alignment: 'AlignLeft';
            }
        """)

        self.master_layout = QVBoxLayout()
        self.master_layout.setSpacing(15)
        self.master_layout.setContentsMargins(40, 30, 40, 30)

        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()

        self.tabs = QTabWidget()

        self.hydraulique_tab = QWidget()
        hydraulique_form = QFormLayout()

        self.type_sol_input = QLineEdit()
        self.type_sol_input.setPlaceholderText("Valeur...")
        self.type_sol = QComboBox()
        self.type_sol.addItems(["clay%", "wL", "d50ff"])

        self.pores_input = QLineEdit()
        self.pores_input.setPlaceholderText("Valeur...")
        self.pores_sol = QComboBox()
        self.pores_sol.addItems(["W", "ρf"])

        self.compress_input = QLineEdit()
        self.compress_input.setPlaceholderText("Valeur...")
        self.compress_sol = QComboBox()
        self.compress_sol.addItems(["σ′v"])

        self.density_input = QLineEdit()
        self.density_input.setPlaceholderText("Valeur...")

        hydraulique_form.addRow("Type de sol :", self._wrap(self.type_sol_input, self.type_sol))
        hydraulique_form.addRow("Type de pores :", self._wrap(self.pores_input, self.pores_sol))
        hydraulique_form.addRow("Compression :", self._wrap(self.compress_input, self.compress_sol))
        hydraulique_form.addRow("Type Gs :", self.density_input)

        self.hydraulique_tab.setLayout(hydraulique_form)

        self.tassement_tab = QWidget()
        tassement_form = QFormLayout()
        self.tassement_tab.setLayout(tassement_form)

        # Champs pour le calcul de ei*
        self.entree_pore_tassement = QLineEdit()
        self.entree_pore_tassement.setPlaceholderText("Valeur du paramètre de pore")

        self.type_pore_tassement = QComboBox()
        self.type_pore_tassement.addItem("Teneur en eau w (kg/kg)", "w")
        self.type_pore_tassement.addItem("Masse volumique ρf (g/cm³)", "ρf")
        self.type_pore_tassement.addItem("Indice des vides ef", "ef")

        self.entree_gs_tassement = QLineEdit()
        self.entree_gs_tassement.setPlaceholderText("Densité spécifique Gs")

        #Ajout du type de sol pour le tassement
        self.entree_type_sol_valeur = QLineEdit()
        self.entree_type_sol_valeur.setPlaceholderText("Valeur du type de sol")

        self.entree_type_sol_type = QComboBox()
        self.entree_type_sol_type.addItems(["clay%", "wL", "d50ff"])

        tassement_form.addRow("Type de sol :", self._wrap(self.entree_type_sol_valeur, self.entree_type_sol_type))

        # Case à cocher pour le calcul automatique de Cc*
        self.checkbox_cc_auto = QCheckBox("Calculer automatiquement Cc*")
        self.checkbox_cc_auto.setChecked(True)
        self.checkbox_cc_auto.stateChanged.connect(self.toggle_cc_input)

        # Champ modifiable (visible seulement si décoché)
        self.cc_input = QLineEdit()
        self.cc_input.setPlaceholderText("Entrez manuellement Cc*")

        self.cc_label = QLabel("Cc*:")

        # Masquer au début
        self.cc_input.setVisible(False)
        self.cc_label.setVisible(False)

        # Ajouter dans le formulaire
        tassement_form.addRow(self.checkbox_cc_auto)
        tassement_form.addRow(self.cc_label, self.cc_input)

        # (σ′v)
        self.entree_sigma_v = QLineEdit()
        self.entree_sigma_v.setPlaceholderText("Valeur de σ′v")
        self.label_sigma_v = QLabel("Contrainte verticale σ′ᵥ (kPa) :")

        # Ajout au layout de l'onglet Tassement
        tassement_form.addRow("Type de pore :", self._wrap(self.entree_pore_tassement, self.type_pore_tassement))
        tassement_form.addRow("Densité Gs :", self.entree_gs_tassement)
        tassement_form.addRow(self.label_sigma_v, self.entree_sigma_v)

        
        
        
        self.tabs.addTab(self.hydraulique_tab, "Conductivité hydraulique")
        self.tabs.addTab(self.tassement_tab, "Tassement")

        self.result_label = QLabel("Résultat :")
        self.result_label.setObjectName("ResultLabel")

        self.calculate_button = QPushButton("Calculer")
        self.calculate_button.clicked.connect(self.calculate)

        self.button_row = QHBoxLayout()
        self.button_row.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.button_row.addWidget(self.calculate_button)
        self.button_row.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.col1.addWidget(self.tabs)
        self.col1.addLayout(self.button_row)
        self.col1.addWidget(self.result_label)

        self.col2.addWidget(self.canvas)

        row_layout = QHBoxLayout()
        row_layout.addLayout(self.col1, 30)
        row_layout.addLayout(self.col2, 70)

        self.master_layout.addLayout(row_layout)
        self.setLayout(self.master_layout)

    # Fonctions

    def _wrap(self, widget1, widget2):
        row = QHBoxLayout()
        row.addWidget(widget1)
        row.addWidget(widget2)
        row.setStretch(0, 1)
        row.setStretch(1, 1)
        container = QWidget()
        container.setLayout(row)
        return container

    def calculate(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            self.calculate_hydraulique()
        elif current_tab == 1:
            self.calculate_tassement()

    def calculate_tassement(self):
        
            # --- Entrées utilisateur ---
            valeur_pore = float(self.entree_pore_tassement.text())
            Gs = float(self.entree_gs_tassement.text())
            type_pore = self.type_pore_tassement.currentData()

            valeur_sol = float(self.entree_type_sol_valeur.text())
            type_sol = self.entree_type_sol_type.currentText()

            # --- Calcul de ei* ---
            ei_star = EI_Tassement(valeur_pore, Gs, type_pore).calculer()
           

            # --- Calcul de ef (indice des vides gelé) ---
            if type_pore == "ef":
                ef = valeur_pore  # utilisateur a fourni ef
            else:
                ef = ei_star * 1.09  # déduit à partir de ei*

            # --- Classification Ice-Rich / Ice-Poor ---
            classification = ClassificationSol(ei_star, valeur_sol, type_sol)
            code_etat = classification.classer()
          

            # --- Cc* (automatique ou manuel) ---
            if self.checkbox_cc_auto.isChecked():
                cc_star = CalculCcStar(ei_star, valeur_sol, type_sol, code_etat).calculer()
                self.cc_input.setText(f"{cc_star:.6f}")
              
            else:
                try:
                    cc_star = float(self.cc_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Erreur", "Veuillez entrer une valeur numérique valide pour Cc*.")
                    return

            # --- Calcul de e₀* ---
            e0_star = CalculE0Tassement(ei_star, cc_star, code_etat).calculer()
           

            # --- Calcul de σ′₀ ---
            sigma0 = CalculSigma0(e0_star, type_sol, valeur_sol, code_etat).calculer()
          

            # ---  σ′ᵥ ---
            try:
                sigma_v = float(self.entree_sigma_v.text())
            except ValueError:
                QMessageBox.warning(self, "Erreur", "Veuillez entrer une valeur numérique valide pour σ′ᵥ.")
                return

            # --- Calcul de l'indice des vides final ---
            indice_vides = CalculIndiceDesVides(e0_star, cc_star, sigma_v, sigma0).calculer()

            # --- Calcul des tassements ---
            s1, s2, s_total = CalculTassements(ef, e0_star, indice_vides).calculer()

            # --- Affichage final ---
            self.result_label.setText(
                f"Tassement total S = {s_total:.2f} %\n"
                f"Tassement S1 (fonte de glace) = {s1:.2f} %\n"
                f"Tassement S2 (compression) = {s2:.2f} %"
            )

       


    def calculate_hydraulique(self):
        try:
            data = {
                'type_sol': float(self.type_sol_input.text()),
                'pores_sol': float(self.pores_input.text()),
                'compress_sol': float(self.compress_input.text()),
                'density_sol': float(self.density_input.text()),
                'water': self.pores_sol.currentText() == "W",
                'type': self.type_sol.currentText()
            }
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs numériques valides.")
            return

        formulas = {
            "clay%": FormulaClay(),
            "wL": FormulaLiquid(),
            "d50ff": FormulaD50ff()
        }

        formula = formulas.get(data['type'])

        try:
            result = formula.calculate(
                data['type_sol'], data['pores_sol'],
                data['compress_sol'], data['density_sol'],
                data['water']
            )
            self.result_label.setText(f"Résultat :  {result}")
        except ValueError as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur de calcul de formula non valide.\n {e}")


    def toggle_cc_input(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        self.cc_input.setVisible(not is_checked)
        self.cc_label.setVisible(not is_checked)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    window = Window()
    window.show()
    sys.exit(app.exec())
