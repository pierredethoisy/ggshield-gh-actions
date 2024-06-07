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
                    script {
                        def output = sh(script: "ggshield secret scan repo . --json", returnStdout: true).trim()
                        writeFile file: 'ggshield_output.json', text: output
                        echo "ggshield_output.json content: ${output}"
                    }
                }
            }
            post {
                always {
                    script {
                        try {
                            def output = readFile('ggshield_output.json').trim()
                            echo "ggshield_output.json content: ${output}"
                            def json = new groovy.json.JsonSlurper().parseText(output)
                            def totalIncidents = json.total_incidents
                            
                            if (totalIncidents > 0) {
                                def incidentsList = json.incidents
                                for (incident in incidentsList) {
                                    def incidentUrl = incident.incident_url
                                    def incidentId = incidentUrl.tokenize("/")[-1]
                                    
                                    def response = sh(script: """
                                        curl -s -H "Authorization: Bearer ${GITGUARDIAN_API_KEY}" \
                                        https://api.gitguardian.com/v1/incidents/secrets/$incidentId
                                    """, returnStdout: true).trim()
                                    
                                    def incidentDetails = new groovy.json.JsonSlurper().parseText(response)
                                    def incidentDate = incidentDetails.date
                                    def incidentSeverity = incidentDetails.severity
                                    
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
