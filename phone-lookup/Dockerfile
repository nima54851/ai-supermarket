FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
RUN mkdir -p logs

ENV BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ENV LOG_LEVEL=INFO

CMD ["python3", "bot.py"]
