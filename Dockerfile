FROM python:3.11-slim  # <-- استخدم Python 3.11 بدلاً من 3.14

WORKDIR /app

RUN apt-get update && apt-get install -y xvfb

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY . .

CMD ["xvfb-run", "python", "app.py"]