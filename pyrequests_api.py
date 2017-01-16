import json, os, random, requests, sys, threading, time
from base64 import b64encode
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from lxml import etree
from os import listdir
from os.path import isfile

lock = threading.Lock()


def request_api(name, url, headers, proxys, proxymesh_ip):
	IMAGE_DIR = "images/"

	desc = "{}\n\n\n{}\n\n{}"
	images = [f for f in listdir(IMAGE_DIR) if isfile("{}{}".format(IMAGE_DIR, f))]
	img = random.choice(image_urls)
	random.shuffle(promos)
	promo = random.choice(promos)
	random.shuffle(contents)
	content = "	{}\n\n".format(", ".join(contents[:random.randint(5,10)]))
	for n in range(random.randint(2,3)):
		random.shuffle(contents)
		content += "	{}\n".format(", ".join(contents[:random.randint(5,10)]))
	headers['X-ProxyMesh-IP'] = proxymesh_ip

	for i in range(req_limit):
		try:
			title = titles[random.randint(0, len(titles) - 1)]
			desc_link = "\n".join(["{} ---- {}".format(l, titles[random.randint(0, len(titles) - 1)]) for l in links[-3:]])
			data = {
				'image': img,
				'title': title,
				'description': desc.format(promo, content, desc_link).replace('.', '&#46;')
			}
			response = requests.post(url, headers=headers, data=data, proxies=proxys, timeout=5)
			if response.status_code == 200:
				response_data = response.json()['data']
				link = "{}{}".format(domain, response_data['id'])
				links.append(link)
				with open("data/pyrequests_api/saveContent.txt", "a", encoding="utf-8") as f:
					f.write("{}\n".format(link))
				with open("data/saveContent.txt", "a", encoding="utf-8") as f:
					f.write("{}\n".format(link))
				print("{}. {} ({} {} {})".format(len(links), link, datetime.now() - start, name, proxymesh_ip)) # temporary for testing of proxymesh
				write_upload_log(proxymesh_ip, 'API:{}'.format(name), link)
			elif response.status_code == 400 and "You are uploading too fast" in response.json()['data']['error']:
				write_upload_log(proxymesh_ip, 'API', response.json()['data']['error'])
				break
			else:
				write_upload_log(proxymesh_ip, 'API', "{}".format(response.json()['data']['error']) if response.json() else response.text)
		except Exception as ex:
			type, value, traceback = sys.exc_info()
			write_upload_log(proxymesh_ip, 'API', "REQUESTS ERROR: {}({}@{} line#{}) - {}".format(type.__name__, name, i + 1, traceback.tb_lineno, value))
			if type.__name__ in ['SSLError', 'ProxyError']:
				break


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
		print("{} OK".format(p))
		if response.status_code == 200 and 'origin' in json.loads(response.text):
			checked_proxies.append(p)
	except Exception as ex:
		print("{} BAD".format(p))
		pass
	s.cookies.clear()
	s.close()

	lock.acquire()
	lock.release()


def get_proxies():
	global checked_proxies
	url = "https://www.sslproxies.org/"
	response = requests.get(url)
	html = BeautifulSoup(response.content, "html.parser")
	proxys = []
	for tr in html.find("table", {'id': "proxylisttable"}).find('tbody').findAll ('tr'):
		if tr:
			tds = tr.findAll('td')
			if tds[4].string == 'elite proxy' and tds[6].string == 'yes':
				proxys.append("{}:{}".format(tds[0].string, tds[1].string))
	threads_num = 10
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
	with open("data/pyrequests_api/checked_proxies.txt", "w", encoding="utf-8") as f:
		f.write("\n".join(checked_proxies))


def main():
	global domain, keywords, links, proxies, req_limit, start, descriptions
	counter = 0
	domain = "http://imgur.com/"
	keywords = []
	with open("data/keywords.txt", "r") as f:
		keywords = [key.rstrip() for key in f.readlines()]
	descriptions = []
	with open("data/descriptions.txt", "r") as f:
		descriptions = [key.rstrip() for key in f.readlines()]
	links = []
	proxies = []
	with open("data/pyrequests_api/checked_proxies.txt", "r") as f:
		for proxy in f.readlines():
			proxies.append(proxy.strip())
	req_limit = 100
	start = datetime.now()
	threads_num = 2
	url = "https://api.imgur.com/3/image"
	img_file = open("images/thumbnail00.jpg", "rb").read()
	files = {'Filedata': ("thumbnail00.jpg", img_file, "image/jpg")}
	headers = {}
	headers['Authorization'] = "Client-ID e8e0297762a5593"
	print("Start API request.")
	while True:
		proxys = {
			'https': "https://{}".format(proxies[counter]),
			'http': "http://{}".format(proxies[counter]),
			'ftp': "{}".format(proxies[counter])
		}

		threads = []
		for i in range(threads_num):
			t = threading.Thread(target = request_api, args = ("Thread-{}".format(i), url, headers, proxys))
			threads.append(t)
			t.start()

		for t in threads:
			t.join()

		counter += 1
		if counter >= len(proxies):
			print("Returning to first proxy in the list.")
			counter = 0
			break # For now break loop after go all proxy. 


