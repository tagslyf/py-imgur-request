import json, os, pprint, random, re, requests, threading, uuid
from datetime import datetime, timedelta
from lxml import etree
from signal import *
from time import time


lock = threading.Lock()

def check_proxy(name, p):
	url = 'http://httpbin.org/ip'
	s = requests.session()
	headers = {
		# 'User-agent': random.choice(user_agents)
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
	global checked_proxies, user_agents
	# url = "https://www.sslproxies.org/"
	# url = "http://www.xicidaili.com/nn/"
	url = "https://www.sslproxies.org/"
	response = requests.get(url)
	html_tree = etree.HTML(response.content)
	# proxys = ["{}:{}".format(tr[0].text, tr[1].text) for tr in html_tree.xpath("//table[@id='proxylisttable']/tbody/tr")]
	# proxys = ["{}:{}".format(tr[1].text, tr[2].text) for index, tr in enumerate(html_tree.xpath("//table[@id='ip_list']/tr"))][1:]
	# proxys = [ip.strip() for ip in re.findall(r'r/>(.*?)<b', response.text, re.S)]

	proxys = []
	user_agents = get_user_agents()

	for tr in html_tree.xpath("//table[@id='proxylisttable']/tbody/tr"):
		if tr[4].text == "elite proxy" and tr[6].text == "yes":
			proxys.append("{}:{}".format(tr[0].text, tr[1].text))

	print(proxys, len(proxys))

	threads_num = 2
	checked_proxies = []
	while proxys:
		threads = []
		for i in range(threads_num):
			p = proxys.pop()
			
			t = threading.Thread(target = check_proxy, args = ("Thread-{}".format(i), p))
			threads.append(t)
			t.start()

		for t in threads:
			t.join()
			# proxy = "{}:{}".format(tr[0].text, tr[1].text)
	# with open("proxies.txt", "w", encoding="utf-8") as f:
	# 	f.write("\n".join(proxys))

	# with open("proxies.txt", "r", encoding="utf-8") as f:
	# 	proxys = [proxy.rstrip() for proxy in f]
			# print("CHECKING {}".format(proxy))
			# try:
			# 	url = 'http://httpbin.org/ip'
			# 	s = requests.session()
			# 	headers = {
			# 		'User-agent': random.choice(user_agents)
			# 	}
			# 	proxies = {
			# 		'http': 'http://{}'.format(proxy),
			# 		'https': 'https://{}'.format(proxy),
			# 		'ftp': '{}'.format(proxy),
			# 	}
			# 	response = s.get(url, headers=headers, proxies=proxies, timeout=15)
			# 	print("WORKING", response, json.loads(response.text)['origin'] if response.status_code == 200 else '')
			# 	if response.status_code == 200 and 'origin' in json.loads(response.text):
			# 		# with open("proxies.txt", "w", encoding="utf-8") as f:
			# 		# 	f.write("\n".join(proxys))

			# 		# with open("active_proxy.txt", "w", encoding="utf-8") as f:
			# 		# 	f.write(proxy)

			# 		# return proxy
			# 		proxys.append(proxy)
			# except Exception as e:
			# 	print("ERROR: {}".format(e))
			# 	# create function to log errors
			# 	pass
	print(checked_proxies)

def savecontent(links):
	with open("saveContent.txt", "w", encoding="utf-8") as f:
		for link in links:
			f.write("{}\n".format(link))
		f.close()

def validate():
	print("VALIDATING ACCOUNTS.")
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
			html = s.post(url, data, headers=headers, proxies=proxies, timeout=15)
			html_tree = etree.HTML(html.content)
			print(html, html.status_code, data, html_tree.xpath("//div[@class='dropdown-footer']"), html_tree.xpath("//div[@class='captcha']"))
			if html_tree.xpath("//div[@class='dropdown-footer']"):
				accounts_active.append("{}----{}".format(account[0], account[1]))
			else:
				accounts_inactive.append("{}----{}".format(account[0], account[1]))
		except Exception as e:
			print("ERROR: {}".format(e))
		except HTTPSConnectionPool as e:
			print("Proxy error.")
		s.cookies.clear()
		s.close()

	print("ACTIVE: {}".format(accounts_active))
	print("INACTIVE: {}".format(accounts_inactive))

	with open("账号active.txt", "w", encoding="utf-8") as f:
		f.write("\n".join(accounts_active))

	with open("账号inactive.txt", "w", encoding="utf-8") as f:
		f.write("\n".join(accounts_inactive))

def request_post(s):
	# upload URL http://imgur.com/upload; need to send request first in captcha URL https://imgur.com/upload/checkcaptcha
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 
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
	try:
		upload_captcha_html = s.post(upload_captcha_url, headers=headers, data=data, proxies=proxy, timeout=15)
	except Exception as e:
		print("An exception of type {0} occured (Proxy: {1}). Arguments:\n{2!r}".format(type(ex).__name__, proxy, ex.args))
		upload_captcha_html = s.post(upload_captcha_url, data=data, headers=headers)
	print(upload_captcha_url, upload_captcha_html, upload_captcha_html.content, upload_captcha_html.text, upload_captcha_html.request.headers)

	upload_captcha_response = json.loads(upload_captcha_html.text)

	post_url = "https://imgur.com/upload"
	png_file = open('thumbnail00.png', 'rb')
	
	files = {
		'Filedata': ('thumbnail00.png', png_file, 'image/png'),
		'new_album_id': (None, upload_captcha_response['data']['new_album_id'])	
	}

	try:
		post_html = s.post(post_url, files=files, headers=headers, proxies=proxy, timeout=15)
	except Exception as e:
		print("An exception of type {0} occured (Proxy: {1}). Arguments:\n{2!r}".format(type(ex).__name__, proxy, ex.args))
		post_html = s.post(post_url, files=files, headers=headers)
	print(post_url, post_html, post_html.text)

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
	try:
		update_html = s.post(update_url, data=data, headers=headers, proxies=proxy, timeout=15)
	except Exception as e:
		print("An exception of type {0} occured (Proxy: {1}). Arguments:\n{2!r}".format(type(ex).__name__, proxy, ex.args))
		update_html = s.post(update_url, data=data, headers=headers)
	print(update_html)

def get_user_agents():
	user_agents = []
	with open("user_agents.txt", "r") as f:
		for ua in f:
			user_agents.append(ua.rstrip())
	random.shuffle(user_agents)
	return user_agents

def main():
	keywords = []
	links = []
	accounts = []
	proxy = ""

	with open("keywords.txt", "r", encoding="utf-8") as f:
		keywords = [key.rstrip() for key in f]

	with open("账号active.txt", "r", encoding='utf-8') as f:
		accounts = [tuple(account.rstrip().split("----")) for account in f]

	with open("active_proxy.txt", "r", encoding='utf-8') as f:
		proxy = [p.rstrip() for p in f] [0]
		proxy = {
			'http': 'http://{}'.format(proxy),
			'https': 'https://{}'.format(proxy),
			'ftp': '{}'.format(proxy),
		}

	url = "http://www.imgur.com"
	counter = 0
	start = datetime.now()
	start_time = time()

	print("Requesting {} ({})".format(url, start))
	while True:
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
		try:
			html = s.post(login_url, data=login_data, headers=headers, proxies=proxy, timeout=15)
		except Exception as e:
			print("An exception of type {0} occured (Proxy: {1}). Arguments:\n{2!r}".format(type(ex).__name__, proxy, ex.args))
			html = s.post(login_url, data=login_data, headers=headers)
		print(login_url, html, login_data)

		# call post here

		s.cookies.clear()
		s.close()

		counter += 1
		if counter >= len(accounts):
			counter = 0

		if (time() - start_time) >= 1800:
			savecontent(links)
			print("Upload is running for 30m. Stop!")
			break

if __name__ == "__main__":
	get_proxies()
	# validate() # Validate accounts
	# main()