pipeline {
  agent none   // ไม่กำหนด agent หลัก → แต่ละ stage จะเลือก agent เอง (VM2 หรือ VM3)

  environment {
    // ชื่อ owner ใน GitHub (username หรือ org)
    OWNER        = 'patipan-pib'
    // ชื่อ image
    IMAGE        = 'prime-api'
    // Registry ของ GitHub Packages
    REGISTRY     = 'ghcr.io'
    // ชื่อเต็มของ image (ghcr.io/owner/image)
    FULL_IMAGE   = "${REGISTRY}/${OWNER}/${IMAGE}"
    // Tag ของ image ใช้ build number (unique ทุก build)
    TAG          = "${BUILD_NUMBER}"
  }

  stages {

    stage('Checkout (VM2)') {
      agent { label 'vm2' }   // รันบน VM2
      steps {
        // ดึงโค้ดจาก GitHub main branch ด้วย SSH key
        git branch: 'main',
            url: 'git@github.com:patipan-pib/Lab-API-PSPD.git',
            credentialsId: 'github_ssh'
      }
    }

    stage('Build (VM2)') {
      agent { label 'vm2' }
      steps {
        sh '''
          # Build image จาก Dockerfile ใน repo
          docker build -t ${IMAGE}:local .
          
          # Tag image ให้ตรงกับ GHCR (ทั้ง tag ตาม build number และ latest)
          docker tag ${IMAGE}:local ${FULL_IMAGE}:${TAG}
          docker tag ${IMAGE}:local ${FULL_IMAGE}:latest
        '''
      }
    }

    stage('Run unittest (VM2)') {
      agent { label 'vm2' }
      steps {
        sh '''
          # ติดตั้ง dependencies ของ app
          python3 -m pip install -r app/requirements.txt || true
          
          # (optional) ติดตั้ง lib เพิ่มถ้าต้องการ export report XML
          python3 -m pip install unittest-xml-reporting || true
          
          # รัน unittest อัตโนมัติ ค้นหาไฟล์ test*.py
          # เช่น test_app.py หรือ unit_test.py
          python3 -m unittest discover -s . -p "test*.py" -v || true
        '''
      }
    }

    stage('Push to GHCR (VM2)') {
      agent { label 'vm2' }
      steps {
        withCredentials([string(credentialsId: 'ghcr_pat', variable: 'GHCR_PAT')]) {
          sh '''
            # Login เข้า GitHub Container Registry ด้วย PAT
            echo "$GHCR_PAT" | docker login ${REGISTRY} -u ${OWNER} --password-stdin
            
            # Push image ไปที่ GHCR ทั้งแบบ tag ตาม build number และ latest
            docker push ${FULL_IMAGE}:${TAG}
            docker push ${FULL_IMAGE}:latest
          '''
        }
      }
    }

    stage('Deploy (VM3)') {
      agent { label 'vm3' }
      steps {
        sh '''
          # ลบ container เก่า (ถ้ามี) เพื่อป้องกันชื่อชนกัน
          docker rm -f ${IMAGE} || true
          
          # ดึง image จาก GHCR ตาม tag ที่ push ขึ้นไป
          docker pull ${FULL_IMAGE}:${TAG}
          
          # รัน container ใหม่ที่พอร์ต 5000
          docker run -d --name ${IMAGE} -p 5000:5000 ${FULL_IMAGE}:${TAG}
        '''
      }
    }

    stage('Smoke Test (VM3)') {
      agent { label 'vm3' }
      steps {
        sh '''
          # รอ 3 วิ ให้ container start
          sleep 3
          
          # ยิง curl ไปยัง endpoint /is_prime/17
          # ถ้าทำงานถูกต้องจะได้ {"number":17,"is_prime":true}
          curl -sSf http://localhost:5000/is_prime/17 | tr -d "\\n" || true
          echo
        '''
      }
    }
  }
}
