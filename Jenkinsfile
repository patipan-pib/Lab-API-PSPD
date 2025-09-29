pipeline {
  agent none   // ไม่กำหนด agent หลัก → แต่ละ stage จะเลือก agent เอง (VM2 หรือ VM3)

  environment {
    // ---- Registry config (GHCR) ----
    // ชื่อ owner ใน GitHub (username หรือ org)
    OWNER        = 'patipan-pib'
    // ชื่อ image
    IMAGE        = 'prime-api'
    REGISTRY     = 'ghcr.io'
    FULL_IMAGE   = "${REGISTRY}/${OWNER}/${IMAGE}"
    // Tag ของ image ใช้ build number (unique ทุก build)
    TAG          = "${BUILD_NUMBER}"

    // ---- Repo URLs ----
    APP_REPO     = 'git@github.com:patipan-pib/Lab-API-PSPD.git'
    ROBOT_REPO   = 'git@github.com:patipan-pib/Lab-API-PSPD-Robot.git'
  }

  stages {

     /* ========== CHECKOUT ========== */
    stage('Checkout App (VM2)') {
      agent { label 'vm2' }
      steps {
        dir('app-src') {
          git branch: 'main', url: "${APP_REPO}", credentialsId: 'github_ssh'
        }
      }
    }

    stage('Checkout Robot (VM2)') {
      agent { label 'vm2' }
      steps {
        dir('rf-tests') {
          git branch: 'main', url: "${ROBOT_REPO}", credentialsId: 'github_ssh'
        }
        // ส่งโฟลเดอร์เทสต์ไปใช้ที่ VM3
        stash name: 'rf-tests', includes: 'rf-tests/**'
      }
    }

    /* ========== BUILD & UNIT TEST ========== */
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
          python3 -m unittest discover -s . -p "unit_test.py" -v || true
        '''
      }
    }
    /* ========== PUSH ========== */
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
    /* ========== DEPLOY ========== */
    stage('Deploy (VM3)') {
    agent { label 'vm3' }
    steps {
        withCredentials([string(credentialsId: 'ghcr_pat', variable: 'GHCR_PAT')]) {
            sh '''
                # ลบ container เก่า ถ้ามี
                docker rm -f ${IMAGE} || true

                # login GHCR ก่อน pull
                echo "$GHCR_PAT" | docker login ${REGISTRY} -u ${OWNER} --password-stdin

                # ดึง image จาก GHCR
                docker pull ${FULL_IMAGE}:${TAG}

                # รัน container ใหม่
                docker run -d --name ${IMAGE} -p 5000:5000 ${FULL_IMAGE}:${TAG}
            '''
            }
        }
    }

     /* ========== ROBOT TEST ========== */
    stage('Robot Tests (VM3)') {
      agent { label 'vm3' }
      steps {
        // ดึงชุดเทสต์จาก VM2 ที่ stash ไว้
        unstash 'rf-tests'
        dir('rf-tests') {
          sh '''
            python3 -m pip install --upgrade pip
            python3 -m pip install -r requirements.txt
            # ยิงไปยัง service ที่รันบน VM3
            export BASE_URL="http://localhost:5000"
            robot -d reports tests/prime_api.robot
          '''
        }
      }
      post {
        always {
          // แสดงรายงาน Robot + เก็บไฟล์รายงาน
          publishHTML(target: [allowMissing: true, keepAll: true,
                               reportDir: 'rf-tests/reports', reportFiles: 'report.html',
                               reportName: 'Robot Report'])
          junit 'rf-tests/reports/output.xml'
          archiveArtifacts artifacts: 'rf-tests/reports/**', fingerprint: true
        }
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

          # ถ้าทำงานถูกต้องจะได้ {"number":13,"is_prime":true}
          curl -sSf http://localhost:5000/is_prime/13 | tr -d "\\n" || true

          # ถ้าทำงานถูกต้องจะได้ {"number":12,"is_prime":false}
          curl -sSf http://localhost:5000/is_prime/12 | tr -d "\\n" || true
          echo
        '''
      }
    }
  }
}
