pipeline {
    agent {
        label 'master'
    }
    triggers {
        upstream(upstreamProjects: '../Reference/ref_migration',
                 threshold: hudson.model.Result.SUCCESS)
    }
    stages {
        stage('Clean') {
            steps {
                sh 'rm -rf out'
            }
        }
        stage('Transform') {
            agent {
                docker {
                    image 'cloudfluff/databaker'
                    reuseNode true
                }
            }
            steps {
                sh "jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute 'Long-term international migration 2.02 next or last residence tidydata.ipynb'"
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    def csvs = []
                    for (def file : findFiles(glob: 'out/*.csv')) {
                        csvs.add("out/${file.name}")
                    }
                    uploadTidy(csvs,
                                   'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv',
                                   'ONS LTIM country of residence')
                }
            }
        }
        stage('Publish') {
            steps {
                script {
                    publishDraftset()
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts 'out/*'
        }
        success {
            build job: '../GDP-tests', wait: false
        }
    }
}
