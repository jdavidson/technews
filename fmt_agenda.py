import StringIO
import unicodecsv

# Descriptions of columns to show in output
header_descrs = ['Company',
                 'Contacts',
                 'Description',
                 'Sector',
                 'Round',
                 'Deal Team',
                 'Days in Status']

# names of relateiq columns that map to columns to use (ignored RIQ columns won't show up)
header_cols = ['Name',
               'Contacts',
               'Description',
               'Sector',
               'Round',
               'Deal Team',
               'Days in Current Status']

# sizes (for bootstrap) of each column above - should add up to 12
header_sizes = [2,2,3,2,1,1,1]

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
#        print "replacing %s with %s" % ("{{ " + header[col] + " }}", row[col])

    return text

def format_table_header():
    output = ""
    for i in range(len(header_descrs)):
        output += '<th class="span%s">%s</th>\n' % (header_sizes[i], header_descrs[i])
    return output

def format_agenda(data):
    df = StringIO.StringIO(unicode(data).encode("utf-8"))
    reader = unicodecsv.reader(df, delimiter='\t')
    header = reader.next() # get the column headers
    status_col = header.index('Status')
    days_col = header.index('Days in Current Status')
    last_status = ""
    output = ""

    sorted_reader = sorted(reader, key=lambda x:
            (status_order[x[status_col]], int(x[days_col]) if x[days_col].isdigit() else 0))

    for row in sorted_reader:
        # iterate through the rest of the rows and create the data structure
        if row[status_col] != last_status:
            # add a column to break up the statuses
            output += '<tr class="status_row"><td colspan=%s>%s</td></tr>\n' % (len(header_cols), row[status_col])
            last_status = row[status_col]

        output = output + render_row(row, header)

    return output
