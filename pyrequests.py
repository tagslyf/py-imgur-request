import json, os, pprint, random, re, requests, uuid
from datetime import datetime, timedelta
from lxml import etree
from signal import *
from time import time


def scrape_proxy():
	# url = "https://www.sslproxies.org/"
	# url = "http://www.xicidaili.com/nn/"
	url = "http://haoip.cc/tiqu.htm"
	headers = {
		'User-agent': 'Mozilla/5.0'
	}
	response = requests.get(url, headers=headers)
	html_tree = etree.HTML(response.content)
	# proxys = ["{}:{}".format(tr[0].text, tr[1].text) for tr in html_tree.xpath("//table[@id='proxylisttable']/tbody/tr")]
	# proxys = ["{}:{}".format(tr[1].text, tr[2].text) for index, tr in enumerate(html_tree.xpath("//table[@id='ip_list']/tr"))][1:]
	proxys = [ip.strip() for ip in re.findall(r'r/>(.*?)<b', response.text, re.S)]
	with open("proxies.txt", "w", encoding="utf-8") as f:
		f.write("\n".join(proxys))

def get_proxies():
	with open("proxies.txt", "r", encoding="utf-8") as f:
		proxys = [proxy.rstrip() for proxy in f]

	user_agents = [
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Safari/537.1",
		"Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
		"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
		"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
		"Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
		"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
		"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
		"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
		"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
		"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
		"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
	]

	while proxys:
		proxy = proxys.pop()
		print("CHECKING {}".format(proxy))

		try:
			url = 'http://httpbin.org/ip'
			s = requests.session()
			headers = {
				'User-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Safari/537.1"
			}
			proxies = {
				'http': 'http://{}'.format(proxy),
				'https': 'https://{}'.format(proxy),
				'ftp': '{}'.format(proxy),
			}
			response = s.get(url, headers=headers, proxies=proxies, timeout=180)
			print(response.status_code)
			if response.status_code == 200:
				with open("proxies.txt", "w", encoding="utf-8") as f:
					f.write("\n".join(proxys))

				with open("active_proxy.txt", "w", encoding="utf-8") as f:
					f.write(proxy)

				return proxy
			print("WORKING", response, response.content if response.status_code == 200 else '')
		except Exception as e:
			print("ERROR: {}".format(e))
			# create function to log errors
			pass

def savecontent(links):
	with open("saveContent.txt", "w", encoding="utf-8") as f:
		for link in links:
			f.write("{}\n".format(link))
		f.close()

def validate():
	print("VALIDATIG ACCOUNTS.")
	accounts = []
	with open("账号.txt", "r", encoding='utf-8') as f:
		accounts = [tuple(account.rstrip().split("----")) for account in f]

	proxy = ""
	with open("active_proxy.txt", "r", encoding="utf-8") as f:
		for ip in f:
			proxy = ip.rstrip() 
	print("PROXY: {}".format(proxy))

	accounts_active = []
	accounts_inactive = []

	for account in accounts:
		try:
			s = requests.session()

			# login
			url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
			data = {
				'username': account[0], 
				'password': account[1]
			}
			headers = {
				# 'User-agent': 'Mozilla/5.0', 
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
				'referer': ''
			}
			proxies = {
				'http': 'http://{}'.format(proxy),
				'https': 'https://{}'.format(proxy),
				'ftp': '{}'.format(proxy)
			}
			print("SENDING REQUEST: {} {}  {}".format(proxies, data, headers))
			html = s.post(url, data, headers=headers, proxies=proxies, timeout=180)
			html_tree = etree.HTML(html.content)
			print(html, html.status_code, data, html_tree.xpath("//div[@class='dropdown-footer']"), html_tree.xpath("//div[@class='captcha']"))
			if html_tree.xpath("//div[@class='dropdown-footer']"):
				accounts_active.append("{}----{}".format(account[0], account[1]))
			else:
				accounts_inactive.append("{}----{}".format(account[0], account[1]))
		except Exception as e:
			print("ERROR: {}".format(e))

		s.cookies.clear()
		s.close()

	print("ACTIVE: {}".format(accounts_active))
	print("INACTIVE: {}".format(accounts_inactive))

	with open("账号active.txt", "w", encoding="utf-8") as f:
		f.write("\n".join(accounts_active))

	with open("账号inactive.txt", "w", encoding="utf-8") as f:
		f.write("\n".join(accounts_inactive))

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
	scrape_proxy()
	get_proxies()
	validate() # Validate accounts
	# main()
	# scrape_proxy()