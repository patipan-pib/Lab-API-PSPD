10.55.245.207 vm1
10.166.153.241 vm2
10.55.245.176 vm3


10.55.245.176:5000

unit_test
python3 -m unittest -v unit_test.py

# 1) เตรียม workspace ส่วนตัว (ไม่พึ่ง /var/lib/jenkins)
mkdir -p ~/ci && cd ~/ci

# 2) เอาโค้ดแอป + ชุดทดสอบ Robot มาวาง (ใช้ HTTPS จะได้ไม่ต้องเตรียม SSH key)
rm -rf app-src rf-tests
git clone https://github.com/patipan-pib/Lab-API-PSPD.git       app-src
git clone https://github.com/patipan-pib/Lab-API-PSPD-Robot.git rf-tests

# 3) สร้าง image สำหรับทดสอบโลคัลบน VM2
cd app-src
docker build -t prime-api:local .

# 4) สตาร์ทคอนเทนเนอร์ทดสอบที่พอร์ต 5001 (บน VM2)
docker rm -f prime-api-test || true
docker run -d --name prime-api-test -p 5001:5000 prime-api:local

# 5) ยิงเช็คปลายทางว่าพร้อม
for i in $(seq 1 30); do
  curl -fsS http://localhost:5001/is_prime/13 && break
  sleep 1
done

# 6) รัน unittest (จากโฟลเดอร์โค้ดแอป)
python3 -m pip install -r app/requirements.txt || true
python3 -m unittest -v unit_test.py || python3 -m unittest discover -s . -p "unit_test.py" -v

# 7) รัน Robot (จากโฟลเดอร์ชุดทดสอบ)
cd ~/ci/rf-tests
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
export BASE_URL="http://localhost:5001"
python3 -m robot -d reports tests/lab_api.robot

# 8) ดูรายงาน Robot ที่สร้างไว้
ls -lah reports
# ถ้าอยากเปิดผ่าน browser จากเครื่องคุณ:
# python3 -m http.server 8000 -d ./reports
# แล้วเปิด http://vm2.local:8000/report.html
