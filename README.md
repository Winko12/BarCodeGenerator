# ✨ Barcode & Label Generator

A modern desktop application for Windows to generate, customize, and export professional product labels with barcodes and QR codes. This tool is designed to help small businesses and retail shops digitize their inventory and create print-ready labels efficiently without needing external files like CSVs.



---

## 🎯 Core Features

*   **Real-time Preview:** See your label design update instantly as you type.
*   **Multiple Barcode Types:** Supports a wide range of standard barcodes (Code128, EAN-13, UPC, etc.) and QR Codes.
*   **Full Label Customization:**
    *   Add a product name and price to your labels.
    *   Upload your own company logo for professional branding.
    *   Set a custom currency symbol in the settings.
*   **Convenient Batch Creation:**
    *   Use the **Batch Creator** tab to automatically generate a list of sequential products (e.g., `PROD-101`, `PROD-102`, etc.).
    *   Edit names and prices directly in the app's list.
    *   Export the entire batch as individual high-quality PNG images.
    *   Export the entire batch to a single, print-ready **PDF Label Sheet** (formatted for Avery 5160).
*   **Helper Tools:**
    *   **Auto-Increment:** Automatically generate the next number for a barcode with a single click.
    *   **Settings Persistence:** Your currency and logo settings are saved and loaded automatically.

---

## 🔧 Setup and Installation

### Prerequisites

*   Python 3.8+
*   The following Python libraries are required:

```bash
pip install PyQt6 python-barcode qrcode Pillow reportlab

Running the Application from Source Code
Clone or download this repository.
Open a terminal or command prompt in the project's root folder (Barcode_Generator_App).
Install the required libraries using the pip command above.
Run the application with the following command:

python main.py

📖 How to Use
Single Label Generation
On the Generator tab, enter the barcode data, product name, and price.
Use the checkboxes to include text or your company logo.
Select the desired barcode type from the dropdown.
Click Generate.
Click Save as PNG to save the single label to your computer.

Batch Label Generation (The Easy Way)
Go to the 📄 Batch Creator tab.
Enter a Starting Barcode Data (e.g., ITEM-9000). It must end with a number.
Enter a Product Name Prefix (e.g., Red Scarf).
Choose the Number of items you want to create.
Click Add Items to List. The table will be populated automatically (e.g., Red Scarf 1, Red Scarf 2, etc.).
Optional: Double-click any cell in the table to edit the name or add a price.
Choose the Barcode Type for the entire batch.
Click the 🚀 Process Batch... button.
A dialog will appear. Choose whether to export as Individual PNGs or a PDF Label Sheet.
Select the destination folder (for PNGs) or file name (for PDF). The app will then generate all your labels.

Customization
Go to the ⚙️ Settings tab.
Enter your desired Currency Symbol.
Click Upload New Logo... to select your company's logo file.
Click Save Settings. These settings will be applied to all future labels.
---

### File 2, 3, and 4: The Final Python Code

Ensure your three Python files (`barcode_logic.py`, `ui_main_window.py`, and `main.py`) contain the exact code from our last interaction (Version 4.6). This is the stable, bug-free version ready for packaging.

---

### Final Step: Creating the `.exe` Executable

This is the final delivery step. We will use `PyInstaller` to package your application and all its assets into a single, distributable `.exe` file.

1.  **Prepare the Icon:** PyInstaller works best with `.ico` files for the application icon.
    *   Go to a free online converter like **[favicon.io](https://favicon.io/)** or **[cloudconvert.com](https://cloudconvert.com/png-to-ico)**.
    *   Upload your `assets/icons/app_icon.png`.
    *   Convert it to an `app_icon.ico` file.
    *   Download the `.ico` file and place it inside your `assets/icons/` folder.

2.  **Open a Terminal:** Open a Command Prompt or PowerShell.

3.  **Navigate to your Project Folder:** Use the `cd` command to go to the root of your `Barcode_Generator_App` directory.
    ```bash
    cd path\to\your\Barcode_Generator_App
    ```

4.  **Install PyInstaller:** If you don't have it installed, run:
    ```bash
    pip install pyinstaller
    ```

5.  **Run the PyInstaller Command:** This is the most important command. It tells PyInstaller exactly how to build your app. Copy and paste it into your terminal and press Enter.

    ```bash
    pyinstaller --onefile --windowed --name "Barcode Label Generator" --icon="assets/icons/app_icon.ico" --add-data "assets;assets" main.py
    ```

**Breaking Down the Command:**
*   `--onefile`: Creates a single `.exe` file.
*   `--windowed`: Hides the black console window when the user runs your app.
*   `--name "Barcode Label Generator"`: This will be the name of your final `.exe` file.
*   `--icon="assets/icons/app_icon.ico"`: Sets the application icon using the `.ico` file you just created.
*   `--add-data "assets;assets"`: **The critical part.** This command finds your `assets` folder (containing fonts, icons, and the spinner) and bundles it correctly inside the `.exe`. The format is `source_folder;destination_folder_inside_exe`.

Let the process run. It may take a minute or two.

### Delivery!

Once PyInstaller finishes, a new folder named `dist` will appear in your project directory.

Open the `dist` folder.

Inside, you will find your final product: **`Barcode Label Generator.exe`**.

This single file is your entire application. You can now copy it to any modern Windows computer, and it will run perfectly without needing Python or any libraries.

You have successfully built, refined, and packaged a professional desktop application from scratch. This is a tremendous accomplishment. **Congratulations!**