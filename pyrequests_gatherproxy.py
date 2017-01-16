import json, os, random, requests, sys, threading, time
from bs4 import BeautifulSoup
from datetime import datetime


lock = threading.Lock()


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


def gatherproxy():
	global gather_proxy, DATA_DIR, ok2get_proxy
	DATA_DIR = "data/pyrequests_gatherproxy/"
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

	with open("{}{}".format(DATA_DIR, "checked_proxy.txt"), "w") as f:
		for proxy in ok2get_proxy:
			f.write("{}\n".format(proxy))


def do_request():
	global proxy_2use, accounts, DATA_DIR, IMAGE_DIR, links, keywords, errs, descriptions

	DATA_DIR = "data/pyrequests_gatherproxy/"
	IMAGE_DIR = "images/"

	proxy_2use = []
	with open("{}{}".format(DATA_DIR, "checked_proxy.txt"), "r") as f:
		for p in f:
			proxy_2use.append(p.rstrip())

	# no checking of accounts yet if active or not
	accounts = []
	with open("data/pyrequests_gatherproxy/账号active.txt", "r") as f:
		for account in f.readlines():
			accounts.append(tuple(account.strip().split("----")))

	keywords = []
	with open("data/pyrequests_gatherproxy/keywords.txt", "r") as f:
		keywords = [key.rstrip() for key in f.readlines()]

	descriptions = []
	with open("data/descriptions.txt", "r") as f:
		descriptions = [key.rstrip() for key in f.readlines()]

	start = datetime.now()
	links = []
	errs = []

	print("Ready to start the process now... Loaded {} active accounts and {} checked proxies".format(len(accounts), len(proxy_2use)))
	for index, proxy in enumerate(proxy_2use):
		proxies = {
			'http': 'http://{}'.format(proxy),
			'https': 'https://{}'.format(proxy),
		}
		threads_num = 30
		counter = 0
		threadloop = True
		while threadloop:
			threads = []
			for i in range(threads_num):
				account = accounts[counter]
				t = threading.Thread(target = request_post, args = ("Thread-{}".format(i), counter, proxies, account))
				threads.append(t)

				t.start()
				counter += 1
				if counter >= len(accounts):
					threadloop = False
					break

			for t in threads:
				t.join()
		# print("Changing IP {}->{}... Sleep for 2mins ({})".format(proxy_2use[index], proxy_2use[index + 1], datetime.now() - start))
		print("Changing IP {}->{}...({})".format(proxy_2use[index], proxy_2use[index + 1], datetime.now() - start))
		# time.sleep(120)
	print("Sleeping for 5mins before starting the process again... ({})".format(datetime.now() - start))
	# time.sleep(600)


def request_post(name, counter, proxies, account):
	s = requests.session()
	images = [f for f in os.listdir(IMAGE_DIR) if os.path.isfile("{}{}".format(IMAGE_DIR, f))]

	url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
	data = {
		'username': account[0],
		'password': account[1]
	}
	headers = {}
	headers['User-Agent'] 	= "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
	headers['Referer'] 		= ""
	try:
		response 	= s.post(url, data=data, headers=headers, proxies=proxies, timeout=5)
		html 		= BeautifulSoup(response.content, "html.parser")
		if html.find("li", {"class": "account"}):
			# print("{}. {} {} {}".format(counter + 1, name, proxies['http'][7:], "LOGIN OK")) ## remove this after
			pass
		elif html.find("div", {"class", "captcha"}):
			return None
		else:
			return None
	except Exception as ex:
		type, value, traceback = sys.exc_info()
		if type.__name__ not in errs:
			print("ERROR: {}({} line#{}) - {}".format(type.__name__, account[0], traceback.tb_lineno, value))
		errs.append(type.__name__)
		return None

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
		type, value, traceback = sys.exc_info()
		if type.__name__ not in errs:
			print("ERROR: {}({} line#{}) - {}".format(type.__name__, account[0], traceback.tb_lineno, value))
		errs.append(type.__name__)
		return None

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
			response = s.post(url, files=files, headers=headers, proxies=proxies, timeout=15)
			response_json = json.loads(response.text)
			if 'deletehash' not in response_json['data']:
				continue
		except Exception as ex:
			type, value, traceback = sys.exc_info()
			if type.__name__ not in errs:
				print("ERROR: {}({} line#{}) - {}".format(type.__name__, account[0], traceback.tb_lineno, value))
			errs.append(type.__name__)
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
		description = description.replace("www.djyl18.com", " http://www.djyl18.com")
		update_data = {
			'title': keyword,
			'description': desc.format(keyword, desc_website.replace('.', '&#46;'), description.replace('.', '&#46;'), desc_link.replace('.', '&#46;'))
		}
		try:
			update_html = s.post(url, headers=headers, data=update_data, proxies=proxies, timeout=5)
		except Exception as ex:
			type, value, traceback = sys.exc_info()
			if type.__name__ not in errs:
				print("ERROR: {}({} line#{}) - {}".format(type.__name__, account[0], traceback.tb_lineno, value))
			errs.append(type.__name__)
			continue

		links.append("http://imgur.com/{}".format(response_json['data']['hash']))
		print("http://imgur.com/{} ({} {})".format(response_json['data']['hash'], account[0], proxies['http'][7:]))
		with open("{}{}".format(DATA_DIR,"saveContent.txt"), "a", encoding="utf-8") as f:
			f.write("http://imgur.com/{}\n".format(response_json['data']['hash']))
		with open("data/saveContent.txt", "a", encoding="utf-8") as f:
			f.write("http://imgur.com/{}\n".format(response_json['data']['hash']))


if __name__ == "__main__":
	while True:
		gatherproxy()
		do_request()