FROM python:3.10-slim

WORKDIR /app

# copy requirements.txt และติดตั้ง dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source code ทั้งหมดเข้า container
COPY app/ .

EXPOSE 5000

CMD ["python", "main.py"]
