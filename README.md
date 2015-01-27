[![Stories in Ready](https://badge.waffle.io/librekpi/librekpi.svg?label=ready&title=Ready)](http://waffle.io/librekpi/librekpi) [![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/LibreKPI/librekpi?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
# librekpi

A web-service exposing freely available information about university majors, courses and individual lectures. Feedback-driven.

## dev
### Prerequisites
Ensure that you have `mongodb` service running. Also you may want to modify config/dev/app.py and/or environment variables to make some initial configuration (prior to issuing the last command). Default port is 8888.
### Execution
```bash
$ git clone git@github.com:LibreKPI/librekpi.git
$ cd librekpi
$ virtualenv -p python3.4 .env
$ . .env/bin/activate
(.env)$ pip install -r requirements.txt
(.env)$ python src/librekpi/app.py
```
Now you may open http://localhost:8888/ in your browser.
