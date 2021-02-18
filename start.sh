yarn --cwd vue_frontend/ build
python3 manage.py makemigrations
python3 manage.py migrate

for cmd in "python3 manage.py runserver 0.0.0.0:8000" "yarn --cwd vue_frontend/ serve --host 0.0.0.0 --port 8080"; do {
  echo "Process \"$cmd\" started";
  $cmd & pid=$!
  PID_LIST+=" $pid";
} done

trap "kill $PID_LIST" SIGINT

echo "Parallel processes have started";

wait $PID_LIST

echo
echo "All processes have completed";
