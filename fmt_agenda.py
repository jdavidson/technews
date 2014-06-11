import StringIO
import unicodecsv

# columns to display, in order.  (Displayed Name, RelateIQ Column Name, bootstrap column width (should add to 12))
columns = [('Company', 'Name', 2),
           ('Contacts', 'Contacts', 2),
           ('Description', 'Description', 3),
           ('Sector', 'Sector', 1),
           ('Round', 'Round', 1),
           ('Team', 'Deal Team', 1),
           ('Owner', 'Owner', 1),
           ('Days', 'Days in Current Status', 1),
           ('Inactive', 'Inactive (days)', 1)]

# converts names to initials.  If not in this list, will just use first and last initials
initial_translation = { 'Adil Syed': 'AS',
                        'Alex Clayton': 'AC',
                        'Allen Beasley': 'WAB',
                        'Chris Child': 'CPC',
                        'Chris Moore': 'CBM',
                        'Edward Suh': 'ES',
                        'Elliot Geidt': 'EG',
                        'Jamie Davidson': 'JD',
                        'Jeff Brody': 'JDB',
                        'Mahesh Vellanki': 'MV',
                        'Pueo Keffer': 'PGK',
                        'Ryan Sarver': 'RS',
                        'Satish Dharmaraj': 'SD',
                        'Scott Raney': 'SCR',
                        'Tim Haley': 'TMH',
                        'Tom Dyal': 'RTD',
                        'Tom Tunguz': 'TT',
                        'geoff yang': 'GYY',
                        'john walecka': 'JLW'}


# determines the order in which each status type should appear in the list
status_order = {'Signed Deal': 1,
                'Diligence': 2,
                'Met': 3}

# determines the order in which companies in each group should be sorted (sort column is set in format_agenda)
sort_order = {'Signed Deal': 1,
              'Diligence': 1,
              'Met': -1}

####################
### RENDER A ROW ###
####################
### takes a row from the relateiq csv format and, given the matching header row and a list of columns to display, creates an html row

def render_row(row, header, header_cols):
    text = "<tr>"
    for hc in header_cols:
        text += "<td>{{ %s }}</td>" % hc
    text += "</tr>"

    print "rendering row: %s" % row
    # loop through all the columns in header, and grab the associated info from row

    for col in range(len(header)):
        tr = row[col] # grab the right piece of info

        # special cases for a couple columns
        # first, contacts, add spaces after the commas to make it look better
        if header[col] == 'Contacts':
            tr = tr.replace(',', ', ')

        # second, deal team.  if empty, use the initials of the owner, either from the lookup list or generated
        if header[col] == 'Deal Team' and tr == '':
            owner = row[header.index('Owner')]
            tr = initial_translation.get(owner) or ''.join([c[0].upper() for c in owner.split(' ')]) # grab initials from initial_translation or, if they don't exist, generate them

        if header[col] == 'Owner':
            tr = initial_translation.get(tr)

        text = text.replace("{{ " + header[col] + " }}", tr)
#        print "replacing %s with %s" % ("{{ " + header[col] + " }}", row[col])

    return text

#####################
### RENDER HEADER ###
#####################
# creates a header row from the global variables for either regular agenda or inactive agenda

def format_table_header():
    output = "\n".join(['<th class="span%s">%s</th>' % (width, title) for (title, riqname, width) in columns ])
    return output

#####################
### FORMAT AGENDA ###
#####################
# main entry point.  data is the full csv from relateiq, inactive is whether to use the inactive headers or regular headers

def format_agenda(data):
    df = StringIO.StringIO(unicode(data).encode("utf-8"))
    reader = unicodecsv.reader(df, delimiter='\t')
    header = reader.next() # get the column headers, assumed to be the first row
    print "header: %s" % header
    status_col = header.index('Status') # back into the status and days in the current status columns, since we'll need them later
    sort_col = header.index('Days in Current Status')

    last_status = ""
    output = ""

    header_cols = [riqname for (title, riqname, width) in columns]
    #header_indicies = {j:i for i, j in enumerate(header)}

    # sort the reader by status col, followed by sort_col (assumed to be an int, and set to 0 if not a digit)
    sorted_reader = sorted(reader, key=lambda x:
        (status_order[x[status_col]], (int(x[sort_col]) * sort_order[x[status_col]]) if x[sort_col].isdigit() else 0))

    # iterate through the sorted reader, creating new rows, and creating a status row whenever the status changes
    for row in sorted_reader:
        if row[status_col] != last_status:
            # add a column to break up the statuses
            output += '<tr class="status_row"><td colspan=%s>%s</td></tr>\n' % (len(columns), row[status_col])
            last_status = row[status_col]

        # render the row
        output = output + render_row(row, header, header_cols)

    return output
