from flask import Flask, request, url_for, render_template, Response
import mypocket, build, read_excel
import boto
from boto.s3.key import Key
from werkzeug import secure_filename

s3bucketid = 'cchild-technews'
HTML = '.html'
MARKDOWN = '.mdown'

app = Flask(__name__)
conn = boto.connect_s3()

##############################
##### BASE NEWS RETUNERS #####
##############################

## get news from amazon, using the filename + filetype as the key, and error_msg if key doesn't exist
def get_news_aws(filename=build.strFile(), filetype=HTML, error_msg="Can't find that news.  Sorry."):
    bucket = conn.get_bucket(s3bucketid)
    k = bucket.get_key(filename + filetype)
    if k:
        return k.get_contents_as_string()
    else:
        return error_msg

@app.route('/')
def base_page():
    error_msg = "This week's news hasn't been posted yet. <a href='" + url_for('old_news') + "'>Last Week</a>"
    return get_news_aws(error_msg=error_msg)

@app.route('/mdown')
def base_markdown():
    error_msg = "This week's news hasn't been posted yet. <a href='" + url_for('old_news_mdown') + "'>Last Week</a>"
    return get_news_aws(filetype=MARKDOWN, error_msg=error_msg)

@app.route('/last_week/')
def old_news():
    filename = build.strLastFile()
    error_msg = "Can't find last week's news.  Sorry."
    return get_news_aws(filename=filename, error_msg=error_msg)

@app.route('/last_week/mdown')
def old_news_mdown():
    filename = build.strLastFile()
    error_msg = "Can't find last week's news.  Sorry."
    return get_news_aws(filename=filename, filetype=MARKDOWN, error_msg=error_msg)

##########################
##### POCKET METHODS #####
##########################

## show the markdown for the news
@app.route('/news/')
def get_news():
    return Response(mypocket.gimme_markdown(), mimetype="text/plain")

## convert the default markdown to html
@app.route('/news/html')
def get_news_html():
    return build.convert_news(mypocket.gimme_markdown(), '')

#################################
##### CONVERSION AND SAVING #####
#################################

def save_news(contents, filetype=HTML):
    bucket = conn.get_bucket(s3bucketid)
    key = Key(bucket)
    key.key = build.strFile() + filetype
    key.set_contents_from_string(contents)

## convert submitted markdown to html, and potentially save it
@app.route('/convert/', methods=['GET', 'POST'])
def convert_news():
    if request.method == 'POST':
        markdown = request.form['news_text']
        ## figure out which button was pressed
        print request.form
        if request.form.has_key('save'):
            save_news(markdown, MARKDOWN)
            return render_template('enter_news.html', action = url_for('convert_news'), text=markdown, msg_success="Saved!")
        html = build.convert_news(markdown, '')
        if request.form.has_key('publish'):
            save_news(html, HTML)
            save_news(markdown, MARKDOWN)
        return html
    else:
        action = url_for('convert_news')
        return render_template('enter_news.html', action=action, text='')

## show the markdown convert dialog with the news filled in - kind of a useless endpoint but oh well
@app.route('/convert/news')
def convert_shown_news():
    action = url_for('convert_news')
    text = mypocket.gimme_markdown()
    return render_template('enter_news.html', action=action, text=text)

## saveable and re-workable conversion template (this is where I'm trying to replace the need for an editor)
@app.route('/convert/edit')
def convert_edit():
    print "got request"
    action = url_for('convert_news')
    action_load_raw = url_for('convert_shown_news')
    action_load_saved = url_for('convert_edit')
    error_msg = 'NOT_FOUND'
    print "getting text from aws"
    text = get_news_aws(filetype=MARKDOWN, error_msg=error_msg)
    print "got text from aws"
    if text == error_msg:
        text = mypocket.gimme_markdown()
        print "couldn't get text from aws, grabbed from pocket instead"
    else:
        print "got text from aws, decoding"
        text = text.decode('utf-8')
    return render_template('enter_news.html', action=action, text=text)

## archive everything (separate action so you are sure when you want to do it) - just dumps out status
## this (along with saving) should have some sort of authentication built in
@app.route('/archive/', methods=['GET', 'POST'])
def archive_news():
    if request.method == 'POST':
        return mypocket.archive_all_items()
    else:
        count = mypocket.count_items()
        return render_template('archive_confirm.html', action=url_for('archive_news'), count=count)

## still in progress - you need to post a url to an excel file which isn't all that great, but it does work
## formatting is all screwed up though.  need to fix that
@app.route('/financings/', methods=['GET', 'POST'])
def convert_financings():
    if request.method == 'POST':
        url = request.form['url']
        table = read_excel.parse_url(url)
        return render_template('financings.html', table=table, date=build.strMonday())
    else:
        return render_template('enter_excel.html', action=url_for('convert_financings'), action_file=url_for('convert_financing_file'))

def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1] in set(['xls',])

## upload and read a financing file
## note that financings are not saved to S3 right now, so you have to save the output
@app.route('/financings_file/', methods=['POST',])
def convert_financing_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            table = read_excel.parse_file(file)
            return render_template('financings.html', table=table, date=build.strMonday())
        else:
            return 'Error parsing file'
    else:
        return redirect(url_for('convert_financings'))

if __name__ == '__main__':
    app.run(debug=True)