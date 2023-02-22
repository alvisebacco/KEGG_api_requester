from Bio.KEGG import Enzyme
from Bio.KEGG import REST
from flask import Flask
from model.esercizi import Api


def create_app():
    application = Flask(__name__)
    application.register_blueprint(Api().api_to_k(), url_prefix='/api')
    return application


if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5001, debug=False)




