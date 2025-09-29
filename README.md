# APP for Prime API

## Run Locally
```bash

# 10.55.245.207 vm1
# 10.166.153.241 vm2
# 10.55.245.176 vm3


# 10.55.245.176:5000

# https://docs.google.com/document/d/1Ouuz8hrII5wqpWGe18TdM4-b8wi0Vkp-pyXwMtUyT9A/edit?tab=t.0#heading=h.7o1aatw19hwf

# ถ้าต้องการแก้ไข ip add ใน vm1 vm2 vm3
sudo nano /etc/hosts
# การออก จาก nano Ctrl + x ->  y -> Enter


# ติดตั้ง venv

python -m venv venv
.\venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r requirements.txt


# ขั้นตอนการ RUN in VScode App
python app/main.py

# ขั้นตอนการ RUN in VScode Unittest
python -m unittest unit_test.py -v

# ขั้นตอนการ RUN in VScode Robot
# 1. RUN Docker compose ใน LAB-API-PSPD

# ตรวจสอบ
docker ps

# docker compose up
docker compose up -d lab-api

# (ถ้าต้องการปิด) docker compose down
docker compose down lab-api

# 2. รันเทสต์
python -m robot -d reports tests/lab_api.robot


# ขั้นตอนการ RUN in VM2 TEST
# 1) เตรียม workspace ส่วนตัว (ไม่พึ่ง /var/lib/jenkins)
mkdir -p ~/ci && cd ~/ci

# 2) **** จำเป็นต้องทำ ***** เอาโค้ดแอป + ชุดทดสอบ Robot มาวาง (ใช้ HTTPS จะได้ไม่ต้องเตรียม SSH key) 
rm -rf app-src rf-tests
git clone https://github.com/patipan-pib/Lab-API-PSPD.git       app-src
git clone https://github.com/patipan-pib/Lab-API-PSPD-Robot.git rf-tests

# 3) **** จำเป็นต้องทำ ***** สร้าง image สำหรับทดสอบโลคัลบน VM2
cd app-src
docker build -t prime-api:local .

# 4) **** จำเป็นต้องทำ ***** สตาร์ทคอนเทนเนอร์ทดสอบที่พอร์ต 5001 (บน VM2)
docker rm -f prime-api-test || true
docker run -d --name prime-api-test -p 5000:5000 prime-api:local

# 5) ยิงเช็คปลายทางว่าพร้อม
for i in $(seq 1 30); do
  curl -fsS http://localhost:5000/is_prime/13 && break
  sleep 1
done

# 6) **** จำเป็นต้องทำ ***** รัน unittest (จากโฟลเดอร์โค้ดแอป)
python3 -m pip install -r app/requirements.txt || true
python3 -m unittest -v unit_test.py || python3 -m unittest discover -s . -p "unit_test.py" -v

# 7) **** จำเป็นต้องทำ ***** รัน Robot (จากโฟลเดอร์ชุดทดสอบ)
cd ~/ci/rf-tests
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m robot -d reports tests/lab_api.robot
