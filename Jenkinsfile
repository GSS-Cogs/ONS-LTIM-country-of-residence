pipeline {
    agent {
        label 'master'
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
                sh "jupyter-nbconvert --to python --stdout 'Long-term international migration 2.02 next or last residence tidydata.ipynb' | ipython"
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    def csvs = []
                    for (def file : findFiles(glob: 'out/*.csv')) {
                        csvs.add("out/${file.name}")
                    }
                    uploadDraftset('ONS-LTIM-country-of-residence', csvs)
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
    }
}
