#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -e


if [ "x$DJANGO_PIP_INSTALL" = 'xon' ]; then
  echo "==> Running pip install"
  pip3 install --user --no-cache-dir -U -r requirements/"$DJANGO_PIP_FILE"
fi

local_python="$(python -m site --user-site)"
if [ "x$SETUP_COVERAGE_PY" = 'xon' ]; then
  echo "==> Initialize needed files and ENVs for running coverage.py"
  export COVERAGE_PROCESS_START=.coveragerc
  cp ./coverage/setup/sitecustomize.py "$local_python"
else
  rm -f "$local_python"/sitecustomize.py
fi

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
  echo "==> Running migration"
  python manage.py migrate --noinput
fi

if [ "x$DJANGO_MANAGEPY_COLLECTSTATIC" = 'xon' ]; then
  echo "==> Collecting static files"
  python manage.py collectstatic --noinput
fi

if [ "x$DJANGO_MANAGEPY_COMPILEMESSAGES" = 'xon' ]; then
  echo "==> Running compile messages for BG language"
  python manage.py compilemessages -l bg
fi

if [ "x$DJANGO_MANAGEPY_CREATE_SUPER_USER" = 'xon' ]; then
  echo "==> Creating super user"
  # printf "from django.contrib.auth.models import User\nif not User.objects.exists(): User.objects.create_superuser(*'$DJANGO_SUPER_USER'.split(':'))" | python manage.py shell
  echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$DJANGO_SUPER_USER_USERNAME').delete(); User.objects.create_superuser(username='$DJANGO_SUPER_USER_EMAIL', password='$DJANGO_SUPER_USER_PASS')" | python manage.py shell
fi

exec "$@"