def proxymesh_api():
	global contents, domain, image_urls, titles, links, req_limit, start, promos
	domain = "http://imgur.com/"
	print("Start API request using proxmesh proxy. ({})".format(datetime.now()))
	titles = []
	with open("data/titles.txt", "r") as f:
		titles = [key.rstrip() for key in f.readlines()]
	promos = []
	with open("data/promos.txt", "r") as f:
		promos = [key.rstrip() for key in f.readlines()]
	contents = []
	with open("data/contents.txt", "r") as f:
		contents = [key.rstrip() for key in f.readlines()]
	image_urls = ['http://i.imgur.com/4BoBLeK.jpg', 'https://i.imgbox.com/5eveR18P.jpg', 'http://i64.tinypic.com/n5mudx.jpg', 'http://thumbsnap.com/i/WOv9HaHv.jpg?0116']
	links = []
	req_limit = 100
	start = datetime.now()
	threads_num = 2
	url = "https://api.imgur.com/3/image"
	headers = {}
	headers['Authorization'] = "Client-ID e8e0297762a5593"
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

	proxy_counter = 0
	print("{} proxymesh IPs gathered.".format(proxymesh_ips))
	write_upload_log(proxymesh_ips, 'API', 'Proxymesh current IP address given.')
	while True:
		threads = []
		for i in range(threads_num):
			proxymesh_ip = proxymesh_ips[proxy_counter]
			t = threading.Thread(target = request_api, args = ("Thread-{}".format(i), url, headers, proxys, proxymesh_ip))
			threads.append(t)
			t.start()
			proxy_counter += 1
			if proxy_counter >= len(proxymesh_ips):
				print("Going back to first IP. Break threads")
				break
		for t in threads:
			t.join()
		if proxy_counter >= len(proxymesh_ips):
			print("Going back to first IP. Exit process using proxymesh IPs.")
			break


def checkedproxy_api():
	global domain, contents, image_urls, links, promos, req_limit, start, titles
	domain = "http://imgur.com/"
	print("Start API request using scraped proxies. ({})".format(datetime.now()))
	titles = []
	with open("data/titles.txt", "r") as f:
		titles = [key.rstrip() for key in f.readlines()]
	promos = []
	with open("data/promos.txt", "r") as f:
		promos = [key.rstrip() for key in f.readlines()]
	contents = []
	with open("data/contents.txt", "r") as f:
		contents = [key.rstrip() for key in f.readlines()]
	image_urls = ['http://i.imgur.com/4BoBLeK.jpg', 'https://i.imgbox.com/5eveR18P.jpg', 'http://i64.tinypic.com/n5mudx.jpg', 'http://thumbsnap.com/i/WOv9HaHv.jpg?0116']
	get_proxies()
	checked_proxies = []
	with open("data/pyrequests_api/checked_proxies.txt", "r") as f:
		for p in f.readlines():
			checked_proxies.append(p.rstrip())
	proxy_counter = 0
	links = []
	req_limit = 100
	start = datetime.now()
	threads_num = 2
	url = "https://api.imgur.com/3/image"
	headers = {}
	headers['Authorization'] = "Client-ID e8e0297762a5593"
	print("{} scraped proxies loaded".format(len(checked_proxies)))
	write_upload_log(checked_proxies, 'API', 'Scraped proxies current IP address.')
	while True:
		threads = []
		for i in range(threads_num):
			proxy_ip = checked_proxies[proxy_counter]
			proxys = {
				'http': 'http://{}'.format(proxy_ip),
				'https': 'https://{}'.format(proxy_ip)
			}
			t = threading.Thread(target = request_api, args = ("Thread-{}".format(i), url, headers, proxys, proxy_ip))
			threads.append(t)
			t.start()
			proxy_counter += 1
			if proxy_counter >= len(checked_proxies):
				print("Going back to first IP. Break threads")
				break
		for t in threads:
			t.join()
		if proxy_counter >= len(checked_proxies):
			print("Going back to first IP. Exit process using scraped proxys' IPs.")
			break

