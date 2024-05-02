pipeline {
  agent {
        label 'slave'
    }

  environment {
    version = '1.0.0' 
  }

  stages {
    stage('STAGE 1 checkout scm') {
      steps {
        git branch: 'main',
            credentialsId: 'github_unamepword',
            url: 'https://github.com/tomergabayy/musachit.git'
      }
    }

    stage ('STAGE 2 build') {
      steps {
        script{
          sh "sudo docker build -t tomergabayy/musachit:'${version}-${currentBuild.number}' ." 
          sh "sudo docker build -t tomergabayy/musachit:latest ."
        }
        
      }
    }

    stage ('STAGE 3 Tests') {
      steps {
        sh "echo 'Tested...'"
      }
    }

    stage ('STAGE 4 Publish ') {
      steps {
      sh "sudo docker push tomergabayy/musachit:'${version}-${currentBuild.number}'"
      sh "sudo docker push tomergabayy/whatstheweather:latest"
      }
    }

    stage('STAGE 5 Change image tag in gitops repo') {
      steps {
          script {
              // Clone the GitOps repository into the Jenkins workspace
              git branch: 'main',
                  credentialsId: 'github_unamepword',
                  url: 'https://github.com/tomergabayy/musachit.git'

              // Modify the configuration file(s) to update the image tag
              new_tag = ${version}-${currentBuild.number}
              sh 'sed -i "s/tag:.*/tag: \"$new_tag\"/" values.yaml'

              // Add, commit, and push the changes to the GitOps repository
              sh 'git add .'
              sh 'git commit -m "Update image tag"'
              sh 'git push origin main'
          }
      }
    }
  }

  post {
    always {
      sh "sudo docker image prune -a -f"
      cleanWs()
    }

    failure{
      slackSend( channel: "#devops-alerts", color: "bad", message: "Build #${currentBuild.number} failed")
    }

    success{
      slackSend( channel: "#succeeded-builds", color: "good", message: "Build #${currentBuild.number} succeed")
    }

  }
}
