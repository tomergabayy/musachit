pipeline {
  agent {
        label 'slave'
    }

  parameters {
    string defaultValue: '2', description: 'Replicas number', name: 'replicas'
  }

  environment {
    version = '1.0.0' 
  }

  stages {
    stage('STAGE 1 checkout scm') {
      steps {
        git branch: 'main',
            credentialsId: 'gitlab_cred',
            url: 'http://gitlab.tomerg.click/tomer_gabay/portfolio.git'
      }
    }

    stage ('STAGE 2 build') {
      steps {
        script{
          sh "docker build -t tomergabayy/whatstheweather:${version}-${currentBuild.number} ./weatherapp/"
          sh "docker build -t tomergabayy/whatstheweather:latest ./weatherapp/"
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
      sh "docker push tomergabayy/whatstheweather:'${version}-${currentBuild.number}'"
      sh "docker push tomergabayy/whatstheweather:latest"
      }
    }

    stage('STAGE 5 Upgrade Helm chart') {
      steps {
        withKubeConfig([credentialsId: 'k8s-user', serverUrl: 'https://88AAEF22F52FFB389FD411F6BEC2B79E.yl4.eu-north-1.eks.amazonaws.com']) {
          sh "helm upgrade weather-application weatherapp-chart --set image.tag='${version}-${currentBuild.number}',replicaCount=${replicas}"
        }
      }
    }
  }

  post {
    always {
      sh "docker image rm -f tomergabayy/whatstheweather:'${version}-${currentBuild.number}'"
      sh "docker image rm -f tomergabayy/whatstheweather:latest"
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
