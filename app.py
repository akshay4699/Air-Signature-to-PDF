from flask import Flask, render_template_string, send_file, redirect, url_for
import subprocess
import os

app = Flask(__name__)

# HTML Template embedded for simplicity
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🖋️ Sign PDF via Webcam</title>
</head>
<body style="font-family: Arial; padding: 20px;">
    <h1>📸 Sign PDF via Webcam & Download</h1>

    {% if error %}
        <p style="color:red;">Error: {{ error }}</p>
    {% endif %}

    <form method="POST" action="/sign">
        <button type="submit" style="padding: 10px 20px;">Capture Signature & Sign PDF</button>
    </form>

    {% if signed %}
        <p>✅ PDF signed successfully.</p>
        <a href="{{ url_for('download') }}">Download Signed PDF</a>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML, signed=False)

@app.route("/sign", methods=["POST"])
def sign_pdf():
    try:
        # Step 1: Run Signature Capture Script
        subprocess.run(["python", "Signature Capture.py"], check=True)

        # Step 2: Run PDF Processing Script
        subprocess.run(["python", "Image Processor.py"], check=True)

        return render_template_string(HTML, signed=True)
    except subprocess.CalledProcessError as e:
        return render_template_string(HTML, error=str(e), signed=False)

@app.route("/download")
def download():
    return send_file("output_with_signature.pdf", as_attachment=True)
    
if __name__ == "__main__":
    app.run(debug=True)
