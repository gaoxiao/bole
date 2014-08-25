bole
=====================


Getting Started:

    pip install -r requirements.txt
	python manage.py loaddata data.dat
    python manage.py syncdb
    python manage.py runserver
    
Before search, run:
	
	copy whoosh_cn_backend.py to %python_path%\Lib\site-packages\haystack\backends
	python manage.py rebuild_index
