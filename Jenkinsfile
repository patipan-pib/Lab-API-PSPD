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

    VM3_HOST     = 'vm3.local'
    // BASE_URL สำหรับ Robot ตอนรันบน VM2 → ชี้ localhost:5001
    ROBOT_BASE_URL_VM2 = "http://localhost:5001"
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

    /* ========== BUILD & UNIT TEST (VM2) ========== */
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
    /* ========== LOCAL SMOKE + ROBOT ON VM2 (hit localhost:5001) ========== */
    stage('Start App for Robot (VM2)') {
      agent { label 'vm2' }
      steps {
        sh '''
          # เคลียร์ container ทดสอบเดิมถ้ามี
          docker rm -f ${IMAGE}-test || true

          # รันคอนเทนเนอร์ทดสอบบนพอร์ต 5001
          docker run -d --name ${IMAGE}-test -p 5001:5000 ${IMAGE}:local

          # รอให้พร้อมใช้งาน (ลองตี endpoint ง่าย ๆ)
          for i in $(seq 1 30); do
            curl -fsS http://localhost:5001/is_prime/13 && break
            sleep 1
          done
        '''
      }
    }
    stage('Robot Tests (VM2 → localhost)') {
      agent { label 'vm2' }
      steps {
        dir('rf-tests') {
          sh '''
            python3 -m pip install --upgrade pip
            python3 -m pip install -r requirements.txt
            export BASE_URL="${ROBOT_BASE_URL_VM2}"
            echo "Robot BASE_URL=$BASE_URL"
            python3 -m robot -d reports tests/lab_api.robot
          '''
        }
      }
      post {
        always {
          // เก็บรายงานถ้าต้องการ
          publishHTML(target: [allowMissing: true, keepAll: true, reportDir: 'rf-tests/reports', reportFiles: 'report.html', reportName: 'Robot Report'])
          junit 'rf-tests/reports/output.xml'
          archiveArtifacts artifacts: 'rf-tests/reports/**', fingerprint: true
        }
      }
    }
    /* ========== PUSH (VM2) ========== */
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
    /* ========== DEPLOY (VM3) ========== */
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

    //  /* ========== ROBOT TEST ========== */
    // stage('Robot Tests (VM3)') {
    //   agent { label 'vm3' }
    //   steps {
    //     // ดึงชุดเทสต์จาก VM2 ที่ stash ไว้
    //     unstash 'rf-tests'
    //     dir('rf-tests') {
    //       sh '''
    //         python3 -m pip install --upgrade pip
    //         python3 -m pip install -r requirements.txt
    //         # ยิงไปยัง service ที่รันบน VM3
    //         export BASE_URL="http://localhost:5000"
    //         python3 -m robot -d reports tests/lab_api.robot
    //       '''
    //     }
    //   }
    // }

    stage('Smoke Test (VM3)') {
      agent { label 'vm3' }
      steps {
        sh '''
          sleep 3
          curl -sSf http://localhost:5000/is_prime/17 | tr -d "\\n" || true
          curl -sSf http://localhost:5000/is_prime/13 | tr -d "\\n" || true
          curl -sSf http://localhost:5000/is_prime/12 | tr -d "\\n" || true
          echo
        '''
      }
    }
  }
}
