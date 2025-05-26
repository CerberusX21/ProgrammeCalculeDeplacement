from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox, QMessageBox,
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from widgets import parametre, parametre_result_inter
from formulas.hydraulique.FormulaClay import FormulaClay
from formulas.hydraulique.FormulaLiquid import FormulaLiquid
from formulas.hydraulique.FormulaD50ff import FormulaD50ff
from pages.Hydro.graph_viewer_hydro import GraphViewer


class HydroPage(QWidget):
    def __init__(self):
        super().__init__()
        self.graph_data = None

        self._setup_form()
        self._init_unit_mappings()
        self._init_input_limits()
        self._connect_unit_updates()
        self._set_initial_units()

        self.result_label = QLabel("Result:")
        self.result_label.setObjectName("ResultLabel")

        self.calculate_button = QPushButton("Calculate")
        self.reset_button = QPushButton("Reset")
        self.graph_viewer = GraphViewer()

        self.calculate_button.clicked.connect(self.calculate)
        self.reset_button.clicked.connect(self.reset)

        self._assemble_layout()

    def _setup_form(self):
        self.form_layout = QFormLayout()
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form_layout.setHorizontalSpacing(20)
        self.form_layout.setVerticalSpacing(15)

        self.type_sol_input = self._create_line_edit("Value...")
        self.pores_input = self._create_line_edit("Value...")
        self.compress_input = self._create_line_edit("Value...")
        self.density_input = self._create_line_edit("Value...")

        self.type_sol = QComboBox()
        self.type_sol.addItems(["clay%", "wL", "d50ff"])
        self.type_sol_unit = QComboBox()

        self.pores_sol = QComboBox()
        self.pores_sol.addItems(["W", "ρf", "ef*"])
        self.pores_sol_unit = QComboBox()

        self.compress_sol = QComboBox()
        self.compress_sol.addItems(["σ′v"])
        self.compress_sol_unit = QComboBox()

        self.result_EI_input, self.result_EI_check = self._create_optional_input("Value...")
        self.result_Cc_input, self.result_Cc_check = self._create_optional_input("Value...")
        self.result_Ck_input, self.result_Ck_check = self._create_optional_input("Value...")

        self.form_layout.addRow("Soil type:", parametre(self.type_sol, self.type_sol_unit, self.type_sol_input))
        self.form_layout.addRow("Pore type:", parametre(self.pores_sol, self.pores_sol_unit, self.pores_input))
        self.form_layout.addRow("Compression:", parametre(self.compress_sol, self.compress_sol_unit, self.compress_input))
        self.form_layout.addRow("Gs type:", self.density_input)
        self.form_layout.addRow("Result Ei:", parametre_result_inter(self.result_EI_check, self.result_EI_input))
        self.form_layout.addRow("Result Cc*:", parametre_result_inter(self.result_Cc_check, self.result_Cc_input))
        self.form_layout.addRow("Result Ck*:", parametre_result_inter(self.result_Ck_check, self.result_Ck_input))

    def _assemble_layout(self):
        left_layout = QVBoxLayout()
        left_layout.addLayout(self.form_layout)

        button_row = QHBoxLayout()
        button_row.addWidget(self.reset_button)
        button_row.addWidget(self.calculate_button)
        left_layout.addLayout(button_row)
        left_layout.addWidget(self.result_label)

        self.graph_viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.graph_viewer)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 3)
        self.setLayout(main_layout)

    def _create_line_edit(self, placeholder):
        edit = QLineEdit()
        edit.setMinimumWidth(120)
        edit.setPlaceholderText(placeholder)
        return edit

    def _create_optional_input(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        checkbox = QCheckBox("Use custom result?")
        edit.setEnabled(False)
        checkbox.stateChanged.connect(lambda state: edit.setEnabled(state == Qt.CheckState.Checked.value))
        return edit, checkbox

    def _init_unit_mappings(self):
        self.type_unit_mapping = {
            self.type_sol: {"clay%": ["%"], "wL": ["%"], "d50ff": ["mm"]},
            self.pores_sol: {"W": ["kg/kg"], "ρf": ["kg/m3", "g/cm3"], "ef*": ["Direct"]},
            self.compress_sol: {"σ′v": ["kPa"]}
        }

    def _init_input_limits(self):
        self.input_limits = {
            self.type_sol_unit: {"%": (1, 100), "mm": (0.001, 0.1)},
            self.pores_sol_unit: {
                "kg/kg": (0, float('inf')), "kg/m3": (0.9, 3),
                "g/cm3": (900, 3000), "Direct": (0, float('inf'))
            },
            self.compress_sol_unit: {"kPa": (0, float('inf'))}
        }

    def _connect_unit_updates(self):
        self.type_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.type_sol, self.type_sol_unit))
        self.pores_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.pores_sol, self.pores_sol_unit))
        self.compress_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.compress_sol, self.compress_sol_unit))

    def _set_initial_units(self):
        self.update_unit_options(self.type_sol, self.type_sol_unit)
        self.update_unit_options(self.pores_sol, self.pores_sol_unit)
        self.update_unit_options(self.compress_sol, self.compress_sol_unit)

    def update_unit_options(self, type_combo: QComboBox, unit_combo: QComboBox):
        selected_type = type_combo.currentText()
        units = self.type_unit_mapping.get(type_combo, {}).get(selected_type, [])

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
            return (1 <= value <= 4), 1, 4

        unit = unit_combo.currentText()
        limits = self.input_limits.get(unit_combo, {}).get(unit)
        if limits:
            min_val, max_val = limits
            return (min_val <= value <= max_val), min_val, max_val

        return True, None, None

    def calculate(self):
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
            QMessageBox.critical(self, "Value Error", "Please enter valid numerical values.")
            return

        validations = [
            (data["type_sol"], self.type_sol_unit, self.type_sol.currentText()),
            (data["pores_sol"], self.pores_sol_unit, self.pores_sol.currentText()),
            (data["compress_sol"], self.compress_sol_unit, self.compress_sol.currentText()),
            (data["density_sol"], False, "Gs")
        ]

        for value, unit_combo, label in validations:
            valid, min_val, max_val = self.validate_input(value, unit_combo)
            if not valid:
                QMessageBox.warning(self, "Invalid value", f"The value for {label} must be between {min_val} and {max_val}.")
                return

        if self.pores_sol_unit.currentText() == "g/cm3":
            data["pores_sol"] /= 1000

        if self.pores_sol.currentText() == "ρf" and data["pores_sol"] >= data["density_sol"]:
            QMessageBox.warning(self, "Invalid value", "Make sure Gs > ρf")
            return

        formula_class = {"clay%": FormulaClay, "wL": FormulaLiquid, "d50ff": FormulaD50ff}.get(data["type"])
        ei = float(self.result_EI_input.text()) if self.result_EI_check.isChecked() else None
        cc = float(self.result_Cc_input.text()) if self.result_Cc_check.isChecked() else None
        ck = float(self.result_Ck_input.text()) if self.result_Ck_check.isChecked() else None

        try:
            result, ei, cc, ck, e0, sigma_0, kv0, sigma_v = formula_class().calculate(
                data["type_sol"], data["pores_sol"], data["compress_sol"], data["density_sol"],
                data["water"], ei=ei, cc=cc, ck=ck
            )
            self.result_label.setText(f"Result: {result:.2e}")
            self.result_EI_input.setText(f"{ei:.2f}")
            self.result_Cc_input.setText(f"{cc:.2f}")
            self.result_Ck_input.setText(f"{ck:.2f}")

            self.graph_data = {
                "result": result, "ei": ei, "cc": cc, "ck": ck,
                "e0": e0, "sigma_0": sigma_0, "kv0": kv0, "sigma_v": sigma_v
            }
            self.graph_viewer.set_graph_data(self.graph_data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Calculation error: {e}")

    def reset(self):
        for input_widget in [
            self.type_sol_input, self.pores_input, self.compress_input,
            self.density_input, self.result_EI_input, self.result_Cc_input, self.result_Ck_input
        ]:
            input_widget.clear()

        for combo_box in [
            self.type_sol, self.type_sol_unit,
            self.pores_sol, self.pores_sol_unit,
            self.compress_sol, self.compress_sol_unit
        ]:
            combo_box.setCurrentIndex(0)

        for check_box, input_widget in [
            (self.result_EI_check, self.result_EI_input),
            (self.result_Cc_check, self.result_Cc_input),
            (self.result_Ck_check, self.result_Ck_input)
        ]:
            check_box.setChecked(False)
            input_widget.setEnabled(False)

        self.result_label.setText("Result:")
        self.graph_viewer.clear_graph()
