#!/bin/bash

# install dependencies
pip install setuptools
pip install -r requirements.txt

# Run django commands
python manage.py makemigrations
python manage.oy migrate
python manage.py collectstatic