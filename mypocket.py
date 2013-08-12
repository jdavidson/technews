import api, os, pickle, urllib2
import threading
from urllib2 import HTTPError

ckey = os.environ['POCKET_CONSUMER_KEY']
source_string = "[Source: "
end_source_string = "]"
initial_html = "### Market Analysis and Industry News\n\n### Product Releases\n\n### Company Announcements\n\n### Talent\n\n### Exits\n\n### Venture Capital\n\n"

def get_initial_html():
    return initial_html

def fill_in_source(item):
    source = ""
    # first look for a pando-daily style [Source: ] string
    if source_string in item['text']:
        source_string_start = item['text'].find(source_string) + len(source_string)
        source_string_end = item['text'].find(end_source_string)
        source = item['text'][source_string_start:source_string_end]
        # also remove the source notation from the text
        item['text'] = item['text'][0:item['text'].find(source_string)]
    else:
        # not found, so let's just figure it out from the url
        url = item['url']
        domain_start = url.find("http://")
        if domain_start == -1:
            domain_start = url.find("https://") + len("https://")
        else:
            domain_start += len("http://")
        domain_end = url.find("/", domain_start)
        domain = url[domain_start:domain_end] # just split out the domain
        domain = domain[0:domain.rfind(".")]  # and remove the last bit (.com etc)
        if "." in domain:
            domain = domain[domain.find(".")+1:]
        if len(domain) < 4:
            domain = domain.upper()
        else:
            domain = domain[0].upper() + domain[1:]
        source = domain
    item['source'] = source
    # if it's a pando one, use the new download (but slower) method
    if is_pando_source(item):
        item = fill_in_pando_source(item)
    return item

# may do nothing if it couldn't understand the page, in which case it just returns the item
def fill_in_pando_source(item):
    try:
        data = urllib2.urlopen(item['url'])
    except HTTPError as error:
        print "failed to load url: %s" % item['url']
        return item

    html = data.read()
    s = html.split('[Source: ')[1].split('</a>')[0].split('">')
    link = s[0].split('="')[1]
    source = s[1]
    if link[0:7] == 'http://':
        print "updated a pando source"
        item['url'] = link
        item['source'] = source

    return item

def is_pando_source(item):
    return item['url'][0:27] == u'http://pandodaily.com/news/'

def count_items():
    pocket = setup_pocket()
    items = get_items(pocket)
    return len(items['list'])

def get_items(pocket):
    items = pocket.get()
    return items

def setup_pocket():
    pocket = ''
    f = os.path.expanduser(os.path.join('~', '.config', 'pocket.txt'))
    if os.path.exists(f):
        with file(f, 'r') as target:
            data = pickle.load(target)
        consumerkey = data['consumer_key']
        pocket = api.API(consumerkey)
        pocket.authenticate(data['access_token'])
    elif 'POCKET_ACCESS_KEY' in os.environ:
        pocket = api.API(ckey)
        pocket.authenticate(os.environ['POCKET_ACCESS_KEY'])
    else:
        print "AUTHENTICATION FAILED - UNDEFINED FOR NOW"
        pocket = api.API(ckey)
        pocket.authenticate()
        data = {'consumer_key': ckey,
                'access_token': api.access_token,
                'contentType': 'article',
                'detailType': 'complete'}
        with file(f, 'w') as target:
            pickle.dump(data, target)
    return pocket

# v2 with threading!
def parse_items(items):
    # convert into something more usable
    new_items = []

    for index in items['list']:
        item = items['list'][index]
        # create the new item
        new_item = {'text': item['excerpt'],
                    'url': item['resolved_url'],
                    'title': item['resolved_title']}
        # figure out the source
        # new_item = fill_in_source(new_item)
        new_items.append(new_item)

    threads = [threading.Thread(target=fill_in_source, args=(item,)) for item in new_items]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return new_items

def convert_to_markdown(items):
    # convert into markdown
    text = ""
    sources = ""

    for item in items:
        text += "_%s_:: %s [%s][%d]\n\n" % (item['title'], item['text'], item['source'], items.index(item))
        sources += "\n[%d]: %s" % (items.index(item), item['url'])

    return text + "\n" + sources

def gimme_markdown(include_html=True):
    pocket = setup_pocket()
    items = get_items(pocket)
    new_items = parse_items(items)
    markdown = convert_to_markdown(new_items)

    if include_html:
        markdown = initial_html + markdown

    return markdown, len(items['list'])

def archive_all_items():
    pocket = setup_pocket()
    items = get_items(pocket)
    if len(items['list']) > 0:
        status = archive_items_commit(pocket, items['list'].keys())
        if status['status'] == 1:
            return 'Archived %d items' % (len(items['list']))
        else:
            return status['action_results']
    else:
        return 'Nothing to Archive'

def archive_items_commit(pocket, item_ids):
    for item_id in item_ids:
        pocket.actions.append(('archive', {'action': 'archive', 'item_id': item_id}))
    return pocket.commit()

if __name__ == '__main__':
    print gimme_markdown()