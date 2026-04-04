pipeline {
    agent any

    environment {
        PROJECT_DIR = "/var/www/richbot-be/rb-be"
        VENV_PYTHON = "/var/www/richbot-be/rb-be/venv/bin/python"
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                cd $PROJECT_DIR
                pip install -r requirements.txt
                '''
            }
        }

        stage('Migrations') {
            steps {
                sh '''
                cd $PROJECT_DIR
                $VENV_PYTHON manage.py makemigrations
                $VENV_PYTHON manage.py migrate
                '''
            }
        }

        stage('Restart Service') {
            steps {
                sh '''
                sudo systemctl restart richbot
                '''
            }
        }
    }
}
