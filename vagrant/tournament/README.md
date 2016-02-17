TOURNAMENT PROJECT
------------------
The second project for Udacity's Full Stack Web Developer Nanodegree


SETUP
-----
You must have PSQL installed onto the machine you'll be running this program on.

To get the database ready run

    $ psql
    $ CREATE DATABASE tournament;
    $ \i tournament.sql

This will setup the database

run
    $ \q
to exit the psql terminal

TESTING
-------
To check that the application passes all necessary tests to fulfill the 
requirements of the application simply run

    $ python tournament_test.py

This will cycle through all the functions that were written in the 
tournament.py file, ensuring that the code passes the necessary requirements

