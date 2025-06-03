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

    w_pt, h_pt = 594 * mm, 841 * mm  # A1 Format
    margin = 50 * mm  # 5cm Abstand von allen Rändern
    usable_w = w_pt - 2 * margin
    usable_h = h_pt - 2 * margin
    box_w, box_h = usable_w / module_count, usable_h / module_count
    eps = 0.05 * mm

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(w_pt, h_pt))

    c.setTitle("recursive_poster")
    c.setAuthor("neuerstandard")
    c.setSubject("A recursively generated poster that encodes a link to its own identical copy.")

    # Hintergrund: Rot (#FF0004)
    c.setFillColorRGB(1, 0, 0.0157)  # FF0004 in RGB (1, 0, 0.0157)

    c.rect(0, 0, w_pt, h_pt, fill=1, stroke=0)

    # QR-Code: Schwarz (#000000)
    c.setFillColorRGB(0, 0, 0)

    for r, row in enumerate(matrix):
        for cidx, bit in enumerate(row):
            if bit:
                x = margin + cidx * box_w - eps
                y = h_pt - margin - (r + 1) * box_h - eps
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
