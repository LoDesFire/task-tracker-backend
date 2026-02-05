#!/bin/bash
/code/.venv/bin/uvicorn src.web.main:app --host 0.0.0.0 --port 8000