sudo systemctl stop gunicorn.socket
git reset --hard
git pull origin main
sudo yarn --cwd vue_frontend/ install
yarn --cwd vue_frontend/ build
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic
sudo systemctl start gunicorn.socket
