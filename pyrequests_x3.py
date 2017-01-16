import json, os, pprint, random, re, requests, sys, threading, time, uuid
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from lxml import etree
from os import listdir
from os.path import isfile
from signal import *


lock = threading.Lock()


def request_post(name, p, account, user_agent, proxymesh_ip):
	s = requests.session()

	images = [f for f in listdir(IMAGE_DIR) if isfile("{}{}".format(IMAGE_DIR, f))]

	# Login start
	url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
	data = {
		'username': account[0],
		'password': account[1]
	}
	headers['User-Agent'] 	= user_agent
	headers['Referer'] 		= ""
	headers['X-ProxyMesh-IP'] = proxymesh_ip

	try:
		
		response 	= s.post(url, data=data, headers=headers, proxies=p, timeout=5)
		html 		= BeautifulSoup(response.content, "html.parser")
		if html.find("li", {"class": "account"}):
			# print("{} {} {} LOGIN OK".format(name, p, account[0]))
			print("{} {} LOGIN OK".format(name, account[0]))
		elif html.find("div", {"class", "captcha"}):
			# print("{} {} {} LOGIN CAPTCHA".format(name, p, account[0]))
			print("{} {} LOGIN CAPTCHA".format(name, account[0]))
			return None
		else:
			print("{} {} LOGIN ERROR {} {}".format(name, account[0], response))
			return None
	except KeyboardInterrupt as ex:
		print("Ooopsy...")
	except Exception as ex:
		type, value, traceback = sys.exc_info()
		print("REQUESTS ERROR: {}({} line#{}) - {}".format(type.__name__, name, traceback.tb_lineno, value))
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
		response = s.post(url, data=data, headers=headers, proxies=p, timeout=5)
		captcha_response_json = json.loads(response.text)
		if 'new_album_id' not in captcha_response_json['data']:
			print("{} {} UPLOAD CHECK CAPTCHA FAILED {}".format(name, account[0], captcha_response_json['data']))
			return None
	except KeyboardInterrupt as ex:
		print("Ooopsy...")
	except Exception as ex:
		type, value, traceback = sys.exc_info()
		print("REQUESTS ERROR: {}({} line#{}) - {}".format(type.__name__, name, traceback.tb_lineno, value))
		return None

	for i in range(36):
		# upload image start
		url = "https://imgur.com/upload"
		img_filename = random.choice(images)
		img_file = open("{}{}".format(IMAGE_DIR, img_filename), "rb")

		files = {
			'Filedata': (img_filename, img_file, "image/{}".format(img_filename[img_filename.index(".") + 1:])),
			'new_album_id': (None, captcha_response_json['data']['new_album_id'])	
		}
		desc_link = ""
		try:
			response = s.post(url, files=files, headers=headers, proxies=p, timeout=15)
			response_json = json.loads(response.text)
		except KeyboardInterrupt as ex:
			print("Ooopsy...")
		except Exception as ex:
			type, value, traceback = sys.exc_info()
			print("REQUESTS ERROR: {}({}@{} line#{}) - {}".format(type.__name__, name, account[0], traceback.tb_lineno, value))
			continue
		else:
			if 'deletehash' not in response_json['data']:
				continue

		# Update image title and description start
		url = "http://imgur.com/ajax/titledesc/{}".format(response_json['data']['deletehash'])
		headers['Referer'] = "http://imgur.com/{}".format(response_json['data']['album'])
		keyword = keywords[random.randint(0, len(keywords) - 1)]
		desc = "{}&nbsp;&nbsp;{}\n\n{}\n\n{}"
		desc_link = "\n".join(["{}----{}".format(keywords[random.randint(0, len(keywords) - 1)], l) for l in links[-3:]])
		desc_website = "大奖老虎机 http://www.djyl18.com"
		random.shuffle(descriptions)
		description = random.choice(descriptions)
		update_data = {
			'title': keyword,
			'description': desc.format(keyword, desc_website.replace('.', '&#46;'), description.replace('.', '&#46;').replace("www.djyl18.com", " http://www.djyl18.com"), desc_link.replace('.', '&#46;'))
		}
		try:
			update_html = s.post(url, headers=headers, data=update_data, proxies=p, timeout=5)
		except KeyboardInterrupt as ex:
			print("Ooopsy...")
		except Exception as ex:
			type, value, traceback = sys.exc_info()
			print("REQUESTS ERROR: {}({} line#{}) - {}".format(type.__name__, name, traceback.tb_lineno, value))
			continue

		links.append("http://imgur.com/{}".format(response_json['data']['hash']))
		print("{}. http://imgur.com/{} ({} {} {})".format(len(links), response_json['data']['hash'], datetime.now() - start, name, account[0]))
		with open("data/pyrequests_x3/saveContent.txt", "a", encoding="utf-8") as f:
			f.write("http://imgur.com/{}\n".format(response_json['data']['hash']))
		with open("data/saveContent.txt", "a", encoding="utf-8") as f:
			f.write("http://imgur.com/{}\n".format(response_json['data']['hash']))


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
	if response.status_code == 200:
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
	with open("data/pyrequests_x3/checked_proxies.txt", "w", encoding="utf-8") as f:
		f.write("\n".join(checked_proxies))


