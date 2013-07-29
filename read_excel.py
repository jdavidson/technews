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

def companies_in_sheet(sheet):
    companies = []

    for row in range(8, sheet.nrows):
        company = {'name' : sheet.cell(row, 1).value.encode('ascii', errors='ignore').strip(),
                'description' : sheet.cell(row, 3).value.encode('ascii', errors='ignore').strip(),
                'transaction_value' : sheet.cell(row, 4).value,
                'investors' : sheet.cell(row, 5).value.encode('ascii', errors='ignore').strip(),
                'long_description' : sheet.cell(row, 6).value.encode('ascii', errors='ignore').strip()}
        companies.append(company)

    return companies

def companies_to_html(companies):
    html = '<table class="table table-striped">\n'
    html += '<thead>\n<tr>\n<td>Company</td>\n<td>Description</td>\n<td>$</td>\n<td>Investors</td>\n</tr>\n</thead>\n'
    html = ''
    for company in companies:
        html += str.format("<tr>\n<td>%s</td>\n<td>%s</td>\n<td style='text-align: center'>%s</td>\n<td>%s</td>\n</tr>\n" %
            (company['name'],
             company['description'],
             str(company['transaction_value']),
             company['investors']))

    return html


if __name__ == '__main__':
    print parse_file(open('news.xls'))