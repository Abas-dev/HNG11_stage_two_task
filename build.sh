#!/bin/bash 

echo "  BUILD START"

source venv/bin/activate

pip3 install -r requirements.txt
python3.12 manage.py makemigrations
python3.12 manage.py migrate
python3.12 manage.py collectstatic --noinput 

echo "  BUILD END"