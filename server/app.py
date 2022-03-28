import logging

from flask import Flask, render_template

logging.getLogger('werkzeug').disabled = True

app = Flask(__name__)


@app.route('/')
def index() -> str:
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
