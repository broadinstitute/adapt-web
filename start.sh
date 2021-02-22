yarn --cwd vue_frontend/ build
python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py runserver 0.0.0.0:8000 &
PID=$!
trap "kill $PID" SIGINT
wait $PID

echo
echo "Server killed";
