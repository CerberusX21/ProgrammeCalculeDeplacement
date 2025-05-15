from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox, QMessageBox
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

        self.pores_input = QLineEdit()
        self.pores_input.setPlaceholderText("Valeur...")
        self.pores_sol = QComboBox()
        self.pores_sol.addItems(["W", "ρf", "ef*"])
        self.pores_sol_unit = QComboBox()

        self.compress_input = QLineEdit()
        self.compress_input.setPlaceholderText("Valeur...")
        self.compress_sol = QComboBox()
        self.compress_sol.addItems(["σ′v"])
        self.compress_sol_unit = QComboBox()

        self.type_unit_mapping = {
            self.type_sol: {
                "clay%": ["%"],
                "wL": ["%"],
                "d50ff": ["mm"]
            },
            self.pores_sol: {
                "W": ["kg/kg"],
                "ρf": ["kg/m3", "g/cm3"],
                "ef*": ["Direct"]

            },
            self.compress_sol: {
                "σ′v": ["kPa"]
            }
        }

        self.type_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.type_sol, self.type_sol_unit))
        self.pores_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.pores_sol, self.pores_sol_unit))
        self.compress_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.compress_sol, self.compress_sol_unit))

        self.density_input = QLineEdit()
        self.density_input.setPlaceholderText("Valeur...")

        self.result_EI_input = QLineEdit()
        self.result_EI_input.setPlaceholderText("Valeur...")
        self.result_EI_check = QCheckBox("use own result?")
        self.result_EI_input.setEnabled(False)
        self.result_EI_check.stateChanged.connect(
            lambda state: self.result_EI_input.setEnabled(state == Qt.CheckState.Checked.value))

        self.result_Cc_input = QLineEdit()
        self.result_Cc_input.setPlaceholderText("Valeur...")
        self.result_Cc_check = QCheckBox("use own result?")
        self.result_Cc_input.setEnabled(False)
        self.result_Cc_check.stateChanged.connect(
            lambda state: self.result_Cc_input.setEnabled(state == Qt.CheckState.Checked.value))

        self.result_Ck_input = QLineEdit()
        self.result_Ck_input.setPlaceholderText("Valeur...")
        self.result_Ck_check = QCheckBox("use own result?")
        self.result_Ck_input.setEnabled(False)
        self.result_Ck_check.stateChanged.connect(
            lambda state: self.result_Ck_input.setEnabled(state == Qt.CheckState.Checked.value))

        self.layout.addRow("Type de sol :", parametre(self.type_sol_unit, self.type_sol, self.type_sol_input))
        self.layout.addRow("Type de pores :", parametre(self.pores_sol_unit, self.pores_sol, self.pores_input))
        self.layout.addRow("Compression :", parametre(self.compress_sol_unit, self.compress_sol, self.compress_input))
        self.layout.addRow("Type Gs :", self.density_input)
        self.layout.addRow("Résultat Ei :", parametre_result_inter(self.result_EI_check, self.result_EI_input))
        self.layout.addRow("Résultat Cc* :", parametre_result_inter(self.result_Cc_check, self.result_Cc_input))
        self.layout.addRow("Résultat Ck* :", parametre_result_inter(self.result_Ck_check, self.result_Ck_input))

        self.input_limits = {
            self.type_sol_unit: {
                "%": (1, 100),
                "mm": (0.001, 0.1)
            },
            self.pores_sol_unit: {
                "kg/kg": (0, float('inf')),
                "kg/m3": (900, 3000),
                "g/cm3": (0.9, 3),
                "Direct": (0, float('inf')),
            },
            self.compress_sol_unit: {
                "kPa": (0, float('inf'))
            }
        }

        self.update_unit_options(self.type_sol, self.type_sol_unit)
        self.update_unit_options(self.pores_sol, self.pores_sol_unit)
        self.update_unit_options(self.compress_sol, self.compress_sol_unit)

    def update_unit_options(self, type_combo: QComboBox, unit_combo: QComboBox):
        selected_type = type_combo.currentText()
        mapping = self.type_unit_mapping.get(type_combo, {})

        units = mapping.get(selected_type, [])

        if units:
            current_unit = unit_combo.currentText()
            unit_combo.blockSignals(True)
            unit_combo.clear()
            unit_combo.addItems(units)

            if current_unit in units:
                unit_combo.setCurrentIndex(units.index(current_unit))
            unit_combo.blockSignals(False)

    def validate_input(self, value: float, unit_combo):
        if unit_combo is False:
            if not (1 <= value <= 4):
                return False, 1, 4
        else:
            unit = unit_combo.currentText()
            limits = self.input_limits.get(unit_combo, {}).get(unit)
            if limits:
                min_val, max_val = limits
                if not (min_val <= value <= max_val):
                    return False, min_val, max_val

        return True, None, None


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

        validations = [
            (data["type_sol"], self.type_sol_unit, self.type_sol.currentText()),
            (data["pores_sol"], self.pores_sol_unit, self.pores_sol.currentText()),
            (data["compress_sol"], self.compress_sol_unit, self.compress_sol.currentText()),
            (data["density_sol"], False, "Gs")
        ]

        for value, unit_combo, text in validations:
            is_valid, min_val, max_val = self.validate_input(value, unit_combo)
            if not is_valid:
                QMessageBox.warning(self, "Valeur invalide",
                                    f"La valeur de {text} doit être entre {min_val} et {max_val}.")
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
            result, EI, Cc, Ck, E0, σ0, kv0, σv = formula.calculate(
                data['type_sol'], data['pores_sol'],
                data['compress_sol'], data['density_sol'],
                data['water'],
                Ei=Ei, Cc=Cc, Ck=Ck
            )
            result_label.setText(f"Résultat : {result:.2e}")
            self.result_EI_input.setText(f"{EI:.2f}")
            self.result_Cc_input.setText(f"{Cc:.2f}")
            self.result_Ck_input.setText(f"{Ck:.2f}")
            return self.register(result, EI, Cc, Ck, E0, σ0, kv0, σv)
        except Exception as e:
            result_label.setText(f"Erreur de calcul : {e}")

    def reset(self):
        self.type_sol_input.clear()
        self.pores_input.clear()
        self.compress_input.clear()
        self.density_input.clear()
        self.result_EI_input.clear()
        self.result_Cc_input.clear()
        self.result_Ck_input.clear()

        self.type_sol.setCurrentIndex(0)
        self.type_sol_unit.setCurrentIndex(0)
        self.pores_sol.setCurrentIndex(0)
        self.pores_sol_unit.setCurrentIndex(0)
        self.compress_sol.setCurrentIndex(0)
        self.compress_sol_unit.setCurrentIndex(0)

        self.result_EI_check.setChecked(False)
        self.result_Cc_check.setChecked(False)
        self.result_Ck_check.setChecked(False)

        self.result_EI_input.setEnabled(False)
        self.result_Cc_input.setEnabled(False)
        self.result_Ck_input.setEnabled(False)

    def register(self, result, EI, Cc, Ck, E0, σ0, kv0, σv):
        return {"result": result, "Ei": EI, "Cc": Cc, "Ck": Ck, "E0": E0, "σ0": σ0, "kv0": kv0, "σv": σv}
