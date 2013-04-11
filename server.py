from flask import Flask, request, url_for, render_template, Response
import mypocket, build

app = Flask(__name__)

@app.route('/')
def base_page():
    return 'Nothing Here'

@app.route('/news/')
def get_news():
    return Response(mypocket.gimme_markdown(), mimetype="text/plain")

@app.route('/news/html')
def get_news_html():
    return build.convert_news(mypocket.gimme_markdown(), '')

@app.route('/convert/', methods=['GET', 'POST'])
def convert_news():
    if request.method == 'POST':
        return build.convert_news(request.form['news_text'], '')
    else:
        action = url_for('convert_news')
        return render_template('enter_news.html', action=action, text='')

@app.route('/convert/news')
def convert_shown_news():
    action = url_for('convert_news')
    text = mypocket.gimme_markdown()
    return render_template('enter_news.html', action=action, text=text)

if __name__ == '__main__':
    app.run(debug=True)