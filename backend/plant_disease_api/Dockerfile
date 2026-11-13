FROM python:3.11-slim
WORKDIR /app

# تثبيت نسخة CPU-only من PyTorch و torchvision أولاً
# هذا يمنع تنزيل حزم CUDA غير الضرورية ويسرع عملية البناء بشكل كبير
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# نسخ ملف المتطلبات وتثبيت باقي المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT