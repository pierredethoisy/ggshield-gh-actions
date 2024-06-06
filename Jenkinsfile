pipeline {
    agent none
    stages {
        stage('Checkout') {
            agent any
            steps {
                wrap([$class: 'AnsiColorBuildWrapper', 'colorMapName': 'xterm']) {
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
                wrap([$class: 'AnsiColorBuildWrapper', 'colorMapName': 'xterm']) {
                    sh 'echo PATH is $PATH && PATH=$PATH:/usr/local/bin/jq'
                    sh 'ggshield secret scan repo . --json'
                }
            }
            post {
                always {
                    script {
                        try {
                            def output = ggshield secret scan repo . --json
                            def json = readJSON text: output
                            def incidents = json["total_incidents"]
                            if (incidents > 0) {
                                def incidentsList = json["incidents"]
                                for (incident in incidentsList) {
                                    def incidentUrl = incident["incident_url"]
                                    def incidentId = incidentUrl.tokenize("/")[-1]
                                    def response = sh(script: """
                                        curl -s -H "Authorization: Bearer ${GITGUARDIAN_API_KEY}" \
                                        https://api.gitguardian.com/v1/incidents/secrets/$incidentId
                                    """, returnStdout: true).trim()
                                    def incidentDetails = readJSON text: response
                                    echo "Incident ID: ${incidentId}"
                                    echo "Date: ${incidentDetails.date}"
                                    echo "Severity: ${incidentDetails.severity}"
                                }
                            } else {
                                echo "No incidents found."
                            }
                        } catch (Exception e) {
                            echo "Failed to process results: ${e.message}"
                        }
                    }
                }
            }
        }
    }
}
