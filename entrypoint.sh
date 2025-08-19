#!/bin/bash

set -e


if [ "$1" = "celery" ]; then

  exec "$@"
else
  BLUE="\e[34m"
  ENDCOLOR="\e[0m"

  echo -e "${BLUE} ============================================================== ${ENDCOLOR}"

  echo -e "${BLUE} Running migrations... ${ENDCOLOR}"
  python manage.py makemigrations --merge
  python manage.py migrate --noinput

  echo -e "${BLUE} Collecting static... ${ENDCOLOR}"
  python manage.py collectstatic --noinput

  echo -e "${BLUE} All done! Will start guinicorn ${ENDCOLOR}"
  echo -e "${BLUE} ============================================================== ${ENDCOLOR}"

  gunicorn prestamos.wsgi:application --bind 0.0.0.0:8000 --workers 3 --reload
fi