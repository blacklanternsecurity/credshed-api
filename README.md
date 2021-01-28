# credshed-api
REST API for Credshed

## Deployment

* Clone repo recursively
~~~
$ git clone --recursive https://github.com/blacklanternsecurity/credshed-api && cd credshed-api
~~~

* Follow instructions in `./lib/credshed/README.md` to set up the credshed mongo backend

* (Optional) Build the Vue.js frontend
~~~
$ cd lib/credshed-gui

# install node.js
$ apt install npm

# install dependencies
$ npm install

# test, if you want
$ npm run serve

# build for production
$ npm run build
~~~

* Bring up the API via docker-compose
NOTE: make sure you're back inside the `credshed-api` directory
~~~
$ docker-compose up
~~~