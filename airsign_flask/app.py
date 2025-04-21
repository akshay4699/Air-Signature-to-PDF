import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'air_sign_secret'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# === Utility Functions ===

def auto_crop_signature(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(thresh)
    if coords is None:
        raise ValueError("No signature detected.")
    x, y, w, h = cv2.boundingRect(coords)
    cropped = img[y:y + h, x:x + w]
    cropped_path = os.path.join(app.config['UPLOAD_FOLDER'], "cropped_signature.png")
    cv2.imwrite(cropped_path, cropped)
    return cropped_path

def make_signature_transparent(sig_img_path):
    sig_img = Image.open(sig_img_path).convert("RGBA")
    datas = sig_img.getdata()
    new_data = []
    for item in datas:
        if item[0] in range(240, 256) and item[1] in range(240, 256) and item[2] in range(240, 256):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    sig_img.putdata(new_data)
    transparent_path = os.path.join(app.config['UPLOAD_FOLDER'], "signature_transparent.png")
    sig_img.save(transparent_path)
    return transparent_path

def search_signature_in_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_instances = page.search_for("Signature")
        if text_instances:
            return page_num, text_instances[0]
    return None, None

def insert_signature_into_pdf(pdf_path, sig_img_path, output_pdf_path, insert_x, insert_y, page_num, sig_scale=0.35):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    sig_img = Image.open(sig_img_path)
    width, height = sig_img.size
    new_w, new_h = int(width * sig_scale), int(height * sig_scale)
    sig_img = sig_img.resize((new_w, new_h))
    sig_img.save(sig_img_path)

    # Convert to PDF coordinate space
    pdf_y = page.rect.height - insert_y - new_h * 0.7

    page.insert_image(
        fitz.Rect(insert_x, pdf_y, insert_x + new_w, pdf_y + new_h),
        filename=sig_img_path
    )
    doc.save(output_pdf_path)

# === Routes ===

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdf = request.files.get('pdf')
        signature = request.files.get('signature')

        if not pdf or not signature:
            flash("Both PDF and signature image are required.")
            return redirect(request.url)

        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename)
        sig_path = os.path.join(app.config['UPLOAD_FOLDER'], signature.filename)
        pdf.save(pdf_path)
        signature.save(sig_path)

        try:
            cropped_sig = auto_crop_signature(sig_path)
            transparent_sig = make_signature_transparent(cropped_sig)
            page_num, position = search_signature_in_pdf(pdf_path)

            if position:
                x, y, _, _ = position
                output_pdf = os.path.join(app.config['UPLOAD_FOLDER'], "signed_" + pdf.filename)
                insert_signature_into_pdf(pdf_path, transparent_sig, output_pdf, x, y, page_num)
                flash("✅ Signature inserted successfully.")
                return render_template('index.html', download_link="signed_" + pdf.filename)
            else:
                flash("❌ 'Signature' keyword not found in PDF.")
                return redirect(request.url)

        except Exception as e:
            flash(f"Error: {str(e)}")
            return redirect(request.url)

    return render_template('index.html')


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# === Start App ===
if __name__ == '__main__':
    app.run(debug=True)
