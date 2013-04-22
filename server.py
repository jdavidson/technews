from flask import Flask, request, url_for, render_template, Response
import mypocket, build, read_excel
import boto
from boto.s3.key import Key

s3bucketid = 'cchild-technews'

app = Flask(__name__)
conn = boto.connect_s3()

## Static Files (this is cheating and should be moved to amazon)
@app.route('/bootstrap.css')
def return_css():
    return open('bootstrap.css').read()

@app.route('/bootstrap.js')
def return_js():
    return open('bootstrap.js').read()

## show the last saved news file
@app.route('/')
def base_page():
    bucket = conn.get_bucket(s3bucketid)
    k = bucket.get_key(build.strFile() + '.html')
    if k:
        return k.get_contents_as_string()
    else:
        return "This week's news hasn't been posted yet. <a href='" + url_for('old_news') + "'>Last Week</a>"

@app.route('/last_week/')
def old_news():
    print "old_news"
    bucket = conn.get_bucket(s3bucketid)
    print "bucket: %s" % (build.strLastFile() + '.html')
    k = bucket.get_key(build.strLastFile() + '.html')
    print "k"
    if k:
        return k.get_contents_as_string()
    else:
        return "Can't find last week's news.  Sorry."

## still in progress - you need to post a url to an excel file which isn't all that great, but it does work
@app.route('/financings/', methods=['GET', 'POST'])
def convert_financings():
    if request.method == 'POST':
        url = request.form['url']
        table = read_excel.parse_url(url)
        return render_template('financings.html', table=table, date=build.strMonday())
    else:
        return render_template('enter_excel.html', action=url_for('convert_financings'))

## show the markdown for the news
@app.route('/news/')
def get_news():
    return Response(mypocket.gimme_markdown(), mimetype="text/plain")

## convert the default markdown to html
@app.route('/news/html')
def get_news_html():
    return build.convert_news(mypocket.gimme_markdown(), '')

## convert submitted markdown to html, and potentially save it
@app.route('/convert/', methods=['GET', 'POST'])
def convert_news():
    if request.method == 'POST':
        html = build.convert_news(request.form['news_text'], '')
        if request.form.has_key('save') and request.form['save'] == 'save':
            # should add some form of security here
            bucket = conn.get_bucket(s3bucketid)
            k = Key(bucket)
            k.key = build.strFile() + '.html'
            k.set_contents_from_string(html)
        return html
    else:
        action = url_for('convert_news')
        return render_template('enter_news.html', action=action, text='')

## show the markdown convert dialog with the news filled in
@app.route('/convert/news')
def convert_shown_news():
    action = url_for('convert_news')
    text = mypocket.gimme_markdown()
    return render_template('enter_news.html', action=action, text=text)

## archive everything (separate action so you are sure when you want to do it) - just dumps out status
@app.route('/archive/', methods=['GET', 'POST'])
def archive_news():
    if request.method == 'POST':
        return mypocket.archive_all_items()
    else:
        count = mypocket.count_items()
        return render_template('archive_confirm.html', action=url_for('archive_news'), count=count)

if __name__ == '__main__':
    app.run(debug=True)