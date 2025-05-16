from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox, QLabel, QCheckBox, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

from formulas.tassement.formule_ei_tassement import EI_Tassement
from formulas.tassement.formule_ip_ir_tassement import ClassificationSol
from formulas.tassement.formule_cc_tassement import CalculCcStar
from formulas.tassement.formule_e0_tassement import CalculE0Tassement
from formulas.tassement.formule_sigma0 import CalculSigma0
from formulas.tassement.formule_calculer_tassement import CalculTassements
from formulas.tassement.formule_indice_des_vides import CalculIndiceDesVides

class TassementPage(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)

        self.entree_pore_tassement = QLineEdit()
        self.entree_pore_tassement.setPlaceholderText("Valeur du paramètre de pore")

        self.type_pore_tassement = QComboBox()
        self.type_pore_tassement.addItem("Teneur en eau w (kg/kg)", "w")
        self.type_pore_tassement.addItem("Masse volumique ρf (g/cm³)", "ρf")
        self.type_pore_tassement.addItem("Indice des vides ef", "ef")

        self.entree_gs_tassement = QLineEdit()
        self.entree_gs_tassement.setPlaceholderText("Densité spécifique Gs")

        self.entree_type_sol_valeur = QLineEdit()
        self.entree_type_sol_valeur.setPlaceholderText("Valeur du type de sol")

        self.entree_type_sol_type = QComboBox()
        self.entree_type_sol_type.addItems(["clay%", "wL", "d50ff"])

        layout.addRow("Type de sol :", self._wrap(self.entree_type_sol_valeur, self.entree_type_sol_type))
        layout.addRow("Type de pore :", self._wrap(self.entree_pore_tassement, self.type_pore_tassement))
        layout.addRow("Densité Gs :", self.entree_gs_tassement)

        self.checkbox_cc_auto = QCheckBox("Calculer automatiquement Cc*")
        self.checkbox_cc_auto.setChecked(True)
        self.checkbox_cc_auto.stateChanged.connect(self.toggle_cc_input)

        self.cc_input = QLineEdit()
        self.cc_input.setPlaceholderText("Entrez manuellement Cc*")

        self.cc_label = QLabel("Cc*:")
        self.cc_input.setVisible(False)
        self.cc_label.setVisible(False)

        layout.addRow(self.checkbox_cc_auto)
        layout.addRow(self.cc_label, self.cc_input)

        self.entree_sigma_v = QLineEdit()
        self.entree_sigma_v.setPlaceholderText("Valeur de σ′v")
        self.label_sigma_v = QLabel("Contrainte verticale σ′ᵥ (kPa) :")
        layout.addRow(self.label_sigma_v, self.entree_sigma_v)

    def _wrap(self, widget1, widget2):
        row = QHBoxLayout()
        row.addWidget(widget1)
        row.addWidget(widget2)
        row.setStretch(0, 1)
        row.setStretch(1, 1)
        container = QWidget()
        container.setLayout(row)
        return container

    def calculate(self, result_label):
        try:
            valeur_pore = float(self.entree_pore_tassement.text())
            Gs = float(self.entree_gs_tassement.text())
            type_pore = self.type_pore_tassement.currentData()
            valeur_sol = float(self.entree_type_sol_valeur.text())
            type_sol = self.entree_type_sol_type.currentText()
            sigma_v = float(self.entree_sigma_v.text())
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer toutes les valeurs numériques valides.")
            return

        ei_star = EI_Tassement(valeur_pore, Gs, type_pore).calculer()
        ef = valeur_pore if type_pore == "ef" else ei_star * 1.09

        classification = ClassificationSol(ei_star, valeur_sol, type_sol)
        code_etat = classification.classer()

        if self.checkbox_cc_auto.isChecked():

            cc_star = CalculCcStar(ei_star, valeur_sol, type_sol, code_etat).calculer()
            print("here")
            self.cc_input.setText(f"{cc_star:.6f}")
        else:
            try:
                cc_star = float(self.cc_input.text())
            except ValueError:
                QMessageBox.warning(self, "Erreur", "Veuillez entrer une valeur numérique valide pour Cc*.")
                return

        print("hello")

        e0_star = CalculE0Tassement(ei_star, cc_star, code_etat).calculer()
        sigma0 = CalculSigma0(e0_star, type_sol, valeur_sol, code_etat).calculer()
        indice_vides = CalculIndiceDesVides(e0_star, cc_star, sigma_v, sigma0).calculer()
        s1, s2, s_total = CalculTassements(ef, e0_star, indice_vides).calculer()

        self.result_label.setText(
            f"Tassement total S = {s_total:.2f} %\n"
            f"Tassement S1 (fonte de glace) = {s1:.2f} %\n"
            f"Tassement S2 (compression) = {s2:.2f} %"
        )

    def toggle_cc_input(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        self.cc_input.setVisible(not is_checked)
        self.cc_label.setVisible(not is_checked)
