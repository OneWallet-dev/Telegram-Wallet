import io

import qrcode


async def qr_code(wallet):
    qr_img = qrcode.make(str(wallet))
    bio = io.BytesIO()
    qr_img.save(bio, 'PNG')
    bio.seek(0)
    return bio.read()
