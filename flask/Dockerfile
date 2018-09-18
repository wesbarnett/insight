FROM wesbarnett/apache-flask:bionic-x86_64

# Copy and eneable Apache configuration files
COPY apache/* /etc/apache2/sites-available/
RUN a2ensite apache-flask apache-flask-ssl

# Copy Flask application
COPY --chown=www-data application /var/www/apache-flask/application
