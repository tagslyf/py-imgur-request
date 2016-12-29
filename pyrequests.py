import json, os, pprint, random, re, requests, threading, uuid
from datetime import datetime, timedelta
from lxml import etree
from signal import *
from time import time


lock = threading.Lock()


def request_post(name, s, d):
	try:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0', 
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
			
			upload_captcha_html = s.post(upload_captcha_url, data=data, headers=headers)
		except KeyError as ex:
			print("{} {} error {}:{} TRYING TO REQUEST WITH PROXY ({})".format(d['username'], d['proxy'], type(ex).__name__, ex.args, datetime.now() - start))
			for ip in ips:
				try:
					proxies = {
						'http': 'http://{}'.format(ip),
						'https': 'https://{}'.format(ip),
						'ftp': '{}'.format(ip),
					}
					upload_captcha_html = s.post(upload_captcha_url, data=data, headers=headers, proxies=proxies)
					break
				except Exception as ex:
					print("Upload captcha using {} failed. Will try again.".format(ip))

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
		rep['upload_summary'][d['username'].strip()]['links'].append("http://imgur.com/{}".format(post_html_response['data']['hash']))
		rep['upload_summary'][d['username'].strip()]['total_post'] += 1
		print("{}. {} {} http://imgur.com/{} ({})".format(len(links), d['username'], d['proxy'], post_html_response['data']['hash'], datetime.now() - start))

		# Update image title and description
		update_url = "http://imgur.com/ajax/titledesc/{}".format(post_html_response['data']['deletehash'])
		headers = {
			'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0', 
			'referer': 'http://imgur.com/{}'.format(post_html_response['data']['album'])
		}
		keyword = keywords[random.randint(0, len(keywords) - 1)]
		data = {
			'title': keyword,
			'description': "{}&nbsp;&nbsp;{}\n\n{}".format(keyword, '大奖老虎机 http://www.Q82019309.com', desc_link)
		}
		update_html = s.post(update_url, data=data, headers=headers)
	except NameError as ex:
		print("{} {} error {}:{!r} ({})".format(d['username'], d['proxy'], type(ex).__name__, ex.args, datetime.now() - start))
	except Exception as ex:
		print("{} {} error {} ({})".format(d['username'], d['proxy'], type(ex).__name__, datetime.now() - start))
		pass


def request_login(data, headers, p):
	url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
	try:
		s = requests.session()
		html = s.post(url, data=data, headers=headers, proxies=p, timeout=15)
		html_tree = etree.HTML(html.content)
		if html_tree.xpath("//div[@class='dropdown-footer']"):
			print("{} {} logged in.".format(data['username'], p['ftp']))
			return s
		else:
			print("{} {} Encountered captcha.".format(data['username'], p['ftp']))
			return None
		s.cookies.clear()
		s.close()
	except Exception as ex:
		print("{} {} error {}.".format(data['username'], p['ftp'], type(ex).__name__))
		return None


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
	url = "https://www.sslproxies.org/"
	response = requests.get(url)
	html_tree = etree.HTML(response.content)
	proxys = []

	for tr in html_tree.xpath("//table[@id='proxylisttable']/tbody/tr"):
		if tr[4].text == "elite proxy" and tr[6].text == "yes":
			proxys.append("{}:{}".format(tr[0].text, tr[1].text))

	print(proxys, len(proxys))

	threads_num = 2
	checked_proxies = []
	while proxys:
		threads = []
		for i in range(threads_num):
			if proxys:
				p = proxys.pop()
				
				t = threading.Thread(target = check_proxy, args = ("Thread-{}".format(i), p))
				threads.append(t)
				t.start()

		for t in threads:
			t.join()

	print(checked_proxies, len(checked_proxies))
	with open("checked_proxies.txt", "w", encoding="utf-8") as f:
		f.write("\n".join(checked_proxies))


def savecontent(links):
	if links:
		with open("saveContent.txt", "w", encoding="utf-8") as f:
			for link in links:
				f.write("{}\n".format(link))
			f.close()

	if rep:
		with open("reports.txt", "w", encoding="utf-8") as f:
			if rep["upload_summary"]:
				pprint.pprint(rep, f)

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


def check_accounts():
	global active_accounts

	active_accounts = []
	
	threads_num = 2
	print("Verifying accounts")
	for account in accounts:
		# login
		threads = []
		for i in range(threads_num):
			t = threading.Thread(target = validate_account, args = ("Thread-{}".format(i), account))
			threads.append(t)
			t.start()

		for t in threads:
			t.join()

	print("ACTIVE: {}".format(active_accounts))
	with open("账号active.txt", "w", encoding="utf8") as f:
		f.write("\n".join(active_accounts))
		f.close()

	with open("账号inactive.txt", "w", encoding="utf-8") as f:
		for account in accounts:
			if "{}----{}".format(account[0], account[1]) not in active_accounts:
				f.write("{}----{}\n".format(account[0], account[1]))
		f.close()

def get_user_agents():
	user_agents = []
	with open("user_agents.txt", "r") as f:
		for ua in f:
			user_agents.append(ua.rstrip())
	random.shuffle(user_agents)
	return user_agents


def main():
	global active_accounts, keywords, links, start, rep

	active_accounts = []
	with open("账号active.txt", "r", encoding="utf-8") as f:
		active_accounts = [tuple(acc.rstrip().split("----")) for acc in f]
	domain = "http://www.imgur.com"
	counter = 0
	keywords = []
	with open("keywords.txt", "r", encoding="utf-8") as f:
		keywords = [key.rstrip() for key in f]
	links = []
	rep = {}
	rep['upload_summary'] = {}
	start = datetime.now()
	start_time = time()
	threads_num = 40

	print("Requesting {} ({})".format(domain, start))
	try:
		while True:
			account = active_accounts[counter]

			for p in ips:
				# login
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

				if account[0] not in rep['upload_summary']:
					rep['upload_summary'][account[0]] = {
						'links': [],
						'total_post': 0
					}

				s = request_login(data, headers, proxies)

				if type(s).__name__ is "Session":
					threads = []
					for i in range(threads_num):
						d = {
							'username': account[0],
							'proxy': p
						}

						t = threading.Thread(target = request_post, args = ("Thread-{}".format(i), s, d))
						threads.append(t)
						t.start()

					for t in threads:
						t.join()

					lock.acquire()
					lock.release()

					s.cookies.clear()
					s.close()

			counter += 1
			if counter >= len(active_accounts):
				if len(links) == 0:
					print("You are uploading os fast.")
					break
				counter = 0

			if (time() - start_time) >= 7200:
				savecontent(links)
				print("Upload is running for 30m. Stop!")
				break
	except KeyboardInterrupt:
		savecontent(links)
		print(rep)
	except Exception as ex:
		savecontent(links)
		print(rep)
		print("error {} ({}).".format(d['username'], d['proxy'], type(ex).__name__, datetime.now() - start))


if __name__ == "__main__":
	global accounts, ips, user_agents

	get_proxies()

	accounts = []
	with open("账号.txt", "r", encoding='utf-8') as f:
		accounts = [tuple(account.rstrip().split("----")) for account in f]
	print("{} accounts loaded".format(len(accounts)))

	ips = []
	with open("checked_proxies.txt", "r", encoding="utf-8") as f:
		ips = [p.rstrip() for p in f]
	print("{} proxy(ip:port) loaded".format(len(ips)))

	user_agents = []
	with open("user_agents.txt", "r", encoding="utf-8") as f:
		user_agents = [ua.rstrip() for ua in f]
	print("{} user agents loaded.".format(len(user_agents)))

	check_accounts()
	# main()