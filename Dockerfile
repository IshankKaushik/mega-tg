FROM python:3.10-slim

# We only need ffmpeg (for video processing), git (to download pyrogram), and ca-certificates.
RUN apt-get update && apt-get install -y ffmpeg git ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
