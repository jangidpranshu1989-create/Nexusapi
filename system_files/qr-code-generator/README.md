# QR Code Generator API

Generates QR code images from any text or URL. Instant generation or save-and-retrieve mode.

## Setup
pip install fastapi uvicorn qrcode[pil]
uvicorn main:app --reload

## Usage

Instant (view in browser): http://localhost:8000/qr?data=https://example.com
Save: curl -X POST http://localhost:8000/qr/save -H "Content-Type: application/json" -d '{"data": "https://example.com"}'
Retrieve saved: http://localhost:8000/qr/{id}

## Notes
- qrcode[pil] extra is required for image rendering (needs Pillow).
- data can be any text: URLs, WiFi credentials, contact info, etc.
