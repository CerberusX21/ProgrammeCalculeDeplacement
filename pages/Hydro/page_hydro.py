from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QLineEdit,
    QLabel, QPushButton, QMessageBox, QCheckBox, QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from style import APP_STYLE
from pages.Hydro.graph_viewer_hydro import GraphViewer
from formulas.hydraulique.FormulaClay import FormulaClay
from formulas.hydraulique.FormulaLiquid import FormulaLiquid
from formulas.hydraulique.FormulaD50ff import FormulaD50ff
from pages.soil_parameter import assemble_hydro_layout, init_unit_mappings, init_input_limits
from widgets.modern_widgets import ModernParameterWidget, ModernGroupBox


class HydroPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setMinimumSize(800, 600)  # Minimum size for usability
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(APP_STYLE)
        self._other_page = None
        self._syncing = False
        self._custom_ei_edited = False
        self._custom_cc_edited = False
        self._custom_ck_edited = False
        self.graph_data = None
        self._init_widgets()
        # Initialize common mappings and limits from hydro_layout
        init_unit_mappings(self)
        init_input_limits(self)
        self._connect_unit_updates()
        self._set_initial_units()
        self.result_label = QLabel("Result:")
        self.result_label.setObjectName("ResultLabel")
        self.graph_viewer = GraphViewer()
        self.calculate_button = QPushButton("Calculate")
        self.reset_button = QPushButton("Reset")
        self.calculate_button.clicked.connect(self.calculate)
        self.reset_button.clicked.connect(self.reset)
        
        # Set up the main layout first
        assemble_hydro_layout(self)
        
        # Add the hydro-specific custom results section
        self._setup_custom_results()
        
        # For syncing data between pages
        self.type_sol_input.textChanged.connect(lambda value: self._sync_field('type_sol_input', value))
        self.pores_input.textChanged.connect(lambda value: self._sync_field('pores_input', value))
        self.compress_input.textChanged.connect(lambda value: self._sync_field('compress_input', value))
        self.density_input.textChanged.connect(lambda value: self._sync_field('density_input', value))
        # Manual input detection
        self.result_EI_input.textEdited.connect(self._on_custom_ei_edited)
        self.result_Cc_input.textEdited.connect(self._on_custom_cc_edited)
        self.result_Ck_input.textEdited.connect(self._on_custom_ck_edited)
        self.use_custom_params_check.stateChanged.connect(self._on_custom_check_changed)
        self.use_custom_params_check.stateChanged.connect(self._toggle_custom_params)

    def set_other_page(self, other_page):
        self._other_page = other_page

    def _sync_field(self, field_name, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            getattr(self._other_page, field_name).setText(value)
            self._other_page._syncing = False

    def _sync_combo(self, combo_name, index):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            other_combo = getattr(self._other_page, combo_name)
            other_combo.setCurrentIndex(index)
            self._other_page._syncing = False

    def _on_custom_ei_edited(self):
        self._custom_ei_edited = True

    def _on_custom_cc_edited(self):
        self._custom_cc_edited = True

    def _on_custom_ck_edited(self):
        self._custom_ck_edited = True

    def _on_custom_check_changed(self, state):
        if state == Qt.CheckState.Checked.value:
            self._custom_ei_edited = False
            self._custom_cc_edited = False
            self._custom_ck_edited = False

    def _init_widgets(self):
        self.type_sol_input = self._create_line_edit("Value...")
        self.pores_input = self._create_line_edit("Value...")
        self.compress_input = self._create_line_edit("Value...")
        self.density_input = self._create_line_edit("Value...")
        self.density_input.setText("2.67")
        self._set_value_column_width(120)

        self.type_sol = QComboBox()
        self.type_sol.setProperty("type", "type")
        self.type_sol.addItems(["Clay percentage", "Liquid limit", "Fine fraction median diameter"])
        self.type_sol_unit = QComboBox()

        self.pores_sol = QComboBox()
        self.pores_sol.setProperty("type", "type")
        self.pores_sol.addItems(["Thawed soil initial water content", "Frozen buld density", "Frozen void ratio"])
        self.pores_sol_unit = QComboBox()

        self.compress_sol = QComboBox()
        self.compress_sol.setProperty("type", "type")
        self.compress_sol.addItems(["Effective vertical stress"])
        self.compress_sol_unit = QComboBox()

        self.density_sol = QComboBox()
        self.density_sol.setProperty("type", "type")
        self.density_sol.addItems(["Specific gravity of solids"])
        self.density_sol_unit = QComboBox()
        self.density_sol_unit.addItems(["-"])

        # Results widgets
        self.result_EI_input = self._create_line_edit("Value...")
        self.result_EI_input.setProperty("custom", "true")
        self.result_Cc_input = self._create_line_edit("Value...")
        self.result_Cc_input.setProperty("custom", "true")
        self.result_Ck_input = self._create_line_edit("Value...")
        self.result_Ck_input.setProperty("custom", "true")

        self.result_EI_type = QComboBox()
        self.result_EI_type.setProperty("type", "type")
        self.result_EI_type.addItems(["ei*"])
        self.result_EI_unit = QComboBox()
        self.result_EI_unit.addItems(["-"])

        self.result_Cc_type = QComboBox()
        self.result_Cc_type.setProperty("type", "type")
        self.result_Cc_type.addItems(["Cc*"])
        self.result_Cc_unit = QComboBox()
        self.result_Cc_unit.addItems(["-"])

        self.result_Ck_type = QComboBox()
        self.result_Ck_type.setProperty("type", "type")
        self.result_Ck_type.addItems(["Ck*"])
        self.result_Ck_unit = QComboBox()
        self.result_Ck_unit.addItems(["-"])

        # Connect combo box changes
        self.type_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('type_sol', idx))
        self.type_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('type_sol_unit', idx))
        self.pores_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('pores_sol', idx))
        self.pores_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('pores_sol_unit', idx))
        self.compress_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('compress_sol', idx))
        self.compress_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('compress_sol_unit', idx))
        self.density_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('density_sol', idx))
        self.density_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('density_sol_unit', idx))

    def _create_line_edit(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        return edit

    def _create_optional_input(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        checkbox = QCheckBox("Use custom result?")
        edit.setEnabled(False)
        checkbox.stateChanged.connect(lambda state: edit.setEnabled(state == Qt.CheckState.Checked.value))
        return edit, checkbox

    def _connect_unit_updates(self):
        self.type_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.type_sol, self.type_sol_unit))
        self.pores_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.pores_sol, self.pores_sol_unit))
        self.compress_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.compress_sol, self.compress_sol_unit))

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
            (data["density_sol"], False, "Specific gravity of solids")
        ]

        for value, unit_combo, label in validations:
            valid, min_val, max_val = self.validate_input(value, unit_combo)
            if not valid:
                QMessageBox.warning(self, "Invalid value",
                                    f"The value for {label} must be between {min_val} and {max_val}.")
                return

        if self.pores_sol_unit.currentText() == "g/cm3":
            data["pores_sol"] /= 1000

        if self.pores_sol.currentText() == "Frozen buld density" and data["pores_sol"] >= data["density_sol"]:
            QMessageBox.warning(self, "Invalid value", "Make sure Specific gravity of solids > Frozen buld density")
            return

        formula_class = {
            "Clay percentage": FormulaClay,
            "Liquid limit": FormulaLiquid,
            "Fine fraction median diameter": FormulaD50ff
        }.get(data["type"])

        # For custom values
        if self.use_custom_params_check.isChecked():
            # Automatic calculation for initialization
            try:
                result, ei_calc, cc_calc, ck_calc, e0, sigma_0, kv0, sigma_v = formula_class().calculate(
                    data["type_sol"], data["pores_sol"], data["compress_sol"], data["density_sol"],
                    data["water"], ei=None, cc=None, ck=None
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Calculation error: {e}")
                return
            # EI*
            if not self._custom_ei_edited:
                self.result_EI_input.setText(f"{ei_calc:.2f}")
                ei = ei_calc
            else:
                try:
                    ei = float(self.result_EI_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid ei*", "Please enter a valid number for ei*.")
                    return
            # Cc*
            if not self._custom_cc_edited:
                self.result_Cc_input.setText(f"{cc_calc:.2f}")
                cc = cc_calc
            else:
                try:
                    cc = float(self.result_Cc_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Cc*", "Please enter a valid number for Cc*.")
                    return
            # Ck*
            if not self._custom_ck_edited:
                self.result_Ck_input.setText(f"{ck_calc:.2f}")
                ck = ck_calc
            else:
                try:
                    ck = float(self.result_Ck_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Ck*", "Please enter a valid number for Ck*.")
                    return
            # Final calculation with custom or edited values
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
                return
        else:
            try:
                result, ei, cc, ck, e0, sigma_0, kv0, sigma_v = formula_class().calculate(
                    data["type_sol"], data["pores_sol"], data["compress_sol"], data["density_sol"],
                    data["water"], ei=None, cc=None, ck=None
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
                return

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
            input_widget.clear()

        self.result_label.setText("Result:")
        self.graph_viewer.clear_graph()
        self.graph_data = None

    def _toggle_custom_params(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        self.results_group.setVisible(is_checked)
        self.result_EI_input.setEnabled(is_checked)
        self.result_Cc_input.setEnabled(is_checked)
        self.result_Ck_input.setEnabled(is_checked)
        self.result_EI_type.setEnabled(is_checked)
        self.result_EI_unit.setEnabled(is_checked)
        self.result_Cc_type.setEnabled(is_checked)
        self.result_Cc_unit.setEnabled(is_checked)
        self.result_Ck_type.setEnabled(is_checked)
        self.result_Ck_unit.setEnabled(is_checked)

    def _set_value_column_width(self, width=120):
        self.type_sol_input.setMinimumWidth(width)
        self.type_sol_input.setMaximumWidth(width)
        self.pores_input.setMinimumWidth(width)
        self.pores_input.setMaximumWidth(width)
        self.compress_input.setMinimumWidth(width)
        self.compress_input.setMaximumWidth(width)
        self.density_input.setMinimumWidth(width)
        self.density_input.setMaximumWidth(width)
        # For optional results
        if hasattr(self, 'result_EI_input'):
            self.result_EI_input.setMinimumWidth(width)
            self.result_EI_input.setMaximumWidth(width)
        if hasattr(self, 'result_Cc_input'):
            self.result_Cc_input.setMinimumWidth(width)
            self.result_Cc_input.setMaximumWidth(width)
        if hasattr(self, 'result_Ck_input'):
            self.result_Ck_input.setMinimumWidth(width)
            self.result_Ck_input.setMaximumWidth(width)

    def _setup_custom_results(self):
        # Create the custom results group
        self.results_group = ModernGroupBox("Hydraulic Custom Parameters")
        results_layout = QVBoxLayout()
        results_layout.setSpacing(6)

        # Headers
        headers_layout = QGridLayout()
        headers_layout.addWidget(QLabel("<b>Parameter</b>"), 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.addWidget(QLabel("<b>Type</b>"), 0, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.addWidget(QLabel("<b>Unit</b>"), 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.addWidget(QLabel("<b>Value</b>"), 0, 3, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.setColumnStretch(0, 3)
        headers_layout.setColumnStretch(1, 2)
        headers_layout.setColumnStretch(2, 1)
        headers_layout.setColumnStretch(3, 2)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e2e8f0; height: 1px;")

        # Add the parameters
        ei_param = ModernParameterWidget(
            "Initial thawed void ratio",
            self.result_EI_type, self.result_EI_unit, self.result_EI_input
        )

        cc_param = ModernParameterWidget(
            "Thawed soil compression index",
            self.result_Cc_type, self.result_Cc_unit, self.result_Cc_input
        )

        ck_param = ModernParameterWidget(
            "Hydraulic conductivity index",
            self.result_Ck_type, self.result_Ck_unit, self.result_Ck_input
        )

        # Assemble the layout
        results_layout.addLayout(headers_layout)
        results_layout.addWidget(separator)
        results_layout.addWidget(ei_param)
        results_layout.addWidget(cc_param)
        results_layout.addWidget(ck_param)
        
        self.results_group.setLayout(results_layout)
        self.results_group.setVisible(False)

        # Add to main layout
        main_layout = self.layout()
        if main_layout:
            left_widget = main_layout.itemAt(0).widget()
            if left_widget:
                left_layout = left_widget.layout()
                if left_layout:
                    # Insert before the button layout (which is the last item)
                    left_layout.insertWidget(left_layout.count() - 1, self.results_group)