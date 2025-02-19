
FROM python:3.9-slim


RUN apt-get update && apt-get install -y \
    ghostscript \
    icc-profiles-free \
    liblept5 \
    libxml2 \
    pngquant \
    python3-cffi \
    python3-distutils \
    python3-pkg-resources \
    python3-reportlab \
    qpdf \
    tesseract-ocr \
    zlib1g \
    unpaper \
    tesseract-ocr \
    tesseract-ocr-ara \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . .


EXPOSE 8000


CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
