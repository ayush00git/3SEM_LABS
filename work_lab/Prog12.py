from flask import Flask 

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Hey welcome to the flask web server</h1>"

@app.route('/home')
def hello():
    return f"<h1>Hey name</h1>"

if __name__ == '__main__':
    app.run(debug=True)