def checkproxy(name, gather_proxy, counter):	
	url = 'http://httpbin.org/ip'
	proxies = {
		'http': 'http:{}'.format(gather_proxy),
		'https': 'http:{}'.format(gather_proxy),
	}
	try:
		rsp = requests.get(url, proxies=proxies, timeout=10)
	except Exception as e:
		print("{}. {} {} {}".format(counter + 1, name, gather_proxy, "BAD"))
	else:
		print("{}. {} {} {}".format(counter + 1, name, gather_proxy, "OK"))
		ok2get_proxy.append(gather_proxy)
	lock.acquire()
	lock.release()


def check_gatherproxy():
	global gather_proxy, DATA_DIR, ok2get_proxy
	DATA_DIR = "data/pyrequests_api/"
	gather_proxies = []
	ok2get_proxy = []
	with open("{}{}".format(DATA_DIR, "gather_proxy.txt"), "r") as f:
		for proxy in f:
			gather_proxies.append(proxy.rstrip())
	start = datetime.now()
	threads_num = 30
	counter = 0
	proxyloop = True
	while proxyloop:
		threads = []
		for i in range(threads_num):
			proxy = gather_proxies[counter]
			t = threading.Thread(target = checkproxy, args = ("Thread-{}".format(i), proxy, counter))
			threads.append(t)
			t.start()
			counter += 1
			if counter >= len(gather_proxies):
				proxyloop = False
				break
		for t in threads:
			t.join()
	print("Loaded proxy... Total: {} OK: {} BAD: {} (Process timed {})".format(len(gather_proxies), len(ok2get_proxy), len(gather_proxies) - len(ok2get_proxy), datetime.now() - start))
	with open("{}{}".format(DATA_DIR, "gatherok_proxies.txt"), "w") as f:
		for proxy in ok2get_proxy:
			f.write("{}\n".format(proxy))


def gatherproxy_api():
	global contents, domain, image_urls, links, promos, req_limit, start, titles
	domain = "http://imgur.com/"
	print("Start API request using gather proxies. ({})".format(datetime.now()))
	titles = []
	with open("data/titles.txt", "r") as f:
		titles = [key.rstrip() for key in f.readlines()]
	promos = []
	with open("data/promos.txt", "r") as f:
		promos = [key.rstrip() for key in f.readlines()]
	contents = []
	with open("data/contents.txt", "r") as f:
		contents = [key.rstrip() for key in f.readlines()]
	image_urls = ['http://i.imgur.com/4BoBLeK.jpg', 'https://i.imgbox.com/5eveR18P.jpg', 'http://i64.tinypic.com/n5mudx.jpg', 'http://thumbsnap.com/i/WOv9HaHv.jpg?0116']
	check_gatherproxy()
	checked_proxies = []
	with open("data/pyrequests_api/gatherok_proxies.txt", "r") as f:
		for p in f.readlines():
			checked_proxies.append(p.rstrip())
	proxy_counter = 0
	links = []
	req_limit = 100
	start = datetime.now()
	threads_num = 2
	url = "https://api.imgur.com/3/image"
	headers = {}
	headers['Authorization'] = "Client-ID e8e0297762a5593"
	print("{} scraped proxies loaded".format(len(checked_proxies)))
	write_upload_log(checked_proxies, 'API', 'Scraped proxies current IP address.')
	while True:
		threads = []
		for i in range(threads_num):
			proxy_ip = checked_proxies[proxy_counter]
			proxys = {
				'http': 'http://{}'.format(proxy_ip),
				'https': 'https://{}'.format(proxy_ip)
			}
			t = threading.Thread(target = request_api, args = ("Thread-{}".format(i), url, headers, proxys, proxy_ip))
			threads.append(t)
			t.start()
			proxy_counter += 1
			if proxy_counter >= len(checked_proxies):
				print("Going back to first IP. Break threads")
				break
		for t in threads:
			t.join()
		if proxy_counter >= len(checked_proxies):
			print("Going back to first IP. Exit process using scraped proxys' IPs.")
			break


def write_upload_log(ip, username, message):
	with open("data/pyrequests_api/uploadlog_{}.txt".format(datetime.now().strftime("%Y%m%d")), "a") as f:
		f.write("{}	{}	{}	{}\n".format(datetime.now(), ip, username, message))


if __name__ == "__main__":
	while True:
		# get_proxies()

		# main()
		proxymesh_api() # request imgur.com API using proxymesh
		checkedproxy_api()
		gatherproxy_api()

		print("Sleeping for 5mins...")
		time.sleep(300)