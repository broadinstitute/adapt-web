sudo systemctl stop gunicorn.socket
cd adapt-web
git reset --hard
git pull origin main
yarn --cwd vue_frontend/ build
python3 manage.py makemigrations
python3 manage.py migrate
sudo systemctl start gunicorn.socket
