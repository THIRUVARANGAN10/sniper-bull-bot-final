FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sniper_bull_bot.py .

CMD ["python", "sniper_bull_bot.py"]
