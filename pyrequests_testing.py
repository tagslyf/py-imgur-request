import json, os, random, requests, sys
from bs4 import BeautifulSoup
from datetime import datetime

def do_request():
	global accounts
	proxymesh = [
		{
			'username': "winner88",
			'password': "qweasd321",
			'proxy_host': "fr.proxymesh.com:31280"
		}
	]

	accounts = []
	with open("data/账号active.txt", "r") as f:
		for account in f.readlines():
			accounts.append(tuple(account.strip().split("----")))

	account = ("mmktest05", "123qwe!!")
	# account = ("qq1074513369", "123qwe")

	for acc in proxymesh:
		proxies = {
			'http': 'http://{}:{}@{}'.format(acc['username'], acc['password'], acc['proxy_host']), 
			'https': 'http://{}:{}@{}'.format(acc['username'], acc['password'], acc['proxy_host']), 
		}

		for account in accounts:
			request_post('test only', account, proxies)


def request_post(name, account, proxies):
	IMAGE_DIR = "images/"
	links = []
	keywords = []
	with open("data/keywords.txt", "r") as f:
		keywords = [key.rstrip() for key in f.readlines()]
	start = datetime.now()

	s = requests.session()

	url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
	data = {
		'username': account[0],
		'password': account[1]
	}
	headers = {}
	headers['X-ProxyMesh-IP'] = ""
	headers['User-Agent'] 	= "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
	headers['Referer'] 		= ""
	try:
		
		response 	= s.post(url, data=data, headers=headers, proxies=proxies, timeout=5)
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
	else:
		if 'X-ProxyMesh-IP' in response.headers:
			xproxymesh_ip = response.headers['X-ProxyMesh-IP']
			print(response.headers['X-ProxyMesh-IP'])

	headers['X-ProxyMesh-IP'] = xproxymesh_ip

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
		response = s.post(url, data=data, headers=headers, proxies=proxies, timeout=5)
		captcha_response_json = json.loads(response.text)
		if 'new_album_id' not in captcha_response_json['data']:
			return None
	except Exception as ex:
		return None
	else:
		if 'X-ProxyMesh-IP' in response.headers:
			print(response.headers['X-ProxyMesh-IP'])

	images = [f for f in os.listdir(IMAGE_DIR) if os.path.isfile("{}{}".format(IMAGE_DIR, f))]

	for i in range(100):
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
			response = s.post(url, files=files, headers=headers, proxies=proxies, timeout=5)
			response_json = json.loads(response.text)			
		except Exception as ex:
			continue
		else:
			if 'X-ProxyMesh-IP' in response.headers:
				print(response.headers['X-ProxyMesh-IP'])

		# Update image title and description start
		url = "http://imgur.com/ajax/titledesc/{}".format(response_json['data']['deletehash'])
		headers['Referer'] = "http://imgur.com/{}".format(response_json['data']['album'])
		keyword = keywords[random.randint(0, len(keywords) - 1)]
		desc = "{}&nbsp;&nbsp;{}\n\n{}"
		desc_link = "\n".join(["{}----{}".format(keywords[random.randint(0, len(keywords) - 1)], l) for l in links[-3:]])
		desc_website = "大奖老虎机 http://www.Q82019309.com"
		update_data = {
			'title': keyword,
			'description': desc.format(keyword, desc_website.replace('.', '&#46;'), desc_link.replace('.', '&#46;'))
		}
		try:
			update_html = s.post(url, headers=headers, data=update_data, proxies=proxies, timeout=5)
		except Exception as ex:
			continue
		else:
			if 'X-ProxyMesh-IP' in response.headers:
				print(response.headers['X-ProxyMesh-IP'])

		links.append("http://imgur.com/{}".format(response_json['data']['hash']))
		print("{}. http://imgur.com/{} ({} {} {})".format(len(links), response_json['data']['hash'], datetime.now() - start, name, account[0]))
		# with open("data/pyrequests_x3/saveContent.txt", "a", encoding="utf-8") as f:
		# 	f.write("http://imgur.com/{}\n".format(response_json['data']['hash']))
		with open("data/saveContent.txt", "a", encoding="utf-8") as f:
			f.write("http://imgur.com/{}\n".format(response_json['data']['hash']))


def check_proxymesh_ip():
	url = "http://httpbin.org/ip"
	proxies = {
		'http': 'http://winner88:qweasd321@fr.proxymesh.com:31280', 
		'https': 'http://winner88:qweasd321@fr.proxymesh.com:31280'
	}
	proxymesh_ips = []
	start = datetime.now()
	print("Getting proxymesh IPs. {}".format(start))
	for n in range(1, 501):
		response = requests.get(url, proxies=proxies)
		if 'X-ProxyMesh-IP' in response.headers:
			if response.headers['X-ProxyMesh-IP'] not in proxymesh_ips:
				proxymesh_ips.append(response.headers['X-ProxyMesh-IP'])
				print("{} NEW {}".format(n, response.headers['X-ProxyMesh-IP']))
	print("Done. {}".format(datetime.new() - start))

if __name__ == "__main__":
	check_proxymesh_ip()
	# do_request()