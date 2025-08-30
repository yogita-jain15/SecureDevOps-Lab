pipeline {
  agent any

  environment {
    COMPOSE_CMD = "docker compose"     // modern compose
    DOCKER_IMAGE = "securedevops-app"  // your app image
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

    stage('Security Scan - Container (Trivy)') {
      steps {
        script {
          // Scan Docker image for CRITICAL/HIGH CVEs
          sh "trivy image --exit-code 1 --severity CRITICAL,HIGH ${DOCKER_IMAGE} || true"
        }
      }
    }

    stage('Deploy (Up)') {
      steps {
        // stop old containers (ignore errors), then start in background
        sh "${COMPOSE_CMD} down || true"
        sh "${COMPOSE_CMD} up -d"
      }
    }

    stage('Security Scan - App (Nikto)') {
      steps {
        script {
          // Scan running Flask app
          sh "nikto -h http://127.0.0.1:5000 > security_report.txt || true"
          archiveArtifacts artifacts: 'security_report.txt', followSymlinks: false
        }
      }
    }
  }

  post {
    success {
      echo "✅ Build, Scan & Deploy successful"
    }
    failure {
      echo "❌ Build failed — check console output"
    }
  }
}
