# wesbarnett/apache-flask example

This is a small example of a Flask Docker application that uses the
`wesbarnett/apache-flask` image as a base. It includes sending the
Apache log to the host system's log.

The `requirements.txt` file only contains `flask` and `mod-wsgi`. Add
additional required Python3 packages to that file if needed.

## Preparation

You will need to [create a self-signed
certificate](https://stackoverflow.com/questions/18034/how-do-i-create-a-self-signed-ssl-certificate-to-use-while-testing-a-web-app)
if you want to use `https` on `localhost` for testing purposes.
Otherwise, modify the Apache configuration files to use only `http` or
you can get a free certificate via Let's Encrypt.

By default the configuration looks for the certificate at
`/etc/ssl/certs/localhost.crt` and they key at
`/etc/ssl/private/localhost.key`. In this example, leave them on the
host system, and they will be mounted and shared with the Docker
image.

## Build

To build this Docker image do:

    docker build -t flaskapp .

## Run

To run the image:

    docker run -v /dev/log:/dev/log -v /etc/ssl:/etc/ssl -p 80:80 -p 443:443 -d flaskapp

## Test

To test on the command line do:

    curl -k https://localhost

You should see the HTML of the webpage and an entry in the host's
system log.
