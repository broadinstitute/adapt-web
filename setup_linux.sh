sudo apt update
sudo apt install npm
sudo apt install python3.8
sudo apt install python3-pip
sudo npm install --g yarn
sudo npm install -g vue@next
sudo yarn --cwd vue_frontend/ install
sudo pip install -r requirements.txt || sudo pip3 install -r requirements.txt
FILE=api/aws_config.txt
if [[ -f "$FILE" ]]; then
    echo "$FILE exists."
else
    echo "$FILE does not exist; making a template. Fill in with AWS Access Keys."
    touch $FILE
    echo 'INSERTACCESSKEY' >> api/aws_config.txt
    echo 'INSERTSECRETACCESSKEY' >> api/aws_config.txt
fi
