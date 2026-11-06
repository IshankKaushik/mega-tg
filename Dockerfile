FROM python:3.10-slim

# THIS IS THE IMPORTANT LINE: Make sure 'git' is in this list!
RUN apt-get update && apt-get install -y ffmpeg megatools git ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
