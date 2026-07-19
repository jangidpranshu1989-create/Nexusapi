# File Upload Service API

Accepts file uploads, validates type and size, stores safely on disk with unique names.

## Features
- Multipart upload with extension whitelist (images, PDFs, docs, zip, csv, txt)
- Max file size enforcement (default 10MB)
- Files stored with UUID names — original filenames kept as metadata
- List, view, download, delete endpoints

## Setup

pip install fastapi uvicorn python-multipart
uvicorn main:app --reload

## Usage

Upload:
curl -X POST http://localhost:8000/upload -F "file=@/path/to/file.pdf"

List:
curl http://localhost:8000/files

Download:
curl http://localhost:8000/files/1/download -o downloaded_file.pdf

Delete:
curl -X DELETE http://localhost:8000/files/1

## Notes
- No authentication in this starter — add auth before exposing publicly.
- For production scale, consider cloud storage (S3) instead of local disk.
