import StringIO
import unicodecsv

# Descriptions of columns to show in output
header_descrs = ['Company',
                 'Contacts',
                 'Description',
                 'Sector',
                 'Round',
                 'Team',
                 'Days']

inactive_header_descrs = ['Company',
                          'Contacts',
                          'Description',
                          'Deal Team',
                          'Owner',
                          'Inactive']

# names of relateiq columns that map to columns to use (ignored RIQ columns won't show up)
header_cols = ['Name',
               'Contacts',
               'Description',
               'Sector',
               'Round',
               'Deal Team',
               'Days in Current Status']

inactive_header_cols = ['Name',
                        'Contacts',
                        'Description',
                        'Deal Team',
                        'Owner',
                        'Inactive (days)']

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

# sizes (for bootstrap) of each column above - should add up to 12
header_sizes = [2,2,3,2,1,1,1]
inactive_header_sizes = [2,2,3,2,2,1]

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

def render_row(row, header, header_cols=header_cols):
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
    output = ""
    hds = header_descrs
    hss = header_sizes

    for i in range(len(hds)):
        output += '<th class="span%s">%s</th>\n' % (hss[i], hds[i])
    return output

#####################
### FORMAT AGENDA ###
#####################
# main entry point.  data is the full csv from relateiq, inactive is whether to use the inactive headers or regular headers

def format_agenda(data):
    df = StringIO.StringIO(unicode(data).encode("utf-8"))
    reader = unicodecsv.reader(df, delimiter='\t')
    header = reader.next() # get the column headers, assumed to be the first row
    status_col = header.index('Status') # back into the status and days in the current status columns, since we'll need them later
    sort_col = header.index('Days in Current Status')
    hc = header_cols

    last_status = ""
    output = ""

    # sort the reader by status col, followed by sort_col (assumed to be an int, and set to 0 if not a digit)
    sorted_reader = sorted(reader, key=lambda x:
        (status_order[x[status_col]], (int(x[sort_col]) * sort_order[x[status_col]]) if x[sort_col].isdigit() else 0))

    # iterate through the sorted reader, creating new rows, and creating a status row whenever the status changes
    for row in sorted_reader:
        if row[status_col] != last_status:
            # add a column to break up the statuses
            output += '<tr class="status_row"><td colspan=%s>%s</td></tr>\n' % (len(header_cols), row[status_col])
            last_status = row[status_col]

        # render the row
        output = output + render_row(row, header, hc)

    return output
