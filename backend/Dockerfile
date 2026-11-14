FROM python:3.11-slim
WORKDIR /app

# نسخ ملف المتطلبات من نفس المجلد
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات من نفس المجلد
COPY . .

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
