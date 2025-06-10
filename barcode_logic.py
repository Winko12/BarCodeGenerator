# FILE: barcode_logic.py
# PURPOSE: Handles barcode generation, label creation, and PDF export.
# VERSION: 4.5 (Convenience Update)

import os
from io import BytesIO
import re # Import re for auto-increment
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image, ImageDraw, ImageFont

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

def get_supported_barcodes():
    """Returns the full list of supported barcode types from the library."""
    return barcode.PROVIDED_BARCODES

def auto_increment_string(text):
    """
    --- NEW HELPER FUNCTION ---
    Finds a number at the end of a string and increments it.
    """
    if not text:
        return "1"
    match = re.match(r'^(.*?)(\d+)$', text)
    if match:
        prefix, number_str = match.groups()
        new_number_str = str(int(number_str) + 1).zfill(len(number_str))
        return f"{prefix}{new_number_str}"
    return None # Indicates failure to increment

def generate_raw_barcode(data, barcode_type):
    """Generates only the barcode image itself (as a PIL Image)."""
    if barcode_type.lower() == "qr code":
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white").convert('RGB')
    else:
        barcode_class = barcode.get_barcode_class(barcode_type)
        writer = ImageWriter(format='PNG')
        buffer = BytesIO()
        barcode_instance = barcode_class(data, writer=writer)
        barcode_instance.write(buffer)
        buffer.seek(0)
        return Image.open(buffer).convert('RGB')

def generate_barcode_with_label(barcode_img, product_name, price, font_top, font_bottom, logo_path=None):
    """Takes a raw barcode PIL Image and adds text and an optional logo."""
    padding = 15
    logo_height, logo_img = 0, None
    if logo_path and os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_height = 60
        logo_img = logo_img.resize((int(logo_img.width * logo_height / logo_img.height), logo_height), Image.Resampling.LANCZOS)
    
    name_bbox = font_top.getbbox(product_name) if product_name else (0,0,0,0)
    price_bbox = font_bottom.getbbox(price) if price else (0,0,0,0)

    name_width, name_height = name_bbox[2] - name_bbox[0], name_bbox[3] - name_bbox[1]
    price_width, price_height = price_bbox[2] - price_bbox[0], price_bbox[3] - price_bbox[1]
    
    extra_height = 0
    if logo_img: extra_height += logo_height + padding
    if product_name: extra_height += name_height + padding
    if price: extra_height += price_height + padding
    if not any((product_name, price, logo_img)): extra_height = padding

    new_width = max(barcode_img.width, name_width, price_width, logo_img.width if logo_img else 0) + (padding * 2)
    new_height = barcode_img.height + extra_height + padding

    label_img = Image.new("RGB", (int(new_width), int(new_height)), "white")
    draw = ImageDraw.Draw(label_img)
    current_y = padding

    if logo_img:
        label_img.paste(logo_img, ((label_img.width - logo_img.width) // 2, current_y), logo_img)
        current_y += logo_height + padding
    
    label_img.paste(barcode_img, ((label_img.width - barcode_img.width) // 2, current_y))
    current_y += barcode_img.height + padding
    
    if product_name:
        draw.text(((label_img.width - name_width) // 2, current_y), product_name, fill="black", font=font_top)
        current_y += name_height + (padding // 2)
    if price:
        draw.text(((label_img.width - price_width) // 2, current_y), price, fill="black", font=font_bottom)
    
    return label_img

def export_to_pdf(image_list, save_path):
    """Arranges a list of PIL Image objects onto a PDF grid."""
    c = canvas.Canvas(save_path, pagesize=letter)
    width, height = letter
    cols, rows = 3, 10
    margin_x, margin_y = 0.5 * inch, 0.5 * inch
    label_width = (width - 2 * margin_x) / cols
    label_height = (height - 2 * margin_y) / rows
    
    x, y, count = margin_x, height - margin_y - label_height, 0
    for img in image_list:
        if count >= (cols * rows):
            c.showPage()
            count, x, y = 0, margin_x, height - margin_y - label_height
            
        buffer = BytesIO()
        img.save(buffer, format='png')
        buffer.seek(0)
        
        img_aspect = img.height / img.width if img.width > 0 else 0
        cell_aspect = label_height / label_width
        
        if img_aspect > cell_aspect:
            img_h, img_w = label_height * 0.9, (label_height * 0.9) / img_aspect if img_aspect > 0 else 0
        else:
            img_w, img_h = label_width * 0.9, (label_width * 0.9) * img_aspect

        c.drawImage(ImageReader(buffer), x + (label_width - img_w) / 2, y + (label_height - img_h) / 2, width=img_w, height=img_h)
        
        x += label_width
        if (count + 1) % cols == 0: x, y = margin_x, y - label_height
        count += 1
        
    c.save()