from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def create_test_pdf(filename="input.pdf"):
    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER

    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 100, "Authorization Form")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 140, "This document is used to confirm the agreement between the user and the service provider.")
    c.drawString(100, height - 180, "Please sign below:")

    # Signature line
    c.line(100, height - 230, 300, height - 230)
    c.drawString(100, height - 250, "Signature")

    # Date line
    c.line(100, height - 290, 250, height - 290)
    c.drawString(100, height - 310, "Date:")

    c.save()
    print(f"[✓] Test PDF created → {filename}")

if __name__ == "__main__":
    create_test_pdf()
