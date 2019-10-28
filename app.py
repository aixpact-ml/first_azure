#!/usr/bin/env python

# # If application.py
# gunicorn --bind=0.0.0.0 --timeout 600 application:app
# # If app.py
# gunicorn --bind=0.0.0.0 --timeout 600 app:app
# # If hello.py
# gunicorn --bind='0.0.0.0' --timeout=600 hello:app

# For local debugging
# from hello import app

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True, port=8241)
