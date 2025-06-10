# FILE: ui_main_window.py
# PURPOSE: Main application with Generator, Batch Creator, and Settings tabs.
# VERSION: 4.7 (Final Polish)

import sys, os, re, time, json, shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QComboBox, QLabel, QFileDialog, QFrame, QGraphicsDropShadowEffect, 
    QMessageBox, QCheckBox, QProgressBar, QTabWidget, QSpinBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea # --- FIX 1: Import QScrollArea ---
)
from PyQt6.QtGui import QPixmap, QIcon, QMovie
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PIL import ImageQt, ImageFont as PIL_ImageFont
from barcode_logic import (
    generate_raw_barcode, generate_barcode_with_label, get_supported_barcodes, 
    export_to_pdf, auto_increment_string
)

SETTINGS_FILE, LOGO_FILE = "data/settings.json", "data/company_logo.png"

APP_STYLESHEET = """
QWidget { font-family: 'Roboto', 'Segoe UI', 'Arial', sans-serif; font-size: 11pt; color: #212121; }
#MainWindow { background-color: #f0f2f5; }
QTabWidget::pane { border: none; }
QTabBar::tab { background-color: #e1e1e1; color: #333333; padding: 10px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: bold; }
QTabBar::tab:selected { background-color: #f0f2f5; border-bottom: 2px solid #0078d4; }
QLineEdit, QComboBox, QSpinBox { background-color: #ffffff; border: 1px solid #d0d0d0; border-radius: 8px; padding: 10px; font-size: 12pt; }
QPushButton#GenerateButton { background-color: #0078d4; color: #ffffff; border: none; border-radius: 8px; padding: 12px; font-size: 12pt; font-weight: bold; }
QPushButton { background-color: #e1e1e1; color: #333333; border: 1px solid #cccccc; border-radius: 8px; padding: 10px; }
QPushButton:hover { background-color: #d1d1d1; }
QPushButton:disabled { background-color: #f5f5f5; color: #a0a0a0; }
#PreviewCard, #SettingsCard, #BatchCard { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; }
#TitleLabel { font-size: 20pt; font-weight: bold; color: #003366; }
QLabel#Header { font-size: 14pt; font-weight: bold; color: #003366; }
QTableWidget { border: 1px solid #e0e0e0; border-radius: 8px; gridline-color: #f0f2f5; }
QHeaderView::section { background-color: #f0f2f5; padding: 4px; border: none; font-weight: bold; }
#ToastLabel { background-color: rgba(33, 150, 243, 230); color: white; font-size: 12pt; font-weight: bold; padding: 15px 30px; border-radius: 15px; }
QScrollArea { border: none; }
"""

class BarcodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = {}
        self.load_settings()
        try:
            self.font_regular = PIL_ImageFont.truetype("assets/fonts/Roboto-Regular.ttf", 24)
            self.font_bold = PIL_ImageFont.truetype("assets/fonts/Roboto-Bold.ttf", 32)
        except IOError:
            self.show_error_message("Font Error", "Could not load font files from 'assets/fonts'.")
            sys.exit(1)
        self.init_ui()

    def load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f: self.settings = json.load(f)
            else:
                self.settings = {"currency": "$", "logo_path": ""}
                os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
                self.save_settings()
        except Exception:
            self.settings = {"currency": "$", "logo_path": ""}

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f: json.dump(self.settings, f, indent=4)

    def init_ui(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("Barcode Label Generator")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        main_layout = QVBoxLayout(self)
        self.setFixedSize(560, 800)
        
        tab_widget = QTabWidget()
        generator_tab, batch_tab, settings_tab = QWidget(), QWidget(), QWidget()
        tab_widget.addTab(generator_tab, "Generator")
        tab_widget.addTab(batch_tab, "📄 Batch Creator")
        tab_widget.addTab(settings_tab, "⚙️ Settings")
        
        self.create_generator_tab_layout(generator_tab)
        self.create_batch_creator_tab_layout(batch_tab)
        self.create_settings_tab_layout(settings_tab)
        main_layout.addWidget(tab_widget)
        self.setStyleSheet(APP_STYLESHEET)

    def create_generator_tab_layout(self, tab):
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 20, 25, 20); layout.setSpacing(15)
        
        # ... (title layout is the same)
        title_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("assets/icons/app_icon.png").scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio))
        title_label = QLabel("Barcode Generator"); title_label.setObjectName("TitleLabel")
        title_layout.addWidget(logo_label); title_layout.addSpacing(10)
        title_layout.addWidget(title_label); title_layout.addStretch()
        
        # ... (input layouts are the same)
        data_layout = QHBoxLayout()
        self.data_input_field = QLineEdit(); self.data_input_field.setPlaceholderText("Enter barcode data (e.g., ITEM-001)")
        self.auto_increment_button = QPushButton("Next #")
        data_layout.addWidget(self.data_input_field); data_layout.addWidget(self.auto_increment_button)
        product_info_layout = QHBoxLayout()
        self.product_name_input = QLineEdit(); self.product_name_input.setPlaceholderText("Product Name")
        self.price_input = QLineEdit(); self.price_input.setPlaceholderText(f"Price (e.g., {self.settings.get('currency', '$')}9.99)")
        product_info_layout.addWidget(self.product_name_input); product_info_layout.addWidget(self.price_input)
        options_layout = QHBoxLayout()
        self.include_text_checkbox = QCheckBox("Include Name & Price"); self.include_text_checkbox.setChecked(True)
        self.include_logo_checkbox = QCheckBox("Include Company Logo"); self.include_logo_checkbox.setChecked(os.path.exists(self.settings.get("logo_path", "")))
        options_layout.addWidget(self.include_text_checkbox); options_layout.addWidget(self.include_logo_checkbox); options_layout.addStretch()
        self.barcode_type_dropdown = QComboBox(); self.barcode_type_dropdown.addItems(["QR Code"] + get_supported_barcodes())
        self.generate_button = QPushButton("Generate"); self.generate_button.setObjectName("GenerateButton")
        
        # --- FIX 1: Create a Scroll Area for the Preview ---
        self.preview_card = QFrame(); self.preview_card.setObjectName("PreviewCard"); self.preview_card.setMinimumHeight(220)
        card_layout = QVBoxLayout(self.preview_card); card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.preview_image_label = QLabel("Preview will appear here")
        self.preview_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.preview_image_label) # Put the label inside the scroll area
        
        self.loading_spinner = QLabel()
        self.spinner_movie = QMovie("assets/spinner.gif")
        self.spinner_movie.setScaledSize(QSize(60, 60))
        self.loading_spinner.setMovie(self.spinner_movie)
        self.loading_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(self.loading_spinner)
        card_layout.addWidget(self.scroll_area) # Add the scroll area to the card
        self.loading_spinner.hide() # Initially hide spinner
        
        self.preview_card.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=25, color=Qt.GlobalColor.lightGray, xOffset=0, yOffset=3))
        
        # ... (bottom buttons are the same)
        bottom_buttons_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset"); self.save_button = QPushButton("Save as PNG")
        self.save_button.setEnabled(False); self.reset_button.setEnabled(False)
        bottom_buttons_layout.addStretch(); bottom_buttons_layout.addWidget(self.reset_button); bottom_buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(title_layout); layout.addLayout(data_layout); layout.addLayout(product_info_layout)
        layout.addLayout(options_layout); layout.addWidget(self.barcode_type_dropdown); layout.addWidget(self.generate_button)
        layout.addSpacing(10); layout.addWidget(self.preview_card); layout.addStretch(); layout.addLayout(bottom_buttons_layout)
        
        self.generate_button.clicked.connect(self.handle_generate_barcode)
        self.save_button.clicked.connect(self.handle_save_barcode)
        self.reset_button.clicked.connect(self.handle_reset)
        self.auto_increment_button.clicked.connect(self.handle_auto_increment_data)

    def create_batch_creator_tab_layout(self, tab):
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 20, 25, 20); layout.setSpacing(15)
        
        form_card = QFrame(); form_card.setObjectName("BatchCard")
        form_layout = QVBoxLayout(form_card)
        form_header = QLabel("1. Create Batch List"); form_header.setObjectName("Header")
        self.batch_start_data = QLineEdit(); self.batch_start_data.setPlaceholderText("Starting Barcode Data (e.g., PROD-100)")
        self.batch_name_prefix = QLineEdit(); self.batch_name_prefix.setPlaceholderText("Product Name Prefix (e.g., Blue T-Shirt)")
        
        # --- FIX 2: Add Price Input to Batch Creator Form ---
        self.batch_price_input = QLineEdit()
        self.batch_price_input.setPlaceholderText("Price for all items (optional)")
        
        add_items_layout = QHBoxLayout()
        self.batch_item_count = QSpinBox(); self.batch_item_count.setRange(1, 1000); self.batch_item_count.setValue(10)
        add_items_button = QPushButton("Add Items to List")
        add_items_layout.addWidget(QLabel("Number of items:"))
        add_items_layout.addWidget(self.batch_item_count)
        add_items_layout.addWidget(add_items_button)
        
        form_layout.addWidget(form_header); form_layout.addWidget(self.batch_start_data)
        form_layout.addWidget(self.batch_name_prefix)
        form_layout.addWidget(self.batch_price_input) # Add the new price field here
        form_layout.addLayout(add_items_layout)

        self.batch_table = QTableWidget(); self.batch_table.setColumnCount(3)
        self.batch_table.setHorizontalHeaderLabels(["Barcode Data", "Product Name", "Price"])
        self.batch_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.batch_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)

        manage_buttons_layout = QHBoxLayout()
        remove_row_button = QPushButton("Remove Selected"); clear_all_button = QPushButton("Clear All")
        manage_buttons_layout.addStretch(); manage_buttons_layout.addWidget(remove_row_button); manage_buttons_layout.addWidget(clear_all_button)

        process_card = QFrame(); process_card.setObjectName("BatchCard")
        process_layout = QVBoxLayout(process_card)
        process_header = QLabel("2. Process Batch"); process_header.setObjectName("Header")
        self.batch_barcode_type = QComboBox(); self.batch_barcode_type.addItems(["QR Code"] + get_supported_barcodes())
        process_batch_button = QPushButton("🚀 Process Batch..."); process_batch_button.setObjectName("GenerateButton")
        self.batch_progress_bar = QProgressBar(); self.batch_progress_bar.setVisible(False)
        process_layout.addWidget(process_header); process_layout.addWidget(self.batch_barcode_type)
        process_layout.addWidget(process_batch_button); process_layout.addWidget(self.batch_progress_bar)

        layout.addWidget(form_card); layout.addWidget(self.batch_table)
        layout.addLayout(manage_buttons_layout); layout.addWidget(process_card)
        
        add_items_button.clicked.connect(self.handle_add_batch_items)
        remove_row_button.clicked.connect(self.handle_remove_batch_rows)
        clear_all_button.clicked.connect(lambda: self.batch_table.setRowCount(0))
        process_batch_button.clicked.connect(self.handle_process_created_batch)

    def create_settings_tab_layout(self, tab):
        # (This layout is the same as before)
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(25, 20, 25, 20); main_layout.setSpacing(20)
        currency_card = QFrame(); currency_card.setObjectName("SettingsCard")
        currency_layout = QVBoxLayout(currency_card); currency_header = QLabel("Currency"); currency_header.setObjectName("Header")
        currency_form_layout = QHBoxLayout(); currency_label = QLabel("Currency Symbol:")
        self.currency_input = QLineEdit(); self.currency_input.setText(self.settings.get("currency", "$")); self.currency_input.setMaxLength(5)
        currency_form_layout.addWidget(currency_label); currency_form_layout.addWidget(self.currency_input)
        currency_layout.addWidget(currency_header); currency_layout.addLayout(currency_form_layout)
        logo_card = QFrame(); logo_card.setObjectName("SettingsCard")
        logo_layout = QVBoxLayout(logo_card); logo_header = QLabel("Company Logo"); logo_header.setObjectName("Header")
        self.logo_preview_label = QLabel("No logo uploaded."); self.logo_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview_label.setMinimumHeight(80); self.logo_preview_label.setStyleSheet("border: 1px dashed #d0d0d0; border-radius: 8px;")
        logo_buttons_layout = QHBoxLayout(); upload_logo_button = QPushButton("Upload New Logo..."); remove_logo_button = QPushButton("Remove Logo")
        logo_buttons_layout.addWidget(upload_logo_button); logo_buttons_layout.addWidget(remove_logo_button)
        logo_layout.addWidget(logo_header); logo_layout.addWidget(self.logo_preview_label); logo_layout.addLayout(logo_buttons_layout)
        save_settings_button = QPushButton("Save Settings"); save_settings_button.setObjectName("GenerateButton")
        main_layout.addWidget(currency_card); main_layout.addWidget(logo_card); main_layout.addStretch(); main_layout.addWidget(save_settings_button)
        upload_logo_button.clicked.connect(self.handle_upload_logo)
        remove_logo_button.clicked.connect(self.handle_remove_logo)
        save_settings_button.clicked.connect(self.handle_save_settings)
        self.update_logo_preview()

    def handle_add_batch_items(self):
        start_data = self.batch_start_data.text()
        name_prefix = self.batch_name_prefix.text()
        price = self.batch_price_input.text() # Get price from new field
        count = self.batch_item_count.value()
        
        if not start_data:
            self.show_error_message("Input Required", "Please enter a starting barcode value.")
            return
            
        # Format the price with currency symbol, if needed
        currency = self.settings.get("currency", "$")
        if price and not price.startswith(currency):
            price = f"{currency}{price}"
            
        current_data = start_data
        for i in range(count):
            row_pos = self.batch_table.rowCount()
            self.batch_table.insertRow(row_pos)
            self.batch_table.setItem(row_pos, 0, QTableWidgetItem(current_data))
            name_suffix = f" {i+1}" if name_prefix else str(i+1)
            self.batch_table.setItem(row_pos, 1, QTableWidgetItem(f"{name_prefix}{name_suffix}"))
            self.batch_table.setItem(row_pos, 2, QTableWidgetItem(price)) # Set the price
            
            next_data = auto_increment_string(current_data)
            if next_data is None:
                self.show_error_message("Increment Error", f"Could not increment '{current_data}'.\nPlease use data ending in a number.")
                break
            current_data = next_data

    def handle_remove_batch_rows(self):
        selected_rows = sorted([index.row() for index in self.batch_table.selectionModel().selectedRows()], reverse=True)
        for row in selected_rows:
            self.batch_table.removeRow(row)

    def handle_process_created_batch(self):
        row_count = self.batch_table.rowCount()
        if row_count == 0:
            self.show_error_message("Empty List", "Please add items to the batch list before processing.")
            return
        
        msg_box = QMessageBox(self); msg_box.setWindowTitle("Select Output Format")
        msg_box.setText("How would you like to save the batch?")
        png_button = msg_box.addButton("Individual PNGs", QMessageBox.ButtonRole.ActionRole)
        pdf_button = msg_box.addButton("PDF Label Sheet", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(QMessageBox.StandardButton.Cancel); msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        if clicked_button == png_button: output_format = "png"
        elif clicked_button == pdf_button: output_format = "pdf"
        else: return

        if output_format == "png": save_location = QFileDialog.getExistingDirectory(self, "Select Folder to Save PNGs")
        else: save_location, _ = QFileDialog.getSaveFileName(self, "Save PDF As", os.path.join(os.path.expanduser('~'), 'Desktop', "product_labels.pdf"), "PDF Files (*.pdf)")
        if not save_location: return

        try:
            items_to_process = []
            for row in range(row_count):
                data = self.batch_table.item(row, 0).text() if self.batch_table.item(row, 0) else ""
                name = self.batch_table.item(row, 1).text() if self.batch_table.item(row, 1) else ""
                price = self.batch_table.item(row, 2).text() if self.batch_table.item(row, 2) else ""
                items_to_process.append((data, name, price))

            self.batch_progress_bar.setVisible(True); self.batch_progress_bar.setMaximum(len(items_to_process))
            generated_images = []
            logo_path = self.settings.get("logo_path") # Batch uses settings, not checkbox
            currency, barcode_type = self.settings.get("currency", "$"), self.batch_barcode_type.currentText()
            
            for i, (data, name, price) in enumerate(items_to_process):
                if price and not price.startswith(currency): price = f"{currency}{price}"
                raw_img = generate_raw_barcode(data, barcode_type)
                final_img = generate_barcode_with_label(raw_img, name, price, self.font_regular, self.font_bold, logo_path)
                
                if output_format == "png":
                    filename = f"{name.replace(' ', '_').replace('/', '-')}_{data}.png"
                    final_img.save(os.path.join(save_location, filename), "PNG")
                else: generated_images.append(final_img)
                self.batch_progress_bar.setValue(i + 1); QApplication.processEvents()

            if output_format == "pdf": export_to_pdf(generated_images, save_location)
            self.show_toast(f"✅ Batch complete! {len(items_to_process)} items processed.")
        except Exception as e: self.show_error_message("Batch Error", f"An error occurred.\n\nError: {e}")
        finally: self.batch_progress_bar.setVisible(False)

    def update_logo_preview(self):
        logo_path = self.settings.get("logo_path", "")
        if logo_path and os.path.exists(logo_path):
            self.logo_preview_label.setPixmap(QPixmap(logo_path).scaled(self.logo_preview_label.width(), self.logo_preview_label.height() - 10, Qt.AspectRatioMode.KeepAspectRatio))
        else: self.logo_preview_label.setText("No logo uploaded.")

    def handle_upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Logo Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            shutil.copy(file_path, LOGO_FILE); self.settings["logo_path"] = LOGO_FILE
            self.update_logo_preview(); self.show_toast("✅ Logo uploaded! Click Save.")
        
    def handle_remove_logo(self):
        if os.path.exists(LOGO_FILE): os.remove(LOGO_FILE)
        self.settings["logo_path"] = ""; self.update_logo_preview(); self.show_toast("Logo removed. Click Save.")
        
    def handle_save_settings(self):
        self.settings["currency"] = self.currency_input.text()
        self.save_settings()
        self.price_input.setPlaceholderText(f"Price (e.g., {self.settings.get('currency', '$')}9.99)")
        self.show_toast("✅ Settings Saved!")

    def show_loading(self, show=True):
        if show:
            self.scroll_area.hide() # Hide scroll area
            self.loading_spinner.show()
            self.spinner_movie.start()
        else:
            self.spinner_movie.stop()
            self.loading_spinner.hide()
            self.scroll_area.show() # Show scroll area again
    
    def handle_auto_increment_data(self):
        new_data = auto_increment_string(self.data_input_field.text())
        if new_data: self.data_input_field.setText(new_data)
        else: self.show_toast("Cannot increment: data must end with a number.")

    def handle_generate_barcode(self):
        data = self.data_input_field.text()
        if not data:
            self.show_error_message("Input Data Required", "Please enter some data.")
            return

        self.show_loading(True)
        self.generate_button.setEnabled(False)
        
        currency = self.settings.get("currency", "$")
        price_text = self.price_input.text()
        if price_text and not price_text.startswith(currency):
            price_text = f"{currency}{price_text}"
        
        QTimer.singleShot(50, lambda: self.generate_and_display(
            data, self.barcode_type_dropdown.currentText(), self.product_name_input.text(),
            price_text, self.settings.get("logo_path") if self.include_logo_checkbox.isChecked() else None))

    def generate_and_display(self, data, barcode_type, product_name, price, logo_path):
        try:
            raw_barcode_img = generate_raw_barcode(data, barcode_type)
            use_text = self.include_text_checkbox.isChecked() and (product_name or price)
            use_logo = self.include_logo_checkbox.isChecked() and logo_path and os.path.exists(logo_path)
            
            if use_text or use_logo:
                self.generated_barcode_image = generate_barcode_with_label(
                    raw_barcode_img, product_name if use_text else "", price if use_text else "", 
                    self.font_regular, self.font_bold, logo_path if use_logo else None)
            else:
                self.generated_barcode_image = raw_barcode_img
            
            self.current_barcode_type = barcode_type
            q_image = ImageQt.ImageQt(self.generated_barcode_image.convert("RGBA"))
            pixmap = QPixmap.fromImage(q_image)
            # The label no longer needs scaling, it will just take its natural size inside the scroll area
            self.preview_image_label.setPixmap(pixmap)
            
            self.save_button.setEnabled(True)
            self.reset_button.setEnabled(True)
        except Exception as e:
            self.generated_barcode_image = None
            self.save_button.setEnabled(False)
            self.preview_image_label.setText("Generation Failed")
            self.show_error_message("Generation Error", f"Could not generate barcode.\n\nError: {e}")
        finally:
            self.show_loading(False)
            self.generate_button.setEnabled(True)

    def handle_save_barcode(self):
        if not self.generated_barcode_image:
            self.show_error_message("No Barcode", "Please generate a barcode first.")
            return

        name = self.product_name_input.text().replace(" ", "_").replace("/", "-") or self.current_barcode_type.replace(' ', '_')
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Barcode As", 
            os.path.join(os.path.expanduser('~'), 'Desktop', f"{name}_{self.data_input_field.text()}.png"), "PNG Images (*.png)")
        if save_path:
            self.generated_barcode_image.save(save_path, "PNG")
            self.show_toast("✅ Saved Successfully!")
                
    def handle_reset(self):
        self.data_input_field.clear()
        self.product_name_input.clear()
        self.price_input.clear()
        self.barcode_type_dropdown.setCurrentIndex(0)
        self.preview_image_label.setText("Preview will appear here")
        self.generated_barcode_image = None
        self.save_button.setEnabled(False)
        self.reset_button.setEnabled(False)

    def show_error_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("QMessageBox { background-color: #f0f2f5; } QLabel { color: #212121; }")
        msg_box.exec()
        
    def show_toast(self, message):
        toast = QLabel(message, self)
        toast.setObjectName("ToastLabel")
        toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toast_width = toast.fontMetrics().boundingRect(message).width() + 60
        toast_height = 50
        x = (self.width() - toast_width) // 2
        start_pos, end_pos = QRect(x, -toast_height, toast_width, toast_height), QRect(x, 20, toast_width, toast_height)
        toast.setGeometry(start_pos)
        toast.show()
        
        self.anim = QPropertyAnimation(toast, b"geometry", self)
        self.anim.setDuration(500); self.anim.setStartValue(start_pos); self.anim.setEndValue(end_pos)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic); self.anim.start()
        QTimer.singleShot(2500, lambda: self.hide_toast(toast))

    def hide_toast(self, toast):
        if not toast or not toast.parent(): return
        start_pos = toast.geometry()
        end_pos = QRect(start_pos.x(), -start_pos.height(), start_pos.width(), start_pos.height())
        self.anim_out = QPropertyAnimation(toast, b"geometry", self)
        self.anim_out.setDuration(500); self.anim_out.setStartValue(start_pos); self.anim_out.setEndValue(end_pos)
        self.anim_out.setEasingCurve(QEasingCurve.Type.InCubic); self.anim_out.finished.connect(toast.deleteLater); self.anim_out.start()