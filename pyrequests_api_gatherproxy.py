import json, os, random, requests, sys, threading, time, uuid
from base64 import b64encode
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from lxml import etree
from os import listdir
from os.path import isfile

lock = threading.Lock()


def request_api(name, url, headers, proxys, proxymesh_ip, limit_errors=False):
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

	errors = {}
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
				print("{}. {}".format(len(links), link)) # temporary for testing of proxymesh
				write_upload_log(proxymesh_ip, 'API:{}'.format(name), link)
			elif response.status_code == 400 and "You are uploading too fast" in response.json()['data']['error']:
				write_upload_log(proxymesh_ip, 'API', "{} {}".format(response, response.json()['data']['error']))
				break
			elif "Imgur is temporarily over capacity" in response.json()['data']['error']:
				write_upload_log(proxymesh_ip, 'API', "{} {}".format(response, response.json()['data']['error']))
				break
			else:
				write_upload_log(proxymesh_ip, 'API', "Error response: {} {}".format(response, response.json()['data']['error']) if response.json() else response.text)
		except Exception as ex:
			type, value, traceback = sys.exc_info()
			if limit_errors:
				if type.__name__ not in errors:
					for element, index in enumerate(errors):
						errors[index] = 0
					errors[type.__name__] = 1
				else:
					if errors[type.__name__] >= 25:
						write_upload_log(proxymesh_ip, 'API', "Error encountered 25 times: {}@{} line#{} {}".format(type.__name__, name, traceback.tb_lineno, value))
						break
					else:
						errors[type.__name__] += 1
			write_upload_log(proxymesh_ip, 'API', "REQUESTS ERROR: {}({}@{} line#{}) - {}".format(type.__name__, name, i + 1, traceback.tb_lineno, value))
			if type.__name__ in ['SSLError', 'ProxyError']:
				break


def checkproxy(name, gather_proxy, counter):	
	url = 'http://httpbin.org/ip'
	proxies = {
		'http': 'http:{}'.format(gather_proxy),
		'https': 'http:{}'.format(gather_proxy),
	}
	try:
		rsp = requests.get(url, proxies=proxies, timeout=3)
	except Exception as e:
		pass
	else:
		if gather_proxy not in ok2get_proxy:
			ok2get_proxy.append(gather_proxy)
	sys.stdout.write("\rChecking working proxies: {}/{}".format(gather_proxies.index(gather_proxy), len(gather_proxies)))
	sys.stdout.flush()
	lock.acquire()
	lock.release()


def check_gatherproxy():
	global gather_proxies, DATA_DIR, ok2get_proxy
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
	print("\nLoaded proxy... Total: {} OK: {} BAD: {} (Process timed {})".format(len(gather_proxies), len(ok2get_proxy), len(gather_proxies) - len(ok2get_proxy), datetime.now() - start))
	if len(ok2get_proxy) > 0:
		with open("{}{}".format(DATA_DIR, "gatherok_proxies.txt"), "w") as f:
			for proxy in ok2get_proxy:
				f.write("{}\n".format(proxy))


def gatherproxy_api():
	global contents, domain, image_urls, promos, req_limit, start, titles
	pid = str(uuid.uuid4()).upper().replace("-", "")[:16]
	domain = "http://imgur.com/"
	print("Start API request using gather proxies. ({})".format(datetime.now()))
	write_upload_log("Start", pid, "Start API request using gather proxies.")
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
	proxyloop = False
	req_limit = 100
	start = datetime.now()
	start_time = time.time()
	threads_num = 2
	url = "https://api.imgur.com/3/image"
	headers = {}
	headers['Authorization'] = "Client-ID e8e0297762a5593"
	print("{} gatherproxy's proxies loaded".format(len(checked_proxies)))
	write_upload_log(checked_proxies, 'API', 'Gathered proxies current IP address.')
	while True:
		threads = []
		for i in range(threads_num):
			proxy_ip = checked_proxies[proxy_counter]
			proxys = {
				'http': 'http://{}'.format(proxy_ip),
				'https': 'https://{}'.format(proxy_ip)
			}
			t = threading.Thread(target = request_api, args = ("GatherProxyThread-{}".format(i), url, headers, proxys, proxy_ip, True))
			threads.append(t)
			t.start()
			proxy_counter += 1
			if proxy_counter >= len(checked_proxies):
				proxyloop = True
				break
		for t in threads:
			t.join()
		if proxyloop:
			break
	write_upload_log("Stop", pid, "Proccessing for gather proxies' is stop. Links total count is {}".format(len(links)))


def write_upload_log(ip, username, message):
	with open("data/pyrequests_api/gatherproxy_uploadlog_{}.txt".format(datetime.now().strftime("%Y%m%d")), "a") as f:
		f.write("{}	{}	{}	{}\n".format(datetime.now(), ip, username, message))


if __name__ == "__main__":
	global links
	links = []
	while True:
		gatherproxy_api()