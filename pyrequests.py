import json, os, pprint, random, re, requests, time, threading, uuid
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
# from lxml import etree
from signal import *


lock = threading.Lock()


def auto_dial():
	return True
	make_dial = True
	while make_dial:
		print("Changing IP.....")
		os.system("Rasdial haha /d")
		redial = os.system("Rasdial haha 059597093234 343937")

		if redial == 0:
			make_dial = False
		else:
			time.sleep(5)


def change_ua(ua):
	if len(ua):
		user_agent = ua.pop(0)
	else:
		user_agents = load_user_agents()
		user_agent = user_agents.pop(0)
	
	headers['User-Agent'] = user_agent


def load_user_agents():
	with open("data/user_agents.txt", "r") as f:
		return [k for i, k in json.loads(f.read()).items()]


def request_post(name, s, d, h):
	auto_dial()
	try:
		headers['User-Agent']		= h
		headers['Referer'] 			= 'https://imgur.com/'
		headers['Host']				= 'imgur.com'
		headers['Origin']			= 'https://imgur.com'
		headers['Accept-Language']	= 'en-US,en;q=0.8'
		

		upload_captcha_url = "https://imgur.com/upload/checkcaptcha"
		data = {
			'total_uploads': 1,
			'create_album': 'true'
		}
		upload_captcha_html = s.post(upload_captcha_url, data=data, headers=headers)
		if 'new_album_id' not in upload_captcha_html.json()['data']:
			print("UPLOAD CAPTCHA RESPONSE: {} - H: {}".format(upload_captcha_html.json(), upload_captcha_html.request.headers['User-Agent']))
			change_ua(user_agents)
			return True

		upload_captcha_response = json.loads(upload_captcha_html.text)

		post_url = "https://imgur.com/upload"
		png_file = open("{}/{}".format(image_dir, 'image00.jpg'), 'rb')
		
		files = {
			'Filedata': ('image00.jpg', png_file, 'image/jpg'),
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
		headers['Referer'] = 'http://imgur.com/{}'.format(post_html_response['data']['album'])
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


def request_login(data):
	auto_dial()

	print("Change IP done.")
	url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
	s = requests.session()
	response = s.post(url, data=data, headers=headers)
	html = BeautifulSoup(response.content, "html.parser")
	
	if html.find("li", {"class": "account"}):
		print("login for {} is successful.".format(data['username']))
		return s
	elif html.find("div", {"class", "captcha"}):
		print("Captcha encountered for {} login. Current UA: {}".format(data['username'], response.request.headers['User-agent']))
		change_ua(user_agents)
		return None
	else:
		print("Error encountered for {} login {}".format(data['username'], response.json()))
		return None

	s.cookies.clear()
	s.close()


def savecontent(links):
	if links:
		with open("{}/{}".format(data_dir, "saveContent.txt"), "a", encoding="utf-8") as f:
			for link in links:
				f.write("{}\n".format(link))

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
		headers['referer'] =  ''

		print("Checking if account {} is active.".format(account[0]))
		s = request_login(data)

		if type(s).__name__ is "Session":
			if "{}----{}".format(account[0], account[1]) not in active_accounts:
				active_accounts.append("{}----{}".format(account[0], account[1]))
		else:
			inactive_accounts.append("{}----{}".format(account[0], account[1]))
	except Exception as ex:
		print(ex)


def check_accounts():
	global active_accounts, inactive_accounts

	accounts = []
	with open("{}/{}".format(data_dir, "账号.txt"), "r", encoding='utf-8') as f:
		accounts = [tuple(account.rstrip().split("----")) for account in f]
	print("{} accounts loaded for checking".format(len(accounts)))

	active_accounts = []
	inactive_accounts = []
	
	threads_num = 2

	temp_accs = accounts
	while temp_accs:
		# login
		threads = []
		for i in range(threads_num):
			if temp_accs:
				acc = temp_accs.pop(0)
				if "{}----{}".format(acc[0], acc[1]) not in active_accounts:
					t = threading.Thread(target = validate_accounts, args = ("Thread-{}".format(i), acc))
					threads.append(t)
					t.start()

			for t in threads:
				t.join()

	print("ACTIVE: {}".format(active_accounts))
	with open("{}/{}".format(data_dir, "账号active.txt"), "a", encoding="utf8") as f:
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
	print("{} accounts loaded to process upload.".format(len(active_accounts)))
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
			if active_accounts:
				account = active_accounts[counter]

				# login
				data = {
					'username': account[0], 
					'password': account[1]
				}
				headers['Referer'] = ''

				if account[0] not in rep['upload_summary']:
					rep['upload_summary'][account[0]] = {
						'links': [],
						'total_post': 0
					}

				print("logging in: {}".format(account[0]))
				s = request_login(data)

				if type(s).__name__ is "Session":
					threads = []
					for i in range(threads_num):
						d = {
							'username': account[0]
						}

						if len(user_agents) == 0:
							user_agents = load_user_agents()

						t = threading.Thread(target = request_post, args = ("Thread-{}".format(i), s, d, user_agents.pop(0)))
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
					print("You are uploading so fast.")
					break
				counter = 0
	except KeyboardInterrupt:
		savecontent(links)
		print(rep)
	except Exception as ex:
		savecontent(links)
		print(rep)
		print("error {} ({})".format(type(ex).__name__, datetime.now() - start))

if __name__ == "__main__":
	global data_dir, image_dir, user_agents, headers
	data_dir = "data"
	image_dir = "images"
	user_agents = load_user_agents()
	headers = {}
	change_ua(user_agents)

	while True:
		check_accounts()
		main()

		print("Sleeping for 1hr...")
		time.sleep(3600)