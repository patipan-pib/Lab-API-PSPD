# ใช้ Python base image ขนาดเล็ก
FROM python:3.10-slim

# กำหนด working directory ใน container
WORKDIR /app

# copy requirements.txt เข้ามา และติดตั้ง dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source code ทั้งหมดเข้า container
COPY app/ .

# เปิดพอร์ต 5000 ให้เข้าถึง API ได้
EXPOSE 5000

# คำสั่งรันแอป
CMD ["python", "main.py"]
