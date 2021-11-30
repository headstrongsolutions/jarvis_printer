#!/usr/bin/env bash
cd /source/jarvis_printer/

. venv/bin/activate
gunicorn -w 1 -b 0.0.0.0 app:app -D --log-file=gunicorn.log

