import cv2
import numpy as np
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter

# Load signature
signature = cv2.imread("signature_output.png")

# STEP 1: Auto-crop the drawn signature area
gray = cv2.cvtColor(signature, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)  # Invert white bg

coords = cv2.findNonZero(thresh)
x, y, w, h = cv2.boundingRect(coords)
cropped_signature = signature[y:y+h, x:x+w]

# STEP 2: Smooth signature lines (optional, can be adjusted)
gray_cropped = cv2.cvtColor(cropped_signature, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray_cropped, (5, 5), 0)
_, smooth_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
smoothed_signature = cv2.cvtColor(smooth_thresh, cv2.COLOR_GRAY2BGR)

# Save the smoothed cropped signature
signature_path = "signature_cleaned.png"
cv2.imwrite(signature_path, smoothed_signature)

# STEP 3: Insert the signature into a PDF

# Create blank A4 PDF
pdf = FPDF()
pdf.add_page()

# Add the signature image at bottom right
pdf.image(signature_path, x=140, y=240, w=50)  # Adjust x, y, w for position/scale

# Save the final PDF
output_pdf_path = "signed_output.pdf"
pdf.output(output_pdf_path)

print(f"✅ Signature inserted and saved as: {output_pdf_path}")
