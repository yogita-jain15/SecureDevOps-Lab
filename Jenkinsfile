pipeline {
  agent any

  environment {
    COMPOSE_CMD = "docker compose"          // modern compose
  }

  stages {
    stage('Checkout') {
      steps {
        checkout([$class: 'GitSCM',
          branches: [[name: '*/main']],
          userRemoteConfigs: [[url: 'https://github.com/yogita-jain15/SecureDevOps-Lab.git']]
        ])
      }
    }

    stage('Build images') {
      steps {
        sh "${COMPOSE_CMD} build"
      }
    }

    stage('Deploy (Up)') {
      steps {
        // stop old containers (ignore errors), then start in background
        sh "${COMPOSE_CMD} down || true"
        sh "${COMPOSE_CMD} up -d"
      }
    }
  }

  post {
    success {
      echo "✅ Build & deploy successful"
    }
    failure {
      echo "❌ Build failed — check console output"
    }
  }
}
