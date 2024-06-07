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
                    sh 'ggshield secret scan repo . --json --output ggshield_output.json'
                }
            }
            post {
                always {
                    script {
                        try {
                            // Read the JSON file and parse total incidents
                            def output = sh(script: "cat ggshield_output.json", returnStdout: true).trim()
                            def totalIncidents = sh(script: "jq '.total_incidents' ggshield_output.json", returnStdout: true).trim().toInteger()
                            
                            if (totalIncidents > 0) {
                                // Parse incidents array and process each incident
                                def incidentsList = sh(script: "jq -c '.incidents[]' ggshield_output.json", returnStdout: true).trim().split('\n')
                                for (incident in incidentsList) {
                                    def incidentJson = sh(script: "echo '${incident}' | jq .", returnStdout: true).trim()
                                    def incidentUrl = sh(script: "echo '${incidentJson}' | jq -r '.incident_url'", returnStdout: true).trim()
                                    def incidentId = incidentUrl.tokenize("/")[-1]
                                    
                                    def response = sh(script: """
                                        curl -s -H "Authorization: Bearer ${GITGUARDIAN_API_KEY}" \
                                        https://api.gitguardian.com/v1/incidents/secrets/$incidentId
                                    """, returnStdout: true).trim()
                                    
                                    def incidentDetails = sh(script: "echo '${response}' | jq .", returnStdout: true).trim()
                                    def incidentDate = sh(script: "echo '${incidentDetails}' | jq -r '.date'", returnStdout: true).trim()
                                    def incidentSeverity = sh(script: "echo '${incidentDetails}' | jq -r '.severity'", returnStdout: true).trim()
                                    
                                    echo "Incident ID: ${incidentId}"
                                    echo "Date: ${incidentDate}"
                                    echo "Severity: ${incidentSeverity}"
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
