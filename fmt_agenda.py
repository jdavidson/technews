import StringIO
import unicodecsv

header_cols = ['Name',
               'Contacts',
               'Description',
               'Sector',
               'Round',
               'Deal Team',
               'Days in Current Status']

status_order = {'Signed Deal': 1,
                'Diligence': 2,
                'Met': 3}

def render_row(row, header):
    text = "<tr>"
    for hc in header_cols:
        text += "<td>{{ %s }}</td>" % hc
    text += "</tr>"

    print "rendering row: %s" % row
    for col in range(len(header)):
        tr = row[col]
        if header[col] == 'Contacts':
            tr = tr.replace(',', ', ')
        text = text.replace("{{ " + header[col] + " }}", tr)
        print "replacing %s with %s" % ("{{ " + header[col] + " }}", row[col])

    return text

def format_agenda(data):
    df = StringIO.StringIO(unicode(data).encode("utf-8"))
    reader = unicodecsv.reader(df, delimiter='\t')
    header = reader.next() # get the column headers
    status_col = header.index('Status')
    days_col = header.index('Days in Current Status')
    last_status = ""
    output = ""

    sorted_reader = sorted(reader, key=lambda x: (status_order[x[status_col]], int(x[days_col])))

    for row in sorted_reader:
        # iterate through the rest of the rows and create the data structure
        if row[status_col] != last_status:
            # add a column to break up the statuses
            output += '<tr class="status_row"><td colspan=%s>%s</td></tr>\n' % (len(header_cols), row[status_col])
            last_status = row[status_col]

        output = output + render_row(row, header)

    return output
