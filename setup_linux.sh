curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install yarn
sudo apt install npm
sudo apt install python3.8
sudo apt install python3-pip
sudo npm install -g vue@next
sudo npm install -g @vue/cli
sudo npm install -g @vue/cli-plugin-babel
sudo npm install -g @vue/cli-plugin-eslint
sudo npm install -g webpack-bundle-tracker
sudo pip install -r requirements.txt || sudo pip3 install -r requirements.txt
