# Insight Project

This is a work in progress. To get the source, do:

    $ git clone https://github.com/wesbarnett/insight.git

## Flask server

### Development

To test and develop the server in a non-production setting, do the following.

    $ cd flask/application

In `app/routes.py` change the variable `wwwdir` such that it points to the `application`
directory.

Then to run the server do:

    $ python run.py

You know the server is running when you go to `localhost` in your web browser and it
says `It works!`.

### Production

    $ cd flask

To install the Flask server in a production environment do the following. First, you
will need to edit the Apache configuration files under the `apache` directory.
Additionally, Docker is required on your system to run this image.

The Docker image can be built by running:

    # docker build -t flaskapp .

The `Dockerfile` pulls in an Ubuntu image I set up for use with Apache/Flask located in
[this project](https://github.com/wesbarnett/apache-flask). That site will give you more
details on how to use the base image.

To run the server, then do something like:

    # docker run --name='flaskapp' -v /etc/letsencrypt:/etc/letsencrypt -v /dev/log:/dev/log -p 443:443 -p 80:80 -d flaskapp 

Note that Chrome won't allow "mixed content" so you have to serve it using SSL. In order
to do that, you have to have an SSL certificate. Free ones are available via Let's
Encrypt.

## Chrome Extension

    $ cd chrome_extension

Edit `main.js` such that it points to the server set up above. This will be the `url`
entry in the function named `handler`. If running locally, change it to the commented
`localhost:8080` entry.

To install the Chrome extension in Chrome, go to `chrome://extensions` and enable
developer mode. Then click `Load unpacked` and navigate to and select the
`chrome_extension` directory.

Now when you go to https://old.reddit.com/submit it should add additional options to the
submission form, which should query the web server.
