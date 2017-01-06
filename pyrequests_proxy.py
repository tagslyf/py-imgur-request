import json, os, pprint, random, re, requests, threading, time, uuid
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from lxml import etree
from signal import *


lock = threading.Lock()


def request_post(name, p):
	proxys = {
		'http': 'http://{}'.format(p),
		'https': 'https://{}'.format(p),
		'ftp': '{}'.format(p),
	}
	for account in accounts:
		s = requests.session()

		# Login start
		url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
		data = {
			'username': account[0],
			'password': account[1]
		}
		headers['User-Agent'] 	= "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
		headers['Referer'] 		= ""
		try:
			
			response 	= s.post(url, data=data, headers=headers, proxies=p, timeout=15)
			html 		= BeautifulSoup(response.content, "html.parser")
			if html.find("li", {"class": "account"}):
				print("{} {} {} LOGIN OK".format(name, p, account[0]))
			elif html.find("div", {"class", "captcha"}):
				print("{} {} {} LOGIN CAPTCHA".format(name, p, account[0]))
				return None
			else:
				print("{} {} {} LOGIN ERROR".format(name, p, account[0]))
				return None
		except Exception as ex:
			print("{} {} {} LOGIN EX {}".format(name, p, account[0], ex))
			return None

		# Check captcha upload image start
		url = "https://imgur.com/upload/checkcaptcha"
		data = {
			'total_uploads': 1,
			'create_album': 'true'
		}
		headers['Referer'] 			= "https://imgur.com/"
		headers['Host'] 			= "imgur.com"
		headers['Origin'] 			= "https://imgur.com"
		headers['Accept-Language']	= "en-US,en;q=0.8"
		try:
			response = s.post(upload_captcha_url, data=data, headers=headers)
			response_json = json.loads(response.text)
			if 'new_album_id' not in response_json['data']:
				print("{} {} {} UPLOAD CHECK CAPTCHA FAILED {}".format(name, p, account[0], response_json['data']))
				return None
		except Exception as ex:
			print("{} {} {} LOGIN EX {}".format(name, p, account[0], ex))
			return None

		for i in range(100):
			# upload image start
			url = "https://imgur.com/upload"
			png_file = open("images/thumbnail00.png", "rb")

			files = {
				'Filedata': ("thumbnail00.png", png_file, "image/png"),
				'new_album_id': (None, response_json['data']['new_album_id'])	
			}
			desc_link = ""
			try:
				response = s.post(post_url, files=files, headers=headers)
				response_json = json.loads(response.text)

				desc_link = "\n".join(links[-3:])
				links.append("http://imgur.com/{}".format(response_json['data']['hash']))
				print("{}. http://imgur.com/{} ({} {} {} {})".format(len(links), response_json['data']['hash'], name, p, account[0], datetime.now() - start))
			except Exception as e:
				print("{} {} {} UPLOAD IMAGE FAILED".format(name, p, account[0]))
				continue

			# Update image title and description start
			url = "http://imgur.com/ajax/titledesc/{}".format(response_json['data']['deletehash'])
			headers['Referer'] = "http://imgur.com/{}".format(response_json['data']['album'])
			keyword = keywords[random.randint(0, len(keywords) - 1)]
			data = {
				'title': keyword,
				'description': "{} {}&nbsp;&nbsp;{}\n\n{}".format(i, keyword, "大奖老虎机 http://www.Q82019309.com", desc_link)
			}
			try:
				update_html = s.post(update_url, data=data, headers=headers)
			except Exception as e:
				print("{} {} {} UDPATE TITLE/DESC FAILED".format(name, p, account[0]))
				continue


