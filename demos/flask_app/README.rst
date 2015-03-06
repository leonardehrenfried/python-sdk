README
======

This is a sample Python web application accessing an IOT application in the relayr_
Open Sensors Cloud. It is built using the micro web framework Flask_, Authomatic_
for OAuth2 and the relayr `Python SDK`_ to access the relayr_ cloud. 

The main functionality is to connect to the relayr_ online application using
OAuth2_ and access some of its resources, like a WunderBar and its individual
transmitters and its devices.


Files
-----

:README.rst:
    This file.

:requirements.txt:
    A list of installation dependencies (requirements) to be used with ``pip``.

:config.py:
    Settings for your Flask_ web application, mostly OAuth2-related.

:relayr_provider.py:
    The Authomatic_ subclass implementing the relayr OAuth2 provider,
    which also accesses several user resources.

:run.py:
    The main Python file to run the Flask_ app on a local webserver.

:templates/:
    The HTML templates used for all pages served by Flask_.


Installation
------------

This should work on Python 2 and 3 alike (Authomatic_ supports Python 3 as of now
only in its repository code, which is currently not realeased yet).

.. code-block:: bash

    cd flask_app
    pip install -r requrements.txt


Setup
-----

1. If you haven't already, create a relayr app (let's say it's named MyApp) on your
   relayr account at https://developer.relayr.io.

2. Go to https://developer.relayr.io/dashboard/apps/myApps and, for MyApp, fill in
   a value for the ``REDIRECT URI`` field like ``http://127.0.0.1:8080``, and make
   sure this is the same host and port as used in the file ``run.py`` that starts
   the webserver and this Flask app.

3. On the same page, copy the value for the field ``APP ID/OAUTH CLIENT ID`` and
   paste it into the file ``config.py`` as a value for the dictionary key
   ``consumer_key``.
   Do the same with the value for the field ``OAUTH CLIENT SECRET``, pasting it
   as a value for the dictionary key ``consumer_secret`` in the same file.


Usage
-----

Now you only have to execute ``python run.py``, open the indicated URL
(e.g. http://127.0.0.1:8080) in a browser, click on the ``relayr`` link,
login on the relayr_ login page with your account credentials.

As a result you should then see a very decent page with some details about
your relayr account (name, ID, email) and your WunderBars and their devices!
From here you can expand the app to do other things in some more interactive,
more shiny fashion.


.. _Flask: http://flask.pocoo.org
.. _Authomatic: http://peterhudec.github.io/authomatic/
.. _Python SDK: https://github.com/relayr/python-sdk/
.. _relayr: http://relayr.io
.. _OAuth2: https://developer.relayr.io/documents/Welcome/OAuthReference
