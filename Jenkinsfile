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
        stash name: 'src', includes: '**/*'
      }
    }

    stage('Build Docker Image (VM2)') {
      agent { label 'vm2' }
      steps {
        sh 'docker build -t ${IMAGE_NAME}:latest .'
      }
    }

    stage('Run unittest (VM2)') {
      agent { label 'vm2' }
      steps {
        sh '''
          # ติดตั้ง dependencies
          python3 -m pip install -r app/requirements.txt
          # รัน unittest (ไฟล์ test_app.py หรือ unit_test.py)
          python3 -m unittest discover -s . -p "unit_test.py" -v
        '''
      }
    }

    stage('Deploy (VM3)') {
      agent { label 'vm3' }
      steps {
        unstash 'src'
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
