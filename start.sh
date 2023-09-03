#!/usr/bin/env bash
cd /home/bonce/source/jarvis_printer/

#. venv/bin/activate removed as worried about venv stealing memory
#gunicorn -w 1 -b 0.0.0.0:4000 app:app -D --log-file=gunicorn.log
gunicorn -w 1 -b 0.0.0.0:4000 app:app -D

sleep 5
