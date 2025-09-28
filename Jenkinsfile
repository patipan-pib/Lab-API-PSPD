pipeline {
  agent { label 'vm2' }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main',
            url: 'git@github.com:patipan-pib/Lab-API-PSPD.git',
            credentialsId: 'github_ssh'
      }
    }

    stage('Build') {
      steps {
        sh 'docker build -t simple-api:test .'
      }
    }

    stage('Test') {
      steps {
        sh 'pytest || true'   // หรือ robot test
      }
    }

    stage('Deploy on VM3') {
      agent { label 'vm3' }
      steps {
        sh 'docker run -d -p 5000:5000 simple-api:test'
      }
    }
  }
}
