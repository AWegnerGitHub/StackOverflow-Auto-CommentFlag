@echo off
rem Batch Script to Run FlaskPanel
rem
rem This will add the current directory to the python path temporarily, allowing the use of
rem import models appropriately

setlocal
SET PYTHONPATH=.

python FlaskPanel\app.py