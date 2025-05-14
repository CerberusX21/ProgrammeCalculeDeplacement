from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox
from PyQt6.QtCore import Qt

from widgets import parametre, parametre_result_inter
from formulas.hydraulique.FormulaClay import FormulaClay
from formulas.hydraulique.FormulaLiquid import FormulaLiquid
from formulas.hydraulique.FormulaD50ff import FormulaD50ff

class HydroPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout()
        self.layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(15)
        self.setLayout(self.layout)

        self.type_sol_input = QLineEdit()
        self.type_sol_input.setPlaceholderText("Valeur...")
        self.type_sol = QComboBox()
        self.type_sol.addItems(["clay%", "wL", "d50ff"])
        self.type_sol_unit = QComboBox()
        self.type_sol_unit.addItems(["%", "mm"])

        self.pores_input = QLineEdit()
        self.pores_input.setPlaceholderText("Valeur...")
        self.pores_sol = QComboBox()
        self.pores_sol.addItems(["W", "ρf", "ef*"])
        self.pores_sol_unit = QComboBox()
        self.pores_sol_unit.addItems(["kg/m3", "g/cm3"])

        self.compress_input = QLineEdit()
        self.compress_input.setPlaceholderText("Valeur...")
        self.compress_sol = QComboBox()
        self.compress_sol.addItems(["σ′v"])
        self.compress_sol_unit = QComboBox()
        self.compress_sol_unit.addItems(["kPa"])

        self.density_input = QLineEdit()
        self.density_input.setPlaceholderText("Valeur...")

        self.result_EI_input = QLineEdit()
        self.result_EI_input.setPlaceholderText("Valeur...")
        self.result_EI_check = QCheckBox("use own result?")
        self.result_EI_input.setEnabled(False)
        self.result_EI_check.stateChanged.connect(lambda state: self.result_EI_input.setEnabled(state == Qt.CheckState.Checked.value))

        self.result_Cc_input = QLineEdit()
        self.result_Cc_input.setPlaceholderText("Valeur...")
        self.result_Cc_check = QCheckBox("use own result?")
        self.result_Cc_input.setEnabled(False)
        self.result_Cc_check.stateChanged.connect(lambda state: self.result_Cc_input.setEnabled(state == Qt.CheckState.Checked.value))

        self.result_Ck_input = QLineEdit()
        self.result_Ck_input.setPlaceholderText("Valeur...")
        self.result_Ck_check = QCheckBox("use own result?")
        self.result_Ck_input.setEnabled(False)
        self.result_Ck_check.stateChanged.connect(lambda state: self.result_Ck_input.setEnabled(state == Qt.CheckState.Checked.value))

        self.layout.addRow("Type de sol :", parametre(self.type_sol, self.type_sol_unit, self.type_sol_input))
        self.layout.addRow("Type de pores :", parametre(self.pores_sol, self.pores_sol_unit, self.pores_input))
        self.layout.addRow("Compression :", parametre(self.compress_sol, self.compress_sol_unit, self.compress_input))
        self.layout.addRow("Type Gs :", self.density_input)
        self.layout.addRow("Résultat Ei :", parametre_result_inter(self.result_EI_check, self.result_EI_input))
        self.layout.addRow("Résultat Cc* :", parametre_result_inter(self.result_Cc_check, self.result_Cc_input))
        self.layout.addRow("Résultat Ck* :", parametre_result_inter(self.result_Ck_check, self.result_Ck_input))

    def calculate(self, result_label):
        try:
            data = {
                'type_sol': float(self.type_sol_input.text()),
                'pores_sol': float(self.pores_input.text()),
                'compress_sol': float(self.compress_input.text()),
                'density_sol': float(self.density_input.text()),
                'water': self.pores_sol.currentText(),
                'type': self.type_sol.currentText()
            }
        except ValueError:
            result_label.setText("Erreur : valeurs invalides.")
            return

        formulas = {
            "clay%": FormulaClay(),
            "wL": FormulaLiquid(),
            "d50ff": FormulaD50ff()
        }

        formula = formulas.get(data['type'])
        if not formula:
            result_label.setText("Erreur : type de sol inconnu.")
            return

        Ei = float(self.result_EI_input.text()) if self.result_EI_input.isEnabled() else None
        Cc = float(self.result_Cc_input.text()) if self.result_Cc_input.isEnabled() else None
        Ck = float(self.result_Ck_input.text()) if self.result_Ck_input.isEnabled() else None

        try:
            result, EI, Cc, Ck = formula.calculate(
                data['type_sol'], data['pores_sol'],
                data['compress_sol'], data['density_sol'],
                data['water'],
                Ei=Ei, Cc=Cc, Ck=Ck
            )
            result_label.setText(f"Résultat : {result}")
            self.result_EI_input.setText(str(EI))
            self.result_Cc_input.setText(str(Cc))
            self.result_Ck_input.setText(str(Ck))
        except Exception as e:
            result_label.setText(f"Erreur de calcul : {e}")

    def reset(self):
        # QLineEdit — vider les champs
        self.type_sol_input.clear()
        self.pores_input.clear()
        self.compress_input.clear()
        self.density_input.clear()
        self.result_EI_input.clear()
        self.result_Cc_input.clear()
        self.result_Ck_input.clear()

        # QComboBox — remettre à l'index 0
        self.type_sol.setCurrentIndex(0)
        self.type_sol_unit.setCurrentIndex(0)
        self.pores_sol.setCurrentIndex(0)
        self.pores_sol_unit.setCurrentIndex(0)
        self.compress_sol.setCurrentIndex(0)
        self.compress_sol_unit.setCurrentIndex(0)

        # QCheckBox — décocher
        self.result_EI_check.setChecked(False)
        self.result_Cc_check.setChecked(False)
        self.result_Ck_check.setChecked(False)

        # désactiver les champs de résultats manuels
        self.result_EI_input.setEnabled(False)
        self.result_Cc_input.setEnabled(False)
        self.result_Ck_input.setEnabled(False)
