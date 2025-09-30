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
    // BASE_URL สำหรับ Robot ตอนรันบน VM2 → ชี้ localhost:5000
    ROBOT_BASE_URL_VM2 = "http://localhost:5000"
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

          docker build -t ${IMAGE}:local .
          
          docker tag ${IMAGE}:local ${FULL_IMAGE}:${TAG}
          docker tag ${IMAGE}:local ${FULL_IMAGE}:latest
        '''
      }
    }

    stage('Run unittest (VM2)') {
      agent { label 'vm2' }
      steps {
        sh '''

          python3 -m pip install -r app/requirements.txt || true
          python3 -m pip install unittest-xml-reporting || true
          
          # unit_test.py 
          python3 -m unittest discover -s . -p "unit_test.py" -v || true 
        '''
      }
    }
    /* ========== LOCAL SMOKE + ROBOT ON VM2 (hit localhost:5000) ========== */
    stage('Start App for Robot (VM2)') {
      agent { label 'vm2' }
      steps {
        sh '''
          docker rm -f ${IMAGE}-test || true

          docker run -d --name ${IMAGE}-test -p 5000:5000 ${IMAGE}:local

          for i in $(seq 1 30); do
            curl -fsS http://localhost:5000/next5/1 && break
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

            python3 -m robot --xunit xunit.xml -d reports tests/lab_api.robot
          '''
        }
      }
      post {
        always {
          robot outputPath: 'rf-tests/reports',
                outputFileName: 'output.xml',
                reportFileName: 'report.html',
                logFileName: 'log.html'
          archiveArtifacts artifacts: 'rf-tests/reports/**', fingerprint: true, allowEmptyArchive: true
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


    stage('Smoke Test (VM3)') {
      agent { label 'vm3' }
      steps {
        sh '''
          sleep 3
          curl -sSf http://localhost:5000/next5/1 | tr -d "\\n" || true
          curl -sSf http://localhost:5000/next5/-10 | tr -d "\\n" || true
          curl -sSf http://localhost:5000/next5/1.5 | tr -d "\\n" || true
          echo
        '''
      }
    }
  }
}
