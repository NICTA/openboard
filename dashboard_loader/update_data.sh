#/bin/bash

source ./setpythonpath.sh

if [ $1 ]
then
	python manage.py update_data $1
else
	python manage.py update_data
fi
	
