from flask import flask
import mypocket

app = Flask(__name__)
setup() #setup pocket

@app.route('/')
def base_page():
    return 'Not Implemented'

@app.route('/get_news/')
def get_news():
    return mypocket.gimme_markdown()

@app.route('/convert_news/')
def convert_news():
    return 'Not Implemented'



if __name__ == '__main__':
    app.run(debug=True)