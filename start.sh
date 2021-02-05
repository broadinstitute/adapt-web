yarn --cwd vue_frontend/ build
python manage.py makemigrations
python manage.py migrate

for cmd in "python manage.py runserver 0.0.0.0:8000" "yarn --cwd vue_frontend/ serve --mode production --host 0.0.0.0 --port 8080"; do {
  echo "Process \"$cmd\" started";
  $cmd & pid=$!
  PID_LIST+=" $pid";
} done

trap "kill $PID_LIST" SIGINT

echo "Parallel processes have started";

wait $PID_LIST

echo
echo "All processes have completed";
