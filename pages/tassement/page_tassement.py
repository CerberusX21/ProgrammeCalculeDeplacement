from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QComboBox,
    QVBoxLayout, QPushButton, QMessageBox, QSizePolicy, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt
from pages.tassement.graph_viewer_tassement import GraphViewer
from style import APP_STYLE
from widgets.modern_widgets import ModernGroupBox, ModernResultsSection, ModernResultsDisplay, ModernResultsPanel

from formulas.tassement.formule_ei_tassement import EI_Tassement
from formulas.tassement.formule_ip_ir_tassement import ClassificationSol
from formulas.tassement.formule_cc_tassement import CalculCcStar
from formulas.tassement.formule_e0_tassement import CalculE0Tassement
from formulas.tassement.formule_sigma0 import CalculSigma0
from formulas.tassement.formule_calculer_tassement import CalculTassements
from formulas.tassement.formule_indice_des_vides import CalculIndiceDesVides
from formulas.tassement.formule_ip_ir_tassement import CLASSE_SOL
from pages.soil_parameter import assemble_hydro_layout, init_unit_mappings, init_input_limits
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter, QTextDocument
import tempfile
import os

class TassementPage(QWidget):
    def __init__(self):
        super().__init__()
        self._other_page = None
        self._syncing = False
        self._custom_ei_edited = False
        self._custom_cc_edited = False
        self._custom_type_edited = False
        self.setMinimumSize(800, 600)  # Minimum size for usability
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(APP_STYLE)

        self._init_widgets()
        
        # Initialize common mappings and limits from hydro_layout
        init_unit_mappings(self)
        init_input_limits(self)
        self._connect_unit_updates()
        self._set_initial_units()
        
        # Create the results display widget
        self.results_display = ModernResultsDisplay()
        self.results_display.setFixedHeight(150)  # Increased height for 3 lines of results
        
        # Create the graph viewer
        self.graph_viewer = GraphViewer()
        self.graph_viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Create the results panel to group results and graphs
        self.results_panel = ModernResultsPanel()
        self.results_panel.add_widget(self.results_display)
        self.results_panel.add_widget(self.graph_viewer)
        
        self.calculate_button = QPushButton("Calculate")
        self.reset_button = QPushButton("Reset")

        #Pour connecter le bouton export à la méthode d'exportation
        self.results_panel.get_export_button().clicked.connect(self.export_to_pdf)
        
        
        # Set up the main layout first
        assemble_hydro_layout(self)
        
        # Add the settlement-specific custom results section
        self._setup_custom_results()
        
        # Connect signals
        self.calculate_button.clicked.connect(lambda: self.calculate(self.results_display))
        self.reset_button.clicked.connect(self.reset)
        
        # Pour que le graphique se mette à jour quand on change la classification manuelle
        self.result_type_sol_unit.currentIndexChanged.connect(
            lambda: self.calculate(self.results_display, from_manual_classification=True)
        )
        
        # For syncing data between pages
        self.type_sol_input.textChanged.connect(self._sync_type_sol)
        self.pores_input.textChanged.connect(self._sync_pores)
        self.compress_input.textChanged.connect(self._sync_compress)
        self.density_input.textChanged.connect(self._sync_density)
        
        # Manual input detection
        self.result_EI_input.textEdited.connect(self._on_custom_ei_edited)
        self.result_Cc_input.textEdited.connect(self._on_custom_cc_edited)
        self.use_custom_params_check.stateChanged.connect(self._on_custom_check_changed)
        self.use_custom_params_check.stateChanged.connect(self._toggle_custom_params)
        self.result_type_sol_unit.currentIndexChanged.connect(self._on_custom_type_edited)

    def _init_widgets(self):
        self.type_sol_input = self._create_line_edit("Value...")
        self.pores_input = self._create_line_edit("Value...")
        self.compress_input = self._create_line_edit("Value...")
        self.density_input = self._create_line_edit("Value...")
        self.density_input.setText("2.67")

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

        # Update initial states of dropdowns with single options
        self._update_combo_state(self.compress_sol)
        self._update_combo_state(self.density_sol)
        self._update_combo_state(self.density_sol_unit)

        # Results widgets
        self.result_EI_input = self._create_line_edit("Value...")
        self.result_Cc_input = self._create_line_edit("Value...")

        # Results unit dropdowns
        self.result_EI_unit = QComboBox()
        self.result_EI_unit.addItems(["ei*"])
        self._update_combo_state(self.result_EI_unit)

        self.result_Cc_unit = QComboBox()
        self.result_Cc_unit.addItems(["Cc*"])
        self._update_combo_state(self.result_Cc_unit)

        self.result_type_sol_unit = QComboBox()
        self.result_type_sol_unit.addItems(["Ice-Rich", "Ice-Poor"])

        # Connect combo box changes
        self.type_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('type_sol', idx))
        self.type_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('type_sol_unit', idx))
        self.pores_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('pores_sol', idx))
        self.pores_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('pores_sol_unit', idx))
        self.compress_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('compress_sol', idx))
        self.compress_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('compress_sol_unit', idx))
        self.density_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('density_sol', idx))
        self.density_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('density_sol_unit', idx))

    def _setup_custom_results(self):
        # Create the custom results group
        self.results_group = ModernGroupBox("Settlement Custom Parameters")
        
        # Create the results section
        results_section = ModernResultsSection()
        
        # Add the parameters and store the checkboxes
        self.result_EI_check = results_section.add_result(
            "Initial thawed void ratio",
            self.result_EI_unit,
            self.result_EI_input
        )
        
        self.result_Cc_check = results_section.add_result(
            "Thawed soil compression index",
            self.result_Cc_unit,
            self.result_Cc_input
        )
        
        # Add Ice content classification without value input
        self.result_type_sol_check = results_section.add_result_no_value(
            "Ice content classification",
            self.result_type_sol_unit
        )
        
        # Connect checkbox state changes to input field states
        self.result_EI_check.stateChanged.connect(
            lambda state: self._toggle_input_fields(state, [self.result_EI_input, self.result_EI_unit])
        )
        self.result_Cc_check.stateChanged.connect(
            lambda state: self._toggle_input_fields(state, [self.result_Cc_input, self.result_Cc_unit])
        )
        self.result_type_sol_check.stateChanged.connect(
            lambda state: self._toggle_input_fields(state, [self.result_type_sol_unit])
        )
        
        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(results_section)
        self.results_group.setLayout(main_layout)
        self.results_group.setVisible(False)

        # Add to main layout right after the checkbox
        main_layout = self.layout()
        if main_layout:
            left_widget = main_layout.itemAt(0).widget()
            if left_widget:
                left_layout = left_widget.layout()
                if left_layout:
                    # Find the checkbox widget
                    for i in range(left_layout.count()):
                        item = left_layout.itemAt(i)
                        if item.widget() and isinstance(item.widget(), QWidget):
                            if hasattr(item.widget(), 'layout'):
                                checkbox_layout = item.widget().layout()
                                if checkbox_layout and isinstance(checkbox_layout, QHBoxLayout):
                                    for j in range(checkbox_layout.count()):
                                        checkbox_item = checkbox_layout.itemAt(j)
                                        if checkbox_item.widget() and isinstance(checkbox_item.widget(), QCheckBox):
                                            # Insert the results group right after the checkbox's parent widget
                                            left_layout.insertWidget(i + 1, self.results_group)
                                            return
                    
                    # Fallback: insert before the button layout if checkbox not found
                    left_layout.insertWidget(left_layout.count() - 1, self.results_group)

    def _toggle_input_fields(self, state, widgets):
        """Enable or disable input fields based on checkbox state"""
        enabled = state == Qt.CheckState.Checked.value
        for widget in widgets:
            widget.setEnabled(enabled)
            if isinstance(widget, (QLineEdit, QComboBox)):
                if enabled:
                    widget.setStyleSheet("")
                else:
                    widget.setStyleSheet("""
                        QLineEdit:disabled, QComboBox:disabled {
                            background-color: #f0f0f0;
                            color: #666666;
                            border: 1px solid #cccccc;
                        }
                    """)

    def _toggle_custom_params(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        self.results_group.setVisible(is_checked)
        
        # When showing the custom results, ensure everything starts disabled
        if is_checked:
            # Reset and disable all checkboxes
            self.result_EI_check.setChecked(False)
            self.result_Cc_check.setChecked(False)
            self.result_type_sol_check.setChecked(False)
            
            # The checkbox state changes will automatically handle disabling and styling the inputs
            # through the connected _toggle_input_fields method

    def _create_line_edit(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        return edit

    def _adjust_combo_box_widths(self):
        for combo in [self.type_sol, self.type_sol_unit,
                      self.pores_sol, self.pores_sol_unit,
                      self.compress_sol, self.compress_sol_unit,
                      self.density_sol, self.density_sol_unit,
                      self.result_type_sol_unit]:
            combo.setMinimumWidth(100)
            combo.setMaximumWidth(120)
            combo.setMinimumHeight(20)

    def _connect_unit_updates(self):
        self.type_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.type_sol, self.type_sol_unit))
        self.pores_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.pores_sol, self.pores_sol_unit))
        self.compress_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.compress_sol, self.compress_sol_unit))
        self.density_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.density_sol, self.density_sol_unit))

    def _set_initial_units(self):
        self.update_unit_options(self.type_sol, self.type_sol_unit)
        self.update_unit_options(self.pores_sol, self.pores_sol_unit)
        self.update_unit_options(self.compress_sol, self.compress_sol_unit)
        self.update_unit_options(self.density_sol, self.density_sol_unit)

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
            
            # Update the combo box state based on number of options
            self._update_combo_state(unit_combo)

    def validate_input(self, value: float, unit_combo):
        if unit_combo is False:
            return (1 <= value <= 4), 1, 4
        unit = unit_combo.currentText()
        limits = self.input_limits.get(unit_combo, {}).get(unit)
        if limits:
            min_val, max_val = limits
            return (min_val <= value <= max_val), min_val, max_val
        return True, None, None

    def calculate(self, results_display, from_manual_classification=False):
        if not all([
            self.type_sol_input.text().strip(),
            self.pores_input.text().strip(),
            self.compress_input.text().strip(),
            self.density_input.text().strip()
        ]):
            return
        try:
            data = {
                'type_sol_valeur': float(self.type_sol_input.text()),
                'valeur_pore': float(self.pores_input.text()),
                'sigma_v': float(self.compress_input.text()),
                'Specific gravity of solids': float(self.density_input.text()),
                'type_pore': self.pores_sol.currentText(),
                'type_sol': self.type_sol.currentText()
            }
        except ValueError:
            QMessageBox.critical(self, "Value Error", "Please enter valid numerical values.")
            return

        # Validation des entrées
        validations = [
            (data["type_sol_valeur"], self.type_sol_unit, self.type_sol.currentText()),
            (data["valeur_pore"], self.pores_sol_unit, self.pores_sol.currentText()),
            (data["sigma_v"], self.compress_sol_unit, self.compress_sol.currentText()),
            (data["Specific gravity of solids"], False, "Specific gravity of solids")
        ]
        for value, unit_combo, label in validations:
            valid, min_val, max_val = self.validate_input(value, unit_combo)
            if not valid:
                QMessageBox.warning(self, "Invalid value",
                                    f"The value for {label} must be between {min_val} and {max_val}.")
                return

        if self.pores_sol_unit.currentText() == "kg/m³":
            data["valeur_pore"] /= 1000
        if data["type_pore"] == "Frozen buld density" and data["valeur_pore"] >= data["Specific gravity of solids"]:
            print('test')
            QMessageBox.warning(self, "Invalid value", "Make sure Specific gravity of solids > Frozen buld density")
            return

        try:
            # 1. Calcul ei*
            ei_star_calc = EI_Tassement(data["valeur_pore"], data["Specific gravity of solids"], data["type_pore"]).calculer()
            # 2. Classification (IR ou IP)
            classification = ClassificationSol(ei_star_calc, data["type_sol_valeur"], data["type_sol"])
            code_etat = classification.classer()
            if code_etat == -1:
                QMessageBox.warning(self, "Warning", "Soil classification unknown")
                return
            if (
                classification.is_near_limit
                and not (self.use_custom_params_check.isChecked() and self.result_type_sol_check.isChecked())
                and not from_manual_classification
            ):
                QMessageBox.warning(self, "Warning",
                                    "The soil is close to the Ice-Rich/Ice-Poor limit. Classification may be sensitive to small changes in parameters.")
            detected_type = CLASSE_SOL[code_etat]
            
            # Clear previous results
            self.results_display.clear()
            
            # Show soil type
            self.results_display.add_result("", f"Soil type : {detected_type}")

            # 3. Gestion des paramètres custom
            if self.use_custom_params_check.isChecked():
                # EI*
                if not self._custom_ei_edited:
                    self.result_EI_input.setText(f"{ei_star_calc:.3f}")
                    ei_star = ei_star_calc
                else:
                    try:
                        ei_star = float(self.result_EI_input.text())
                    except ValueError:
                        QMessageBox.warning(self, "Invalid ei*", "Please enter a valid number for ei*.")
                        return
                # Type de sol
                if not self._custom_type_edited:
                    self.result_type_sol_unit.setCurrentIndex(0 if code_etat == 0 else 1)
                    code_etat_custom = code_etat
                else:
                    code_etat_custom = 0 if self.result_type_sol_unit.currentIndex() == 0 else 1
                # Cc*
                if not self._custom_cc_edited:
                    cc_star = CalculCcStar(ei_star, data["type_sol_valeur"], data["type_sol"],
                                           code_etat_custom).calculer()
                    self.result_Cc_input.setText(f"{cc_star:.3f}")
                else:
                    try:
                        cc_star = float(self.result_Cc_input.text())
                    except ValueError:
                        QMessageBox.warning(self, "Invalid Cc*", "Please enter a valid number for Cc*.")
                        return
                code_etat = code_etat_custom
            else:
                ei_star = ei_star_calc
                self.result_EI_input.setText(f"{ei_star:.3f}")
                cc_star = CalculCcStar(ei_star, data["type_sol_valeur"], data["type_sol"], code_etat).calculer()
                self.result_Cc_input.setText(f"{cc_star:.3f}")
                self.result_type_sol_unit.setCurrentIndex(0 if code_etat == 0 else 1)

            # 4. Calculs restants
            e0_star = CalculE0Tassement(ei_star, cc_star, code_etat).calculer()
            sigma0 = CalculSigma0(e0_star, data["type_sol"], data["type_sol_valeur"], code_etat).calculer()
            indice_vides = CalculIndiceDesVides(e0_star, cc_star, data["sigma_v"], sigma0).calculer()
            ef = data["valeur_pore"] if data["type_pore"] == "Frozen void ratio" else ei_star * 1.09
            s1, s2, s_total = CalculTassements(ef, e0_star, indice_vides).calculer()

            # 5. Display results exactly as before
            self.results_display.clear()
            self.results_display.add_result("", f"Total settlement S = {s_total:.2f} %")
            self.results_display.add_result("", f"Settlement S1 (ice melt) = {s1:.2f} %")
            self.results_display.add_result("", f"Settlement S2 (compression) = {s2:.2f} %")

            # 6. Mise à jour du graphique
            self.graph_viewer.set_is_tassement(True)
            self.graph_viewer.set_ei_value(ei_star)
            self.graph_viewer.set_graph_data(self.register(
                s_total, ei_star, cc_star, e0_star, sigma0, indice_vides, s1, s2
            ))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Calcul error: {e}")

    def reset(self):
        for input_widget in [
            self.type_sol_input, self.pores_input, self.compress_input,
            self.density_input, self.result_EI_input, self.result_Cc_input
        ]:
            input_widget.clear()
        self.density_input.setText("2.67")
        
        for combo_box in [
            self.type_sol, self.type_sol_unit,
            self.pores_sol, self.pores_sol_unit,
            self.compress_sol, self.compress_sol_unit,
            self.result_type_sol_unit
        ]:
            combo_box.setCurrentIndex(0)
        self.use_custom_params_check.setChecked(False)
        self.result_EI_input.setEnabled(False)
        self.result_Cc_input.setEnabled(False)
        self.result_type_sol_unit.setCurrentIndex(-1)
        self.results_display.clear()
        self.graph_viewer.clear_graph()

    def register(self, s_total, ei_star, cc_star, e0_star, sigma0, indice_vides, s1, s2):
        return {
            "result": sigma0,
            "kv0": float(self.compress_input.text()),
            "sigma_v": float(self.compress_input.text()),
            "E0": e0_star,
            "Cc": cc_star,
            "ei_star": ei_star,
            "s_total": s_total,
            "s1": s1,
            "s2": s2,
            "cc_star": cc_star,
            "e0_star": e0_star,
            "sigma0": sigma0,
            "indice_vides": indice_vides
        }

    def _set_value_column_width(self, width=120):
        self.type_sol_input.setMinimumWidth(width)
        self.type_sol_input.setMaximumWidth(width)
        self.pores_input.setMinimumWidth(width)
        self.pores_input.setMaximumWidth(width)
        self.compress_input.setMinimumWidth(width)
        self.compress_input.setMaximumWidth(width)
        self.density_input.setMinimumWidth(width)
        self.density_input.setMaximumWidth(width)
        # Pour les résultats optionnels
        if hasattr(self, 'result_EI_input'):
            self.result_EI_input.setMinimumWidth(width)
            self.result_EI_input.setMaximumWidth(width)
        if hasattr(self, 'result_Cc_input'):
            self.result_Cc_input.setMinimumWidth(width)
            self.result_Cc_input.setMaximumWidth(width)
        if hasattr(self, 'result_Ck_input'):
            self.result_Ck_input.setMinimumWidth(width)
            self.result_Ck_input.setMaximumWidth(width)

    def set_other_page(self, other_page):
    
        self._other_page = other_page

    def _sync_type_sol(self, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            self._other_page.type_sol_input.setText(value)
            self._other_page._syncing = False

    def _sync_pores(self, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            self._other_page.pores_input.setText(value)
            self._other_page._syncing = False

    def _sync_compress(self, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            self._other_page.compress_input.setText(value)
            self._other_page._syncing = False

    def _sync_density(self, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            self._other_page.density_input.setText(value)
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

    def _on_custom_type_edited(self):
        self._custom_type_edited = True

    def _on_custom_check_changed(self, state):
        if state == Qt.CheckState.Checked.value:
            self._custom_ei_edited = False
            self._custom_cc_edited = False
            self._custom_type_edited = False

    def _update_combo_state(self, combo: QComboBox):
        """Update the enabled state and style of a combo box based on number of items"""
        has_multiple_options = combo.count() > 1
        combo.setEnabled(has_multiple_options)
        
        if not has_multiple_options:
            combo.setStyleSheet("""
                QComboBox {
                    background-color: #f0f0f0;
                    color: #666666;
                    border: 1px solid #cccccc;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                }
            """)
        else:
            combo.setStyleSheet("")

    def export_to_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en PDF", "", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        try:
            # 1. Construire le HTML avec les entrées utilisateur
            html = "<h2 style='color:#007bff;'>Entered Parameters</h2><ul>"
            html += f"<li><b>{self.type_sol.currentText()}</b>: {self.type_sol_input.text()} {self.type_sol_unit.currentText()}</li>"
            html += f"<li><b>{self.pores_sol.currentText()}</b>: {self.pores_input.text()} {self.pores_sol_unit.currentText()}</li>"
            html += f"<li><b>{self.compress_sol.currentText()}</b>: {self.compress_input.text()} {self.compress_sol_unit.currentText()}</li>"
            html += f"<li><b>Specific gravity of solids</b>: {self.density_input.text()}</li></ul>"

            # 2. Ajouter les résultats
            html += "<h2 style='color:#007bff;'>Results</h2><ul>"
            for i in range(self.results_display.results_layout.count()):
                widget = self.results_display.results_layout.itemAt(i).widget()
                if widget:
                    html += f"<li>{widget.text()}</li>"
            html += "</ul>"

            # 3. Exporter le graphique temporairement
            temp_dir = tempfile.gettempdir()
            graph_path = os.path.join(temp_dir, "graph_tassement_export.png")
            self.graph_viewer.canvas.figure.savefig(graph_path, dpi=150)

            # 4. Ajouter le graphique dans le HTML
            html += "<h2 style='color:#007bff;'>Graph</h2>"
            html += f"<img src='{graph_path}' width='600' />"

            # 5. Créer et écrire le document PDF
            doc = QTextDocument()
            doc.setHtml(html)

            printer = QPrinter()
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)

            painter = QPainter()
            if not painter.begin(printer):
                QMessageBox.critical(self, "Error", "Unable to open the file for writing.")
                return

            doc.drawContents(painter)
            painter.end()

            QMessageBox.information(self, "Export PDF", "The file has been successfully exported.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
