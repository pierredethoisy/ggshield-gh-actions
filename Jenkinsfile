pipeline {
    agent none
    stages {
        stage('Checkout') {
            agent any
            steps { 
                ansiColor('xterm') {
                    checkout scm
                }
            }
        }
        stage('GitGuardian Scan') {
            agent {
                docker {
                    image 'gitguardian/ggshield:latest'
                    args '-e HOME=${WORKSPACE}'
                }
            }
            environment {
                GITGUARDIAN_API_KEY = credentials('gitguardian-api-key')
            }
            steps {
                ansiColor('xterm') {
                    sh 'ggshield secret scan ci'
                }
            }
        }
    }
}
