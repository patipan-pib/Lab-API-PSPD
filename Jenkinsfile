pipeline {
  agent none
  environment {
    REGISTRY = 'vm2.local:5000'
  }

  stages {
    stage('Checkout (VM2)') {
      agent { label 'vm2' }
      steps {
        git branch: 'main',
            url: 'git@github.com:patipan-pib/Lab-API-PSPD.git',
            credentialsId: 'github_ssh'
      }
    }

    stage('Build & Push (VM2)') {
      agent { label 'vm2' }
      steps {
        script {
          GIT_SHA = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        }
        sh '''
          docker build -t prime-api:latest -f app/Dockerfile .
          docker tag prime-api:latest ${REGISTRY}/prime-api:${BUILD_NUMBER}
          docker push ${REGISTRY}/prime-api:${BUILD_NUMBER}
        '''
      }
    }

    stage('Deploy (VM3)') {
      agent { label 'vm3' }
      steps {
        sh '''
          # อนุญาต insecure registry (ถ้ายังไม่ได้ตั้งใน daemon.json)
          # แล้ว restart docker (ทำครั้งเดียวด้วยมือจะดีกว่า)

          docker rm -f prime-api || true
          docker pull vm2.local:5000/prime-api:${BUILD_NUMBER}
          docker run -d --name prime-api -p 5000:5000 vm2.local:5000/prime-api:${BUILD_NUMBER}
        '''
      }
    }

    stage('Smoke test (VM3)') {
      agent { label 'vm3' }
      steps {
        sh 'curl -sSf http://localhost:5000/is_prime/19 | tr -d "\\n"; echo'
      }
    }
  }
}