def main():
	global accounts, domain, headers, keywords, links, proxies, start, user_agents

	proxies = []
	with open("data/pyrequests_x3/checked_proxies.txt", "r") as f:
		for proxy in f.readlines():
			px = {
				'http': 'http://{}'.format(proxy), 
				'https': 'https://{}'.format(proxy)
			}
			proxies.append(px)

	accounts = []
	with open("data/pyrequests_x3/账号active.txt", "r") as f:
		for account in f.readlines():
			accounts.append(tuple(account.strip().split("----")))

	keywords = []
	with open("data/pyrequests_x3/keywords.txt", "r") as f:
		keywords = [key.rstrip() for key in f.readlines()]

	user_agents = []
	with open("data/pyrequests_x3/user_agents.txt", "r") as f:
		user_agents = list(json.loads(f.read()).values())

	headers = {}

	print("{} proxies(IP:PORT) loaded.".format(len(proxies)))
	print("{} accounts loaded.".format(len(accounts)))
	print("{} user-agents loaded.".format(len(user_agents)))

	domain = "http://www.imgur.com"
	start = datetime.now()
	threads_num = 5

	print("Requesting {} ({})".format(domain, start))
	for p in proxies:
		random.shuffle(accounts)
		random.shuffle(user_agents)
		threads = []
		for i in range(threads_num):
			t_acc = accounts[i]
			t_ua = user_agents[i]
			t = threading.Thread(target = request_post, args = ("Thread-{}".format(i), p, t_acc, t_ua))
			threads.append(t)

			t.start()

		for t in threads:
			t.join()
		lock.acquire()
		lock.release()

def main_proxymesh():
	global accounts, domain, headers, IMAGE_DIR, keywords, links, proxies, start, user_agents, descriptions

	accounts = []
	with open("data/pyrequests_x3/账号active.txt", "r") as f:
		for account in f.readlines():
			accounts.append(tuple(account.strip().split("----")))

	keywords = []
	with open("data/pyrequests_x3/keywords.txt", "r") as f:
		keywords = [key.rstrip() for key in f.readlines()]

	descriptions = []
	with open("data/descriptions.txt", "r") as f:
		descriptions = [key.rstrip() for key in f.readlines()]

	user_agents = []
	with open("data/pyrequests_x3/user_agents.txt", "r") as f:
		user_agents = list(json.loads(f.read()).values())

	headers = {}
	links = []

	domain = "http://www.imgur.com"
	IMAGE_DIR = "images/"
	start = datetime.now()
	# threads_num = 5
	threads_num = 2

	print("Requesting {} ({})".format(domain, start))

	proxys = {
		'http': 'http://winner88:qweasd321@fr.proxymesh.com:31280', 
		'https': 'http://winner88:qweasd321@fr.proxymesh.com:31280'
	}

	proxymesh_ips = []
	for n in range(1, 101):
		response = requests.get('http://httpbin.org/ip', proxies=proxys)
		if 'X-ProxyMesh-IP' in response.headers:
			if response.headers['X-ProxyMesh-IP'] not in proxymesh_ips:
				proxymesh_ips.append(response.headers['X-ProxyMesh-IP'])

	print("{} accounts loaded.".format(len(accounts)))
	print("{} user-agents loaded.".format(len(user_agents)))
	print("{} proxymesh IPs gathered.".format(proxymesh_ips))
	
	counter = 0
	proxy_counter = 0
	threads = []
	while True:
		proxymesh_ip = proxymesh_ips[proxy_counter]
		for i in range(threads_num):
			if counter < len(accounts):
				t_acc = accounts[counter]
				random.shuffle(user_agents)
				t_ua = random.choice(user_agents)
				t = threading.Thread(target = request_post, args = ("Thread-{}".format(i), proxys, t_acc, t_ua, proxymesh_ip))
				threads.append(t)

				t.start()
			counter += 1

		for t in threads:
			t.join()
		lock.acquire()
		lock.release()

		proxy_counter += 1
		if proxy_counter >= len(proxymesh_ips):
			proxy_counter = 0
			print("Going back to first proxymesh IP.")

		if counter >= len(accounts):
			break

def validate_account():
	accounts = []
	with open("data/pyrequests_x3/账号.txt", "r") as f:
		for account in f.readlines():
			accounts.append(tuple(account.strip().split("----")))

	url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"

	user_agents = []
	with open("data/pyrequests_x3/user_agents.txt", "r") as f:
		user_agents = list(json.loads(f.read()).values())
	
	headers= {}
	headers['Referer'] = ""
	proxys = {
		'http': 'http://winner88:qweasd321@fr.proxymesh.com:31280', 
		'https': 'http://winner88:qweasd321@fr.proxymesh.com:31280'
	}
	for i, account in enumerate(accounts):
		data = {
			'username': account[0],
			'password': account[1]
		}
		random.shuffle(user_agents)
		headers['User-Agent'] 	= random.choice(user_agents)
		try:
			s 			= requests.session()
			response 	= s.post(url, data=data, headers=headers, proxies=proxys, timeout=5)
			html 		= BeautifulSoup(response.content, "html.parser")
			if html.find("li", {"class": "account"}):
				with open("data/pyrequests_x3/账号active.txt", "a", encoding="utf-8") as f:
					f.write("{}----{}\n".format(account[0], account[1]))
				accounts.pop(i)
				print("{} OK".format(account[0]))
			elif html.find("div", {"class", "captcha"}):
				print("{} CAPTCHA".format(account[0]))
			else:
				print("{} ERROR".format(account[0]))
		except KeyboardInterrupt as ex:
			pass
		except Exception as ex:
			type, value, traceback = sys.exc_info()
			print("ERROR: {}({} line#{}) - {}".format(type.__name__, account[0], traceback.tb_lineno, value))

	with open("data/pyrequests_x3/账号.txt", "w", encoding="utf-8") as f:
		for a in accounts:
			f.write("{}----{}\n".format(a[0], a[1]))

if __name__ == "__main__":
	while True:
		# get_proxies()

		# main()
		# validate_account()
		main_proxymesh()
		print("Sleeping for 5mins...")
		time.sleep(300)