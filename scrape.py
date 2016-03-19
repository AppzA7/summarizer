import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup
import urllib2

import re
citations = re.compile('(\[((\d*)|(citation needed))\])|\|', re.DOTALL)

fout = open('hw2.txt', 'w')

urls = ["https://en.wikipedia.org/wiki/Dwight_D._Eisenhower","https://en.wikipedia.org/wiki/John_F._Kennedy","https://en.wikipedia.org/wiki/Lyndon_B._Johnson","https://en.wikipedia.org/wiki/Richard_Nixon","https://en.wikipedia.org/wiki/Gerald_Ford","https://en.wikipedia.org/wiki/Jimmy_Carter","https://en.wikipedia.org/wiki/Ronald_Reagan","https://en.wikipedia.org/wiki/Bill_Clinton","https://en.wikipedia.org/wiki/George_W._Bush","https://en.wikipedia.org/wiki/Barack_Obama"]

for url in urls:
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	page = response.read()

	soup = BeautifulSoup(page, 'html.parser')

	ps = soup.find(id="mw-content-text")

	for div in ps.find_all("div", {'class':'reflist'}): 
		div.decompose()

	ps = ps.find_all('p')

	for p in ps:
		ptext = p.get_text()
		ptext = re.sub(citations, "", ptext)

		lines = ptext.split("\n")

		for l in lines:
			if len(l) > 0:
				if l[-1] == ".": #remove lines that don't end in '.', make exception for long lines incase '.'' is missing
					fout.write(l + "\n")

	print(url + " ...DONE!")

fout.close()