import sys
sys.path.insert(0, '/var/www/apache-flask/application')

from app import app as application

if __name__ == '__main__':
    application.run(port=8080)
