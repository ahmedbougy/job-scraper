FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y xvfb

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .

CMD ["xvfb-run", "python", "app.py"]