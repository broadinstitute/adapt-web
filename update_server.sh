sudo systemctl stop gunicorn.socket
git reset --hard
git pull origin main
yarn --cwd vue_frontend/ build
python3 manage.py makemigrations
python3 manage.py migrate
sudo systemctl start gunicorn.socket
