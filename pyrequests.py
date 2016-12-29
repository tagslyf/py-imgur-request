import json, os, pprint, random, re, requests, time, threading, uuid
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
# from lxml import etree
from signal import *


lock = threading.Lock()


def auto_dial():
	make_dial = True
	while make_dial:
		print("Changing IP.....")
		os.system("Rasdial haha /d")
		redial = os.system("Rasdial haha 059597093234 343937")

		if redial == 0:
			make_dial = False
		else:
			time.sleep(5)


def request_post(name, s, d):
	try:
		auto_dial()

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
		upload_captcha_html = s.post(upload_captcha_url, data=data, headers=headers)

		upload_captcha_response = json.loads(upload_captcha_html.text)

		post_url = "https://imgur.com/upload"
		png_file = open("{}/{}".format(image_dir, 'images.jpg'), 'rb')
		
		files = {
			'Filedata': ('thumbnail00.png', png_file, 'image/jpg'),
			'new_album_id': (None, upload_captcha_response['data']['new_album_id'])	
		}
		post_html = s.post(post_url, files=files, headers=headers)

		post_html_response = json.loads(post_html.text)

		desc_link = "\n".join(links[-3:])
		links.append("http://imgur.com/{}".format(post_html_response['data']['hash']))
		rep['upload_summary'][d['username'].strip()]['links'].append("http://imgur.com/{}".format(post_html_response['data']['hash']))
		rep['upload_summary'][d['username'].strip()]['total_post'] += 1
		print("{}. {} http://imgur.com/{} ({})".format(len(links), d['username'], post_html_response['data']['hash'], datetime.now() - start))

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
		print("{} error {}:{!r} ({})".format(d['username'], type(ex).__name__, ex.args, datetime.now() - start))
	except Exception as ex:
		print("{} error {} ({})".format(d['username'], type(ex).__name__, datetime.now() - start))
		pass


def request_login(data, headers):
	auto_dial()

	url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
	s = requests.session()
	response = s.post(url, data=data, headers=headers)
	html = BeautifulSoup(response.content)
	if html.find("li", {"class": "account"}):
		return s
	else:
		print("Captcha encountered" if html.find("div", {"class", "captcha"}) else "")
		return None

	s.cookies.clear()
	s.close()


def savecontent(links):
	if links:
		with open("{}/{}".format(data_dir, "saveContent.txt"), "r", encoding="utf-8") as f:
			link_contents = [cons for cons in f] + links
			f.close()

		with open("{}/{}".format(data_dir, "saveContent.txt"), "w", encoding="utf-8") as f:
			for link in link_contents:
				f.write("{}\n".format(link))
			f.close()

	if rep:
		with open("{}/{}".format(data_dir,"reports.txt"), "w", encoding="utf-8") as f:
			if rep["upload_summary"]:
				pprint.pprint(rep, f)

def validate_accounts(name, account):
	try:
		data = {
			'username': account[0], 
			'password': account[1]
		}
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
			'referer': ''
		}

		s = request_login(data, headers)

		if type(s).__name__ is "Session":
			if "{}----{}".format(account[0], account[1]) not in active_accounts:
				active_accounts.append("{}----{}".format(account[0], account[1]))
		else:
			inactive_accounts.append("{}----{}".format(account[0], account[1]))
	except Exception as ex:
		print(ex)


def check_accounts(accs):
	global active_accounts, inactive_accounts

	active_accounts = []
	inactive_accounts = []
	
	threads_num = 2
	print("Verifying accounts {}".format(accs))
	temp_accs = accs
	while temp_accs:
		# login
		threads = []
		for i in range(threads_num):
			if temp_accs:
				acc = temp_accs.pop()
				print(acc)
				if "{}----{}".format(acc[0], acc[1]) not in active_accounts:
					t = threading.Thread(target = validate_accounts, args = ("Thread-{}".format(i), acc))
					threads.append(t)
					t.start()

			for t in threads:
				t.join()

	print("ACTIVE: {}".format(active_accounts))
	# with open("{}/{}".format(data_dir, "账号active.txt"), "w", encoding="utf8") as f:
	with open("{}/{}".format(data_dir, "账号active.txt"), "r", encoding="utf8") as f:
		accounts = [account.rstrip() for account in f] + active_accounts
		f.close()

	with open("{}/{}".format(data_dir, "账号active.txt"), "w", encoding="utf8") as f:
		f.write("\n".join(accounts))
		f.close()

	with open("{}/{}".format(data_dir, "账号.txt"), "w", encoding="utf-8") as f:
		for a in inactive_accounts:
			f.write("{}\n".format(a))
		f.close()


def main():
	global active_accounts, keywords, links, start, rep

	active_accounts = []
	with open("{}/{}".format(data_dir, "账号active.txt"), "r", encoding="utf-8") as f:
		active_accounts = [tuple(acc.rstrip().split("----")) for acc in f]
	domain = "http://www.imgur.com"
	counter = 0
	keywords = []
	with open("{}/{}".format(data_dir, "keywords.txt"), "r", encoding="utf-8") as f:
		keywords = [key.rstrip() for key in f]
	links = []
	rep = {}
	rep['upload_summary'] = {}
	start = datetime.now()
	start_time = time.time()
	threads_num = 40

	print("Requesting {} ({})".format(domain, start))
	try:
		while True:
			account = active_accounts[counter]

			# login
			data = {
				'username': account[0], 
				'password': account[1]
			}
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
				'referer': ''
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
						'username': account[0]
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
		print("error {} ({})".format(type(ex).__name__, datetime.now() - start))


if __name__ == "__main__":
	global accounts, data_dir, image_dir
	data_dir = "data"
	image_dir = "images"

	accounts = []
	with open("{}/{}".format(data_dir, "账号.txt"), "r", encoding='utf-8') as f:
		accounts = [tuple(account.rstrip().split("----")) for account in f]
	print("{} accounts loaded".format(len(accounts)))

	while True:
		check_accounts(accounts)
		main()

		print("Sleeping for 1hr...")
		time.sleep(3600)