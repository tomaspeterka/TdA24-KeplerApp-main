#!/bin/sh

#grep -rs "flag{" /
find / -name '*flag*'
python3 -m flask --app app/app.py init-db
python3 -m flask --app app/app.py run --host=0.0.0.0 --port=80