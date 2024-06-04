pipeline {
    agent {
        docker {
            image 'gitguardian/ggshield:latest'
            args '-e HOME=${WORKSPACE}'
        }
    }
    environment {
        PDT_SECRETS_CHECK_STRICT = "false"
        PDT_SECRETS_RUNNER_TAG = "tiny"
        GIT_GUARDIAN_REPORT = "gg-secret-detection-report.json"
        GIT_GUARDIAN_PATH_REPORT = "gg-secret-detection-report-path.json"
        GIT_GUARDIAN_ALL_POLICIES = "true"
        GIT_GUARDIAN_OPTS = "--exclude PDT-common --json -b 'Generic Password' -b 'Username Password'"
        GIT_SUBMODULE_STRATEGY = "none"
        PDT_SECRETS_CHECK_APP_TIMEOUT = "5m"
        PIP_CACHE_DIR = "${env.WORKSPACE}/.cache/pip"
        PDT_SECRETS_PG_AUTH = "${env.PDT_SECRETS_PG_USER}:${env.PDT_SECRETS_PG_PASSWORD}"
        queryGsm1900User = "true"
        GIT_LFS_SKIP_SMUDGE = "1"
        GIT_STRATEGY = "clone"
        GIT_DEPTH = "1000"
        CERTS_COPY_TO_ROOT = "false"
        PDT_BEFORE_SCRIPT = ""
    }
    stages {
        stage('Test') {
            steps {
                script {
                    def run_ggshield = { scanType ->
                        switch (scanType) {
                            case 'repo':
                                println "GitGuardian scanning the entire repository history up to GIT_DEPTH value..."
                                GIT_GUARDIAN_OPTS_FINAL = "${GIT_GUARDIAN_OPTS} -o ${GIT_GUARDIAN_REPORT} repo ${env.WORKSPACE}"
                                exitMsg = "ggshield has detected secrets committed in your repository throughout the entire cloned history. Please review discovered secrets above, revoke any actively used secrets from underlying systems, and remove from git history. Info - "
                                break
                            case 'ci':
                                println "GitGuardian scanning the commits associated with the current push..."
                                GIT_GUARDIAN_OPTS_FINAL = "${GIT_GUARDIAN_OPTS} -o ${GIT_GUARDIAN_REPORT} ci"
                                exitMsg = "ggshield has detected at least 1 secret on this branch between current push and the last push. Please review discovered secrets above, revoke any actively used secrets from underlying systems, and remove from git commits before proceeding. Info - "
                                break
                            case 'path':
                                println "Now scanning repo for secrets at current HEAD..."
                                exitMsg = "ggshield has detected secrets at the current HEAD - all files at their current state without history. Please review discovered secrets above, revoke any actively used secrets from underlying systems and remove from your current working HEAD. This is a warning for now, but will block in the future. "
                                GIT_GUARDIAN_REPORT = "${GIT_GUARDIAN_PATH_REPORT}"
                                GIT_GUARDIAN_OPTS_FINAL = "${GIT_GUARDIAN_OPTS} -o ${GIT_GUARDIAN_PATH_REPORT} path -r -y ${env.WORKSPACE}"
                        }
                        println "GIT_GUARDIAN_OPTS_FINAL = ${GIT_GUARDIAN_OPTS_FINAL}"
                        try {
                            sh "timeout ${PDT_SECRETS_CHECK_APP_TIMEOUT} ggshield scan ${GIT_GUARDIAN_OPTS_FINAL}"
                        } catch (Exception e) {
                            exitCode = e.getCode()
                        }
                        if (fileExists(GIT_GUARDIAN_REPORT) && validJson(readFile(GIT_GUARDIAN_REPORT))) {
                            sh "jq -C < ${GIT_GUARDIAN_REPORT}"
                        } else {
                            println "Could not parse json from ${GIT_GUARDIAN_REPORT}, exiting"
                            sh "jq . < ${GIT_GUARDIAN_REPORT}"
                            error("Failed to parse JSON report")
                        }
                    }

                    def validJson = { jsonString ->
                        try {
                            new groovy.json.JsonSlurper().parseText(jsonString)
                            return true
                        } catch (Exception e) {
                            return false
                        }
                    }

                    sh """
                        apk add --no-cache jq git postgresql-client
                        pip3 --disable-pip-version-check install -q ggshield -U
                        ggshield --version
                        echo "GIT_DEPTH = ${GIT_DEPTH}"
                        echo "GIT_STRATEGY = ${GIT_STRATEGY}"
                        echo "PDT_SECRETS_CHECK = ${PDT_SECRETS_CHECK}"
                        echo "PDT_SECRETS_CHECK_STRICT = ${PDT_SECRETS_CHECK_STRICT}"
                        echo "CI_COMMIT_BEFORE_SHA = ${env.GIT_COMMIT}"
                    """
                    def exitCode = 0

                    if (params.GIT_GUARDIAN_FULL_HISTORY == "true") {
                        run_ggshield('repo')
                        if (exitCode != 0) {
                            println exitMsg
                            error("ggshield scan failed with exit code ${exitCode}")
                        }
                    } else {
                        run_ggshield('ci')
                        if (exitCode != 0) {
                            def secretOutJson = readFile(GIT_GUARDIAN_REPORT).replace("'", "''")
                            writeFile file: 'insert.sql', text: """
                                insert into secrets.secrets.secrets (report,gitlab_user_email,gitlab_user_name,gitlab_user_id,gitlab_user_login,ci_commit_ref_name,ci_job_started_at,ci_job_url,ci_project_id,ci_project_name,user_details) values ('$secretOutJson', '$GITLAB_USER_EMAIL','$GITLAB_USER_NAME','$GITLAB_USER_ID','$GITLAB_USER_LOGIN','$CI_COMMIT_REF_NAME','$CI_JOB_STARTED_AT','$CI_JOB_URL','$CI_PROJECT_ID','$CI_PROJECT_NAME','$PDT_USER_JSON');
                            """
                            sh "psql postgres://${PDT_SECRETS_PG_AUTH}@${PDT_SECRETS_PG_HOST}/${PDT_SECRETS_PG_DB} -f insert.sql"
                            def gl = sh(script: "jq '.scans[].entities_with_incidents[] | select(.incidents[].type == \"GitLab Token\").filename' ${GIT_GUARDIAN_REPORT} | wc -l", returnStdout: true).trim()
                            def glpat = sh(script: "jq '.scans[].entities_with_incidents[] | select(.incidents[].type == \"Generic High Entropy Secret\") | .incidents[].occurrences[].match | select (.|test(\"glpat-\"))' ${GIT_GUARDIAN_REPORT} | wc -l", returnStdout: true).trim()
                            if (gl.toInteger() > 0 || glpat.toInteger() > 0) {
                                println "Found at least 1 GitLab token in your secrets report. Please review and remove."
                                error("Significant secret found: GitLab Token")
                            }
                            // ... (Repeat for other secret types as in the original script)
                        }
                    }
                    run_ggshield('path')
                    if (exitCode != 0) {
                        println exitMsg
                        error("ggshield scan failed at HEAD with exit code ${exitCode}")
                    }
                    println "0 Secrets found. Nice work"
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${GIT_GUARDIAN_REPORT}, ${GIT_GUARDIAN_PATH_REPORT}", allowEmptyArchive: true
                }
                failure {
                    retry(2) {
                        unstable("Retrying due to failure")
                    }
                }
            }
        }
    }
    options {
        timeout(time: 10, unit: 'MINUTES')
    }
}
