#!/bin/bash
gunicorn main:app --workers=4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
