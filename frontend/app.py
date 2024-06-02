# from flask import Flask,render_template

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return render_template('index.html')
#     # return "<p>Hello, World!</p>"

# @app.route("/products")
# def products_pg():
#     return "<p>This is products page</p>"

# if __name__ == "__main__":
#     app.run(debug=True,port=8000)

import os
import sys
import subprocess
from flask import Flask, render_template, request, jsonify

# Add the parent directory of frontend to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from speechtext2 import main

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_choice', methods=['POST'])
def process_choice():
    choice = request.json['choice']
    main_with_choice = lambda: main(choice)  # Using a lambda function to pass the choice argument
    try:
        subprocess.Popen(["python", "speechtext2.py"])  # Running the speechtext2.py script
        main_with_choice()
        return jsonify({'message': 'Operation successful'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)