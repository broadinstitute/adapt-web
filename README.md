# adapt-web
Web interface for using ADAPT

## Set up
If you'd like to set up on Linux, run `setup_linux.sh` (you may need to run in sudo mode). 

If you're on Mac, do all of the following steps:

To install the necessary packages for Django, run the following:
```
pip install -r requirements.txt
```

To install the necessary components for Vue, you'll need Yarn and NPM.

To install NPM, you'll need to install Node.js. You can either install from their [site](https://nodejs.org/en/download/) or install via brew by running:
```
brew install node
```

To install Yarn, run the following after NPM is installed:
```
npm install -g yarn
```

To install Vue, run:
```
npm install -g vue@next
```

To install Vue's dependencies, run:
```
yarn --cwd vue_frontend/ install
```

To update the database, run:
```
python manage.py makemigrations
python manage.py migrate
```

To build Vue into a webpack bundle, run:
```
yarn --cwd vue_frontend/ build
```

Finally, you'll need to create `api/aws_config.txt`. It should contain two lines: the first an AWS access key, the second a AWS secret access key. If you're not testing AWS functionality, you can put in gibberish for both to allow the server to compile.

## Run server

If you're running it locally, you'll need to open two terminals to run the Django and Vue servers simultaneously.

To run the Django server, run:
```
python manage.py runserver
```

To run the Vue server, run:
```
yarn --cwd vue_frontend/ serve
```
Running the Vue server is only necessary if a webpack bundle hasn't been built or if you would like updates to Vue to be applied without rebuilding the bundle.

## Directory Structure
Anything in italics is what you most likely want to edit.

### vue_frontend
Contains all of the Vue related files. The Vue server is run from inside this directory. `package.json` contains the list of dependencies; other files are general configuration files.

#### public
Any files that need to be accessible to Django directly. This includes the logo, the favicon, and a default index page (might be able to remove the index page).

#### *src*
All the parts specific to Vue.

##### assets
The site wide stylesheet (written in SCSS) and images are in this folder.

##### *components*
Contains the actual HTML/CSS/JS/Vue code. There are 20 components currently; 4 that corresponds with a page (`About.vue`, `Design.vue`, `RunADAPT.vue`, `Results.vue`), 2 for the header/footer (`Header.vue`, `Footer.vue`), 5 for visualizing assay results in a modal (`AssayModal.vue`, `AssayTable.vue`, `Assay.vue`, `Genome.vue`, and `ColorLegend.vue`), 7 for handling the expanding taxon structure (`Family.vue`, `Genus.vue`, `Species.vue`, `Subspecies.vue`, `ExpandFamily.vue`, `ExpandGenus.vue`, `ExpandSpecies.vue`), 1 message modal (`Modal.vue`), and 1 currently unused Home component (`Home.vue`).

The first section (`<template> ... </template>`) is the HTML template that Vue will insert data into.

The second section (everything in `<script> ... export default {...} </script>`) provides properties and Javascript functions for the component. `data` sets up variables for the DOM. Code in `created()` is run immediately before the component is loaded for the first time; code in `mounted()` is run immediately after the component is loaded for the first time. Functions in `methods` are accessible from the template.

The optional third section (`<style scoped> ... </style>`) is CSS that will only affect this component.

##### pages
Contains code to set up components into actual pages. In the future, we could change the components that are only one page to be made directly in that page, rather than importing them.

#### node_modules (only exists after installing Vue dependencies)
Vue dependencies will be stored in this folder.

### django_backend
Contains the code that connects Vue to Django. It sets up URL routing for each page (`urls.py`) and the settings for the Django server (`settings.py`).

### *api*
Contains the API code-the database schema (*`models.py`*), as well as functions to define the various types of requests to the API (*`views.py`*--note, a "viewset" in *`views.py`* is a class that automatically builds the basic GET/POST/PUT etc. functions). `serializers.py` defines the fields needed to put an object into the database; `urls.py` sets up URL routing to each model; `admin.py` allows access to the models via the Django admin interface (which we shouldn't need, but is set up just in case); `apps.py` sets up the API as an app to be run by the django_backend.

### templates
These are HTML files that Vue inserts into. For the most part, it's just connection between Vue and Django, but the head is made in `base.html` (including the connections to Google Fonts, Google Analytics, and Plausible Analytics).

### static (only exists after building Vue)
Contains a minified version of the static assets for Vue. Django accesses Vue's `public` folder via this.

## Production Server Structure
The production server is currently hosted on an EC2 instance on AWS. It was set up based on the instructions [this Digital Ocean tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04). This repository is located at `/home/ubuntu/adapt-web`.

Anything in italics is what you most likely want to edit.

### NGINX Configuration
NGINX is the web server for the site, listening for HTTP requests and serving static content. If you need to modify how HTTP requests/responses are handled, you likely will need to modify NGINX's configuration file at *`/etc/nginx/sites-available/django_backend`*. NGINX documentation on configuration files is [here](https://docs.nginx.com/nginx/admin-guide/web-server/web-server/).

After you update the NGINX configuration file, you will need to test that the file is valid and restart NGINX. Run:
```
sudo nginx -t && sudo systemctl restart nginx
```

To view NGINX's general logs, run:
```
sudo journalctl -u nginx
```

To view NGINX's error logs, run:
```
sudo less /var/log/nginx/error.log
```

To view NGINX's access logs, run:
```
sudo less /var/log/nginx/access.log
```

### Gunicorn Configuration
Gunicorn is the WSGI HTTP web server. It interfaces with Django to serve dynamic content. You most likely don't need to edit this.

It runs as systemd daemons.The socket file listens for connections to the server and is located at `/etc/systemd/system/gunicorn.socket`. The service file defines what to connect to and is located at `/etc/systemd/system/gunicorn.service`. If you do need to modify Gunicorn's settings, you'll need to edit the service file.

If you edit either file, you'll need to restart Gunicorn. Run:
```
sudo systemctl daemon-reload
sudo systemctl restart gunicorn.socket gunicorn.service
```

### Updating Server
If you've updated any code in this repository, push the changes to GitHub, then (on the production server) run:
```
/home/ubuntu/adapt-web/update_server.sh
```
If something goes wrong and you need to run any Django or Vue updates without using the above script, stop the Gunicorn service daemon before compiling (see `update_server.sh` as an example). It will go extremely slowly if you do not.
