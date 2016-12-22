import json, os, pprint, random, requests, uuid
from datetime import datetime, timedelta
from lxml import etree
from signal import *
from time import time


def scrape_proxy():
	# url = "http://www.gatherproxy.com/proxylist/country/?c=Philippines"
	url = "https://www.proxynova.com/proxy-server-list/country-ph/"
	headers = {
		'User-agent': 'Mozilla/5.0'
	}
	response = requests.get(url, headers=headers)
	print(response)
	html_tree = etree.HTML(response.content)
	print(html_tree.xpath("//table[@id='tbl_proxy_list']/tbody/tr"))
	proxys = []
	for tr in html_tree.xpath("//table[@id='tbl_proxy_list']/tbody/tr"):
		ip = ""
		port = ""
		for index, td in enumerate(tr):
			print(index, td)	
			for x in td[:2]:
				print(x.text)
				if index == 0:
					ip += x.text.strip()

				if index == 1:
					port = x.text.strip()
					print(x)
		proxys.append('{}:{}'.format(ip, port))
	print(proxys)
				
	# pprint.pprint(etree.tostring(html_tree.xpath("//table[@id='tblproxy']")[0]))

def savecontent(links):
	with open("saveContent.txt", "w", encoding="utf-8") as f:
		for link in links:
			f.write("{}\n".format(link))
		f.close()

def validate():
	accounts = []
	with open("账号.txt", "r", encoding='utf-8') as f:
		accounts = [tuple(account.rstrip().split("----")) for account in f]

	for account in accounts:
		s = requests.session()

		# login
		url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
		data = {
			'username': account[0], 
			'password': account[1]
		}
		headers = {
			'User-agent': 'Mozilla/5.0', 
			'referer': ''
		}
		html = s.post(url, data, headers = headers)
		html_tree = etree.HTML(html.content)
		print(html, html.status_code, data, html_tree.xpath("//div[@class='dropdown-footer']"), html_tree.xpath("//div[@class='captcha']"))

		s.cookies.clear()
		s.close()

def main():
	keywords = []
	links = []
	accounts = []

	with open("keywords.txt", "r", encoding="utf-8") as f:
		keywords = [key.rstrip() for key in f]

	with open("账号.txt", "r", encoding='utf-8') as f:
		accounts = [tuple(account.rstrip().split("----")) for account in f]

	url = "http://www.imgur.com"
	counter = 0
	start = datetime.now()
	start_time = time()

	print("Requesting {} ({})".format(url, start))
	while True:
		try:
			s = requests.session()
			account = accounts[counter]

			# login
			login_url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
			logout_url = ""
			login_data = {
				'username': account[0], 
				'password': account[1]
			}
			headers = {
				'User-agent': 'Mozilla/5.0', 
				'referer': ''
			}
			html = s.post(login_url, login_data, headers = headers)

			# upload URL http://imgur.com/upload; need to send request first in captcha URL https://imgur.com/upload/checkcaptcha
			headers = {
				'User-Agent': 'Mozilla/5.0', 
				'Referer': 'https://imgur.com/',
				'Host': 'imgur.com',
				'Origin': 'https://imgur.com',
				'Accept-Language': 'en-US,en;q=0.8'
			}

			upload_captcha_url = "https://imgur.com/upload/checkcaptcha"
			data = {
				'total_uploads': 1,
				'create_album': 'true'
			}
			upload_captcha_html = s.post(upload_captcha_url, headers=headers, data=data)
			upload_captcha_response = json.loads(upload_captcha_html.text)

			post_url = "https://imgur.com/upload"
			png_file = open('thumbnail00.png', 'rb')
			
			files = {
				'Filedata': ('thumbnail00.png', png_file, 'image/png'),
				'new_album_id': (None, upload_captcha_response['data']['new_album_id'])		
			}

			post_html = s.post(post_url, files=files, headers=headers)
			post_html_response = json.loads(post_html.text)

			desc_link = "\n".join(links[-3:])
			links.append("http://imgur.com/{}".format(post_html_response['data']['hash']))
			print("{}. http://imgur.com/{} ({})".format(len(links), post_html_response['data']['hash'], datetime.now() - start))

			# Update image title and description
			update_url = "http://imgur.com/ajax/titledesc/{}".format(post_html_response['data']['deletehash'])
			headers = {
				'User-agent': 'Mozilla/5.0', 
				'referer': 'http://imgur.com/{}'.format(post_html_response['data']['album'])
			}
			keyword = keywords[random.randint(0, len(keywords) - 1)]
			
			data = {
				'title': keyword,
				'description': "{}&nbsp;&nbsp;{}\n\n{}".format(keyword, '大奖老虎机 http://www.Q82019309.com', desc_link)
			}
			update_html = s.post(update_url, data=data, headers=headers)

			s.cookies.clear()
			s.close()
		except KeyboardInterrupt:
			savecontent(links)
		except:
			pass

		counter += 1
		if counter >= len(accounts):
			counter = 0

		if (time() - start_time) >= 1800:
			savecontent(links)
			print("Upload is running for 30m. Stop!")
			break

if __name__ == "__main__":
	# validate() # Validate accounts
	# main()
	scrape_proxy()