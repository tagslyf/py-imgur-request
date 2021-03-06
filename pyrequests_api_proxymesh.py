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


def proxymesh_api():
	global contents, domain, image_urls, titles, req_limit, start, promos
	pid = str(uuid.uuid4()).upper().replace("-", "")[:16]
	domain = "http://imgur.com/"
	print("Start API request using proxmesh proxy. ({})".format(datetime.now()))
	write_upload_log("Start", pid, "Start API request using proxmesh proxy.")
	titles = []
	with open("data/titles.txt", "r") as f:
		titles = [key.rstrip() for key in f.readlines()]
	promos = []
	with open("data/promos.txt", "r") as f:
		promos = [key.rstrip() for key in f.readlines()]
	contents = []
	with open("data/contents.txt", "r") as f:
		contents = [key.rstrip() for key in f.readlines()]
	# Upload images here http://freeimagehosting.net/, 
	# image_urls = ['http://i.imgur.com/4BoBLeK.jpg', 'https://i.imgbox.com/5eveR18P.jpg', 'http://i64.tinypic.com/n5mudx.jpg', 'http://thumbsnap.com/i/WOv9HaHv.jpg?0116']
	image_urls = ["http://i.imgur.com/nRTNo6y.png", "http://oi64.tinypic.com/jtvuxf.jpg", "http://thumbsnap.com/i/e5bvtDl8.png?0118"]
	req_limit = 100
	start = datetime.now()
	threads_num = 2	
	# Call proxymesh api to get the proxy list
	url = "https://proxymesh.com/api/proxies/"
	username = "winner88"
	password = "qweasd321"
	response = requests.get(url, auth=requests.auth.HTTPBasicAuth(username, password))

	if response.status_code == 200:
		url = "https://api.imgur.com/3/image"
		headers = {}
		headers['Authorization'] = "Client-ID e8e0297762a5593"
		proxymesh_proxies = response.json()['proxies']
		for proxymesh_proxy in proxymesh_proxies:
			proxys = {
				'http': 'http://winner88:qweasd321@{}'.format(proxymesh_proxy),
				'https': 'http://winner88:qweasd321@{}'.format(proxymesh_proxy)
			}
			proxymesh_ips = []
			for n in range(1, 176):
				try:
					response = requests.get('http://httpbin.org/ip', proxies=proxys, timeout=5)
				except Exception as ex:
					pass
				else:
					if 'X-ProxyMesh-IP' in response.headers:
						if response.headers['X-ProxyMesh-IP'] not in proxymesh_ips:
							proxymesh_ips.append(response.headers['X-ProxyMesh-IP'])
				sys.stdout.write("\rCount of IP(s) for {}: {}".format(proxymesh_proxy, len(proxymesh_ips)))
				sys.stdout.flush()
			proxy_counter = 0
			print("\n{} {} proxymesh IPs gathered.".format(proxymesh_proxy, len(proxymesh_ips)))
			write_upload_log(proxymesh_ips, 'API', '{} Proxymesh current IP address given.'.format(len(proxymesh_ips)))
			while True:
				threads = []
				for i in range(threads_num):
					proxymesh_ip = proxymesh_ips[proxy_counter]
					t = threading.Thread(target = request_api, args = ("ProxyMeshThread-{}".format(i), url, headers, proxys, proxymesh_ip, False))
					threads.append(t)
					t.start()
					proxy_counter += 1
					if proxy_counter >= len(proxymesh_ips):
						break
				for t in threads:
					t.join()
				if proxy_counter >= len(proxymesh_ips):
					break
		write_upload_log("Stop", pid, "Proccessing for proxymesh proxies' is stop. Links total count is {}".format(len(links)))
	else:
		write_upload_log("None", "None", "Error on getting proxies in {}".format(url))
		write_upload_log("Stop", pid, "Proccessing for proxymesh proxies' is stop. Links total count is {}".format(len(links)))


def write_upload_log(ip, username, message):
	with open("data/pyrequests_api/proxymesh_uploadlog_{}.txt".format(datetime.now().strftime("%Y%m%d")), "a") as f:
		f.write("{}	{}	{}	{}\n".format(datetime.now(), ip, username, message))


if __name__ == "__main__":
	global links
	links = []
	while True:
		proxymesh_api()
		print("Sleeping for 5mins...")
		time.sleep(300)