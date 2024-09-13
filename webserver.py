from flask import flask

app = Flask('')
@app.route('/')
def home():
    return 'Discord Bot Works'

def run():
    app.run(host = '0.0.0.0', port = 8080)

def keep_alive():
    t = Tread(target = run)
    t.start()