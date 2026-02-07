    # main.py
    from flask import Flask, request, jsonify
    from firebase_functions import https
    from firebase_admin import initialize_app


    initialize_app()
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello from Flask!'

    @app.route('/api/data', methods=['GET'])
    def get_data():
        return jsonify({"message": "This is your API data!"})

