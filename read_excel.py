from xlrd import open_workbook
import urllib2


def parse_url(url):
    data = urllib2.urlopen(url)
    excel_data = data.read()
    return parse_data(excel_data)


def parse_file(file):
    excel_data = file.read()
    return parse_data(excel_data)


def parse_data(excel_data):
    book = open_workbook(file_contents=excel_data)
    sheet = book.sheet_by_index(0)
    companies = companies_in_sheet(sheet)
    html = companies_to_html(companies)
    return html


def short_comments(name, comments):
    print "parsing: (%s, %s)" % (name, comments)

    if comments.find(name) == 0:
        st = comments.replace(name, '')
        loc = st.find('. ')
        if loc == -1:
            loc = st.find('.')
        loc += len(name) + 1
    else:
        loc = comments.find('. ') + 1
        if loc == 0:
            loc = comments.find('.') + 1
    return comments[0:loc]


def companies_in_sheet(sheet):
    companies = []

    for row in range(8, sheet.nrows):
        name = sheet.cell(row, 1).value.encode('ascii', errors='ignore').strip()
        comments = sheet.cell(row, 7).value.encode('ascii', errors='ignore').strip()
        company = {'name': name,
                   'description': sheet.cell(row, 3).value.encode('ascii', errors='ignore').strip(),
                   'transaction_value': sheet.cell(row, 4).value,
                   'investors': sheet.cell(row, 5).value.encode('ascii', errors='ignore').strip(),
                   'long_description': sheet.cell(row, 6).value.encode('ascii', errors='ignore').strip(),
                   'comments': short_comments(name, comments)}
        companies.append(company)

    return companies


def companies_to_html(companies):
    html = ''
    fmt_html = "<tr>\n<td>%s</td>\n<td>%s</td>\n<td style='text-align: center'>%s</td>\n<td>%s</td><td>%s</td>\n</tr>\n"
    for company in companies:
        html += str.format(fmt_html %
                           (company['name'],
                            company['description'],
                            str(company['transaction_value']),
                            company['investors'],
                            company['comments']))

    return html


if __name__ == '__main__':
    print parse_file(open('news.xls'))