def check_proxy(name, p):
	url = 'http://httpbin.org/ip'
	s = requests.session()
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
	}
	proxies = {
		'http': 'http://{}'.format(p),
		'https': 'https://{}'.format(p),
		'ftp': '{}'.format(p),
	}
	try:
		response = s.get(url, headers=headers, proxies=proxies, timeout=3)
		print("{} WORKING".format(p), response, json.loads(response.text)['origin'] if response.status_code == 200 else '')
		if response.status_code == 200 and 'origin' in json.loads(response.text):
			checked_proxies.append(p)
	except Exception as ex:
		print("{0} An exception of type {1} occured. Arguments:\n{2!r}".format(p, type(ex).__name__, ex.args))
		# create function to log errors
		pass
	s.cookies.clear()
	s.close()

	lock.acquire()
	lock.release()


def get_proxies():
	global checked_proxies

	# need to add more site to scrape proxy ip address
	# Proxy available from this site https://www.sslproxies.org/
	url = "https://www.sslproxies.org/"
	response = requests.get(url)
	html_tree = etree.HTML(response.content)
	proxys = []

	for tr in html_tree.xpath("//table[@id='proxylisttable']/tbody/tr"):
		if tr[4].text == "elite proxy" and tr[6].text == "yes":
			proxys.append("{}:{}".format(tr[0].text, tr[1].text))

	# Proxy available from this site http://www.kuaidaili.com/free/outtr/
	url = "http://www.kuaidaili.com/free/outtr/"
	response = requests.get(url)
	html = BeautifulSoup(response.content, "html.parser")
	for tr in html.find("table").findAll("tr"):
		if tr.find("td"):
			proxys.append("{}:{}".format(tr.find("td", {'data-title': "IP"}).string,tr.find("td", {'data-title': "PORT"}).string))

	print(proxys, len(proxys))

	threads_num = 2
	checked_proxies = []
	while proxys:
		threads = []
		for i in range(threads_num):
			if proxys:
				p = proxys.pop(0)
				
				t = threading.Thread(target = check_proxy, args = ("Thread-{}".format(i), p))
				threads.append(t)
				t.start()

		for t in threads:
			t.join()

	print(checked_proxies, len(checked_proxies))
	with open("data/pyrequests_proxy/checked_proxies.txt", "w", encoding="utf-8") as f:
		f.write("\n".join(checked_proxies))


def savecontent(links):
	with open("saveContent.txt", "w", encoding="utf-8") as f:
		for link in links:
			f.write("{}\n".format(link))
		f.close()


def validate_account(name, account):
	for p in ips:
		if "{}----{}".format(account[0], account[1]) in active_accounts:
				break

		data = {
			'username': account[0], 
			'password': account[1]
		}
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
			'referer': ''
		}
		proxies = {
			'http': 'http://{}'.format(p),
			'https': 'https://{}'.format(p),
			'ftp': '{}'.format(p)
		}

		s = request_login(data, headers, proxies)

		if type(s).__name__ is "Session":
			if "{}----{}".format(account[0], account[1]) not in active_accounts:
				active_accounts.append("{}----{}".format(account[0], account[1]))


def main():
	global accounts, domain, headers, keywords, links, proxies, start

	proxies = []
	with open("data/pyrequests_proxy/checked_proxies.txt", "r") as f:
		for proxy in f.readlines():
			proxies.append(proxy.strip())

	accounts = []
	with open("data/pyrequests_proxy/账号.txt", "r") as f:
		for account in f.readlines():
			accounts.append(tuple(account.strip().split("----")))

	keywords = []
	with open("data/pyrequests_proxy/keywords.txt", "r") as f:
		keywords = [key.rstrip() for key in f.readlines()]

	headers = {}

	print("{} proxies(IP:PORT) loaded.".format(len(proxies)))
	print("{} accounts loaded.".format(len(accounts)))

	domain = "http://www.imgur.com"
	start = datetime.now()
	threads_num = 2

	print("Requesting {} ({})".format(domain, start))
	for p in proxies:
		threads = []
		for i in range(threads_num):
			t = threading.Thread(target = request_post, args = ("Thread-{}".format(i), p))
			threads.append(t)

			t.start()

		for t in threads:
			t.join()
		lock.acquire()
		lock.release()

if __name__ == "__main__":
	### I have this just to test all IPs for just 1 account and 1 browser only
	while True:
		get_proxies()

		main()
		time.sleep(120)