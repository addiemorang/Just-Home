#!/bin/bash
pip install -r requirements.txt
python setup.py
cd tech_together
python manage.py runserver 0.0.0.0:8080