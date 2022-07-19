import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

search_term = input("> Which item are you looking for? ")
print('Searching . . .')
url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131"
page = requests.get(url).text
doc = BeautifulSoup(page, "html.parser")

page_text = doc.find(class_="list-tool-pagination-text").strong
pages = int(str(page_text).split("/")[-2].split(">")[-1][:-1])

items_found = {}


def find_items(pages):
    items = []
    for page in range(1, pages + 1):
        url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131&page={page}"
        page = requests.get(url).text
        doc = BeautifulSoup(page, "html.parser")

        div = doc.find(class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
        items = div.find_all(text=re.compile(search_term))
    return items


def run_scraping(items):
    for item in items:
        parent = item.parent
        if parent.name != "a":
            continue

        link = parent['href']
        next_parent = item.find_parent(class_="item-container")
        try:
            price = next_parent.find(class_="price-current").find("strong").string
            items_found[item] = {"price": int(price.replace(",", "")), "link": link}
        except:
            pass
    return items_found


def print_on_pdf(srtd_items):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', size=30)
    pdf.cell(200, 10, txt=f"PRODUCT SCRAPER", ln=1, align='C')
    pdf.cell(200, 10, txt="", ln=1, align='C')
    pdf.set_font('Arial', size=20)
    pdf.cell(200, 10, txt=f"Products found for {search_term} :", ln=1, align='C')
    pdf.set_font('Arial', size=10)
    pdf.cell(200, 10, txt=" ", ln=1, align='C')
    i = 1

    for item in srtd_items:
        pdf.cell(200, 10, txt='Item #' + str(i) + ':', ln=1, align='C')
        pdf.cell(200, 10, txt=str(item[0])[:50], ln=1, align='C')
        pdf.cell(200, 10, txt=str(item[1]['price']) + '$', ln=1, align='C')
        pdf.cell(200, 10, txt=str(item[1]['link']), ln=1, align='C')
        pdf.cell(200, 10, txt="", ln=1, align='C')
        i += 1

    pdf.cell(200, 10, txt=" ", ln=1, align='C')
    now = datetime.now()
    t = now.strftime("%m/%d/%Y, %H:%M:%S")
    pdf_footer = "Data taken from " + str(url) + " at " + str(t)
    pdf.cell(200, 10, txt=pdf_footer, ln=1, align='C')
    pdf.output('products_found.pdf')


def main():
    items_found_from_scraping = run_scraping(find_items(pages))
    if not items_found_from_scraping:
        print('No elements found!')
    else:
        sorted_items = sorted(items_found_from_scraping.items(), key=lambda x: x[1]['price'])

        for item in sorted_items:
            print(item[0])
            print(f"${item[1]['price']}")
            print(item[1]['link'])
            print("-------------------------------")
        print_on_pdf(sorted_items)


main()
