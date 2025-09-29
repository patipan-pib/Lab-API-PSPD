pipeline {
  agent none

  environment {
    IMAGE_NAME = "prime-api"
    CONTAINER_NAME = "prime-api"
  }

  stages {
    stage('Checkout (VM2)') {
      agent { label 'vm2' }
      steps {
        git branch: 'main',
            url: 'git@github.com:patipan-pib/Lab-API-PSPD.git',
            credentialsId: 'github_ssh'
        // เก็บ source ไว้ใช้ที่ VM3 ด้วย
        stash name: 'src', includes: '**/*'
      }
    }

    stage('Build Docker Image (VM2)') {
      agent { label 'vm2' }
      steps {
        sh '''
          docker build -t ${IMAGE_NAME}:latest .
        '''
      }
    }

    stage('Test (VM2)') {
      agent { label 'vm2' }
      steps {
        sh '''
          # ติดตั้ง pytest (ถ้ามีไฟล์ test)
          python3 -m pip install -r app/requirements.txt || true
          python3 -m pip install pytest || true
          pytest -q || true
        '''
      }
    }

    stage('Deploy (VM3)') {
      agent { label 'vm3' }
      steps {
        unstash 'src'   // ส่ง source ไป VM3 แล้ว build image ที่นี่อีกครั้ง
        sh '''
          docker build -t ${IMAGE_NAME}:latest .
          docker rm -f ${CONTAINER_NAME} || true
          docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${IMAGE_NAME}:latest
        '''
      }
    }

    stage('Smoke Test (VM3)') {
      agent { label 'vm3' }
      steps {
        sh '''
          sleep 3
          curl -sSf http://localhost:5000/is_prime/17 || true
        '''
      }
    }
  }
}
