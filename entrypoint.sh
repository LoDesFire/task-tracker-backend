#!/bin/bash
cd ./src && /code/.venv/bin/gunicorn --bind=0.0.0.0:8000 config.wsgi