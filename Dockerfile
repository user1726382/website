FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates clamav clamav-freshclam && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Fetch antivirus definitions at image build; update signatures on a maintenance schedule.
RUN freshclam || true
COPY . ./
RUN mkdir -p /app/data /app/private_uploads /app/media_uploads && useradd -u 10001 -m website && chown -R website:website /app/data /app/private_uploads /app/media_uploads
USER website
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
