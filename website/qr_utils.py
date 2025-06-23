# qr_utils.py

import qrcode
import io
import base64

def generate_qr_code_base64(data: str) -> str:
    """
    Generates a QR code as a base64-encoded PNG string from the given data.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)

    return base64.b64encode(img_io.getvalue()).decode('utf-8')
