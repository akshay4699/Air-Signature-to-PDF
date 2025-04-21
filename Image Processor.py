import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image

# === Step 1: Auto-crop the signature ===
def auto_crop_signature(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(thresh)
    x, y, w, h = cv2.boundingRect(coords)
    cropped = img[y:y+h, x:x+w]
    cv2.imwrite("signature_output_cropped.png", cropped)
    return "signature_output_cropped.png"

# === Step 2: Extract PDF as image ===
def pdf_to_image(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=200)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    return img, page.rect.width, page.rect.height

# === Step 3: Search for the word "Signature" in the PDF ===
def search_signature_in_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_instances = page.search_for("Signature")  # Search for the word "Signature"
        if text_instances:
            # Return the first match (top-left corner of the bounding box of the word "Signature")
            return text_instances[0]
    return None  # Return None if the word "Signature" is not found

# === Step 4: Convert the signature to a transparent PNG ===
def make_signature_transparent(sig_img_path):
    sig_img = Image.open(sig_img_path).convert("RGBA")  # Ensure it's in RGBA mode (with alpha channel)
    datas = sig_img.getdata()

    # Replace white pixels with transparency (assuming the signature is on a white background)
    new_data = []
    for item in datas:
        # Change all white (also shades of whites) pixels to transparent
        if item[0] in range(240, 256) and item[1] in range(240, 256) and item[2] in range(240, 256):
            new_data.append((255, 255, 255, 0))  # Transparent pixel
        else:
            new_data.append(item)  # Keep other pixels as is
    sig_img.putdata(new_data)

    transparent_sig_path = "signature_transparent.png"
    sig_img.save(transparent_sig_path)  # Save with transparency
    return transparent_sig_path

# === Step 5: Insert signature into PDF ===
def insert_signature_into_pdf(pdf_path, output_pdf, sig_img_path, insert_x, insert_y, sig_scale=0.35):
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Convert the signature to have transparency
    transparent_sig_path = make_signature_transparent(sig_img_path)
    
    # Open transparent signature image
    sig_img = Image.open(transparent_sig_path)
    
    # Resize signature
    width, height = sig_img.size
    new_w, new_h = int(width * sig_scale), int(height * sig_scale)
    sig_img = sig_img.resize((new_w, new_h))

    # Save resized transparent signature for insertion
    sig_img.save(transparent_sig_path)

    # Convert to PDF coordinates
    page_w, page_h = page.rect.width, page.rect.height
    pdf_x, pdf_y = insert_x, insert_y  # Position found from "Signature" search

    # Slightly adjust upward
    pdf_y -= new_h * 0.3  # Adjust positioning if necessary

    page.insert_image(
        fitz.Rect(pdf_x, pdf_y, pdf_x + new_w, pdf_y + new_h),
        filename=transparent_sig_path
    )
    doc.save(output_pdf)
    print(f"✅ Signature inserted into '{output_pdf}'")

# === Main Execution ===
pdf_path = "input.pdf"
sig_image = "signature_output.png"
output_pdf = "output_with_signature.pdf"

# Crop signature
sig_cropped = auto_crop_signature(sig_image)

# Search for the word "Signature" in the PDF
position = search_signature_in_pdf(pdf_path)

if position:
    x, y, _, _ = position  # Extract the x, y coordinates from the bounding box of the word "Signature"
    print(f"🧭 Found 'Signature' at position: ({x}, {y})")

    # Insert the transparent signature into the PDF at the found position
    insert_signature_into_pdf(pdf_path, output_pdf, sig_cropped, x, y)
else:
    print("❌ The word 'Signature' was not found in the PDF.")
