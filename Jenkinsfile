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
                        // Install curl if not available
                        try {
                            // Capture the exit status of the ggshield command
                            def status = sh(script: "ggshield secret scan repo . --json > ggshield_output.json", returnStatus: true)

                            // Check if the command was successful
                            if (status == 0) {
                                echo "no secret found"
                            } else if (status==1) {
                                def output = readFile('ggshield_output.json')
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
                                            echo "Incident ID: ${incident.incident_url}"
                                            def incidentUrlParts = incident.incident_url.split('/')[-1]
                                            echo incidentUrlParts
                                            def response = httpRequest(
                                                    url: "https://api.gitguardian.com/v1/incidents/secrets/${incidentUrlParts}",
                                                    customHeaders: [[name: 'Authorization', value: "Token ${GITGUARDIAN_API_KEY}"]],
                                                    validResponseCodes: '200'
                                                )
                                            def status_http = sh(script: "httpRequest(
                                                    url: "https://api.gitguardian.com/v1/incidents/secrets/${incidentUrlParts}", /
                                                    customHeaders: [[name: 'Authorization', value: "Token ${GITGUARDIAN_API_KEY}"]], /
                                                    validResponseCodes: '200'
                                                )", returnStatus: true)
                                            echo "status: ${status_http}"
                                            echo "response: ${response.content}"
                                            def incidentDetails = new groovy.json.JsonSlurper().parseText(response)
                                            def incidentDate = incidentDetails.date
                                            def incidentSeverity = incidentDetails.severity
                                            
                                            echo "Incident ID: ${incidentId}"
                                            echo "Date: ${incidentDate}"
                                            echo "Severity: ${incidentSeverity}"

                                        }
                                    }
                                }
                            } else {
                                // Read and print the content of the output file even if the command fails
                                def errorOutput = readFile('ggshield_output.json')
                                echo "ggshield_output.json content (in case of failure): ${errorOutput}"
                                error "GitGuardian scan failed with exit code ${status}"
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
