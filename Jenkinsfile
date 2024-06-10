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
                        try {
                            def output = sh(script: "ggshield secret scan repo . --json", returnStdout: true).trim()
                            writeFile file: 'ggshield_output.json', text: output
                            echo "ggshield_output.json content: ${output}"

                            def jsonSlurper = new groovy.json.JsonSlurper()
                            def parsedOutput = jsonSlurper.parseText(output)
                            
                            // Echo the main id field
                            echo "Main ID: ${parsedOutput.id}"

                            // Iterate through the scans and echo each id
                            parsedOutput.scans.each { scan ->
                                echo "Scan ID: ${scan.id}"
                                
                                // Iterate through entities_with_incidents and echo incident ids
                                scan.entities_with_incidents.each { entity ->
                                    entity.incidents.each { incident ->
                                        echo "Incident ID: ${incident.id}"
                                    }
                                }
                            }
                        } catch (Exception e) {
                            echo "Failed to run GitGuardian scan: ${e.message}"
                        }
                    }
                }
            }
        }
    }
}
