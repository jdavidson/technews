import os, sys, datetime
import markdown2

## run with one argument - a markdown file to be converted.  Always assumes you want the dates to be the next monday (or today if it is a monday)
## needs to be converted for headless use

def convert_news(news, financings):
    template_file = open('tools/template.html', 'r')
    template = template_file.read()
    template_file.close()

    formatted_date = strMonday()
    return html_from_markdown(template, news, financings, formatted_date)

def nextMonday():
    d = datetime.datetime.now()
    nextMonday = d + (datetime.timedelta((7 - d.weekday()) % 7)) # get the next monday, inclusing (ie if today is Monday, give today)
    return nextMonday

def strFile():
    return nextMonday().strftime('%y%m%d - News')

def strMonday():
    return nextMonday().strftime('%B %d, %Y')

def html_from_markdown(template, news, financings, formatted_date):

    news_text = markdown2.markdown(news)
    financings_text = financings # do this better

    replacements = {
        '{{ DATE }}': formatted_date,
        '{{ NEWS }}': news_text,
        '{{ FINANCINGS }}': financings_text
    }

    # run the replacements
    for key, text in replacements.iteritems():
        template = template.replace(key, text)

    return template

if __name__ == '__main__':
    # format the date
    strMonday = strMonday()
    strFile = strFile()

    # get the template
    template_file = open('tools/template.html', 'r')
    template = template_file.read()
    template_file.close()

    # get the content - use argument if given, otherwise default to news.md
    md_filename = "news.md"
    if len(sys.argv) > 1:
        md_filename = sys.argv[1]
    md_file = open(md_filename, 'r')
    news_text = md_file.read()
    md_file.close()

    ## something for financings
    financings_text = ''

    # do the conversion
    output = html_from_markdown(template, news_text, financings_text, strMonday)

    # write the file
    out_file = open(strFile + '.html', 'w')
    out_file.write(output)
    out_file.close()