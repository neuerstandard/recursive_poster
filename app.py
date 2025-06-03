import io
from flask import Flask, request, redirect, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import qrcode
from qrcode.constants import ERROR_CORRECT_H

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('/download')

@app.route('/download')
def download():
    url = request.url

    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=1, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    module_count = len(matrix)

    w_pt, h_pt = 841 * mm, 1189 * mm  # A0 Format
    box_w, box_h = w_pt / module_count, h_pt / module_count
    eps = 0.05 * mm

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(w_pt, h_pt))

    c.setTitle("recursive_poster")
    c.setAuthor("neuerstandard")
    c.setSubject("A recursively generated poster that encodes a link to its own identical copy.")

    # Hintergrund: Rot (#FF1C1C)
    c.setFillColorRGB(1, 0.1098, 0.1098)  # FF1C1C in RGB (1, 0.1098, 0.1098)

    c.rect(0, 0, w_pt, h_pt, fill=1, stroke=0)

    # QR-Code: Weiß (#FFFFFF)
    c.setFillColorRGB(1, 1, 1)

    for r, row in enumerate(matrix):
        for cidx, bit in enumerate(row):
            if bit:
                x = cidx * box_w - eps
                y = h_pt - (r + 1) * box_h - eps
                c.rect(x, y, box_w + 2 * eps, box_h + 2 * eps, fill=1, stroke=0)

    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='recursive_poster.pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
