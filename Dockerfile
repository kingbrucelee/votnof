# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole source
COPY . .

# Use python -m src.main to run the bot
CMD ["python", "-m", "src.main"]
