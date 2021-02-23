# adapt-web
Web interface for using ADAPT

## Set up
If you'd like to set up on Linux, run `setup_linux.sh` (you may need to run in sudo mode). If you're on Mac, do the following:
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

To update the database  (only necessary if not using ./start.sh), run:
```
python manage.py makemigrations
python manage.py migrate
```

To build Vue into a webpack bundle (only necessary if not using ./start.sh), run:
```
yarn --cwd vue_frontend/ build
```

Finally, you'll need to create `api/aws_config.txt`. It should contain two lines: the first an AWS access key, the second a AWS secret access key. @priyappillai has a key she can send; if you're not testing AWS functionality, you can put in gibberish for both to allow the server to compile.

## Run server

If you would like to run the server publically, use `start.sh`. If you're running it locally, you'll need to open two terminals to run the Django and Vue servers simultaneously.

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
Contains the actual HTML/CSS/JS/Vue code. There are 4 components; each currently corresponds with a page.

The first section (`<template> ... </template>`) is the HTML template that Vue will insert data into.

The second section (everything in `<script> ... export default {...} </script>`) provides properties and Javascript functions for the component. `data` sets up variables for the DOM. Code in `mounted()` is run when the component is loaded for the first time. Functions in `methods` are accessible from the template.

The optional third section (`<style scoped> ... </style>`) is CSS that will only affect this component.

##### pages
Contains code to set up components into actual pages. Most pages are just 1 component for now, but that should change in the future (for example, the "Design" component should be usable on both the Designs page and the Results page for visualizing designs)

#### node_modules (only exists after installing Vue dependencies)
Vue dependencies will be stored in this folder.

### django_backend
Contains the code that connects Vue to Django. It sets up URL routing for each page (`urls.py`) and the settings for the Django server (`setttings.py`).

### *api*
Contains the API code-the database schema (*`models.py`*), as well as functions to define the various types of requests to the API (*`views.py`*--note, a "viewset" in `views.py` is a class that automatically builds the basic GET/POST/PUT etc. functions). `serializers.py` defines the fields needed to put an object into the database; `urls.py` sets up URL routing to each model; `admin.py` allows access to the models via the Django admin interface (which we shouldn't need, but is set up just in case); `apps.py` sets up the API as a app to be run by the django_backend.

### templates
These are HTML files that Vue inserts into. For the most part, it's just connection between Vue and Django, but the header is made in `base.html`.

### static (only exists after building Vue)
Contains a minified version of the static assets for Vue. Django accesses Vue's `public` folder via this.
