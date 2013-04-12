from flask import Flask, request, url_for, render_template, Response
import mypocket, build, read_excel
import boto
from boto.s3.key import Key

s3bucketid = 'cchild-technews'

app = Flask(__name__)
conn = boto.connect_s3()

@app.route('/')
def base_page():
    bucket = conn.get_bucket(s3bucketid)
    k = bucket.get_key(build.strFile() + '.html')
    if k:
        return k.get_contents_as_string()
    else:
        return "This week's news hasn't been posted yet, and there's no way to see last week's news yet."

@app.route('/bootstrap.css')
def return_css():
    return open('bootstrap.css').read()

@app.route('/bootstrap.js')
def return_js():
    return open('bootstrap.js').read()

@app.route('/financings/', methods=['GET', 'POST'])
def convert_financings():
    if request.method == 'POST':
        url = request.form['url']
        table = read_excel.parse_url(url)
        return render_template('financings.html', table=table, date=build.strMonday())
    else:
        return render_template('enter_excel.html', action=url_for('convert_financings'))

@app.route('/news/')
def get_news():
    return Response(mypocket.gimme_markdown(), mimetype="text/plain")

@app.route('/news/html')
def get_news_html():
    return build.convert_news(mypocket.gimme_markdown(), '')

@app.route('/convert/', methods=['GET', 'POST'])
def convert_news():
    if request.method == 'POST':
        html = build.convert_news(request.form['news_text'], '')

        if request.form['save'] == 'save':
            bucket = conn.get_bucket(s3bucketid)
            k = Key(bucket)
            k.key = build.strFile() + '.html'
            k.set_contents_from_string(html)
        return html
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