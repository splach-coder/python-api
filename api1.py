from flask import Flask
from flask_cors import CORS
from controllers.MSC.data_controller import data_blueprint
from controllers.Invoice.data_controller import data_blueprint

app = Flask(__name__)
CORS(app)

app.register_blueprint(data_blueprint)

@app.route('/')
def home():
    return "Welcome to my API!"

if __name__ == '__main__':
    app.run(debug=True)