FROM python:3.11-slim
WORKDIR /app

# نسخ ملف المتطلبات من مساره الصحيح داخل فولدر backend
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي محتويات فولدر backend إلى مجلد العمل
COPY backend/ .

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT