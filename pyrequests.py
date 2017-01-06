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


def request_post(name, account, ua):
	auto_dial()
	try:
		print("{:15s} {:15s} {}".format(account[0], "START REQUEST", ua))
		url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
		s = requests.session()
		data = {
			'username': account[0],
			'password': account[1]
		}
		headers['User-Agent']	= ua
		headers['Referer'] 		= ''
		print("{:15s} {:15s} {}".format(account[0], "POST LOGIN", headers['User-Agent']))
		response = s.post(url, data=data, headers=headers, stream=True)
		html = BeautifulSoup(response.content, "html.parser")
		
		if html.find("li", {"class": "account"}):
			print("{:15s} {:15s} {}".format(account[0], "SUCCESS LOGIN", response.request.headers['User-Agent']))
		elif html.find("div", {"class", "captcha"}):
			print("{:15s} {:15s} {}".format(account[0], "CAPTCHA LOGIN", response.request.headers['User-Agent']))
			return None
		else:
			print("{:15s} {:15s} {}".format(account[0], "ERROR LOGIN", response.request.headers['User-Agent']))
			return None
		
		headers['Referer'] 			= 'https://imgur.com/'
		headers['Host']				= 'imgur.com'
		headers['Origin']			= 'https://imgur.com'
		headers['Accept-Language']	= 'en-US,en;q=0.8'
		
		upload_captcha_url = "https://imgur.com/upload/checkcaptcha"
		data = {
			'total_uploads': 1,
			'create_album': 'true'
		}
		print("{:15s} {:15s} {}".format(account[0], "SEND CUPLOAD", headers['User-Agent']))
		upload_captcha_html = s.post(upload_captcha_url, data=data, headers=headers)
		# response format should be like this {"data":{"overLimits":0,"upload_count":false,"new_album_id":"90Rxw","deletehash":"zP3uVDBWdasKvnF"},"success":true,"status":200}
		# new_album_id and deletehash key is needed to upload image
		if 'new_album_id' not in upload_captcha_html.json()['data']:
			print("{:15s} {:15s} {}".format(account[0], "CAPTCHA UPLOAD", response.request.headers['User-Agent']))
			return None

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
		# rep['upload_summary'][account[0].strip()]['links'].append("http://imgur.com/{}".format(post_html_response['data']['hash']))
		# rep['upload_summary'][account[0].strip()]['total_post'] += 1
		print("{}. {} http://imgur.com/{} ({})".format(len(links), account[0], post_html_response['data']['hash'], datetime.now() - start))

		# Update image title and description
		update_url = "http://imgur.com/ajax/titledesc/{}".format(post_html_response['data']['deletehash'])
		headers['Referer'] = 'http://imgur.com/{}'.format(post_html_response['data']['album'])
		keyword = keywords[random.randint(0, len(keywords) - 1)]
		data = {
			'title': keyword,
			'description': "{}&nbsp;&nbsp;{}\n\n{}".format(keyword, '大奖老虎机 http://www.Q82019309.com', desc_link)
		}
		update_html = s.post(update_url, data=data, headers=headers)
		
		s.cookies.clear()
		s.close()
	except NameError as ex:
		print("{:15s} NAMEERROR {}:{!r} ({}) {}".format(account[0], type(ex).__name__, ex.args, datetime.now() - start), ua)
	except Exception as ex:
		print("{:15s} ERROR {}:{!r} ({}) {}".format(account[0], type(ex).__name__, ex.args, datetime.now() - start), ua)
		pass


def request_login(data):
	auto_dial()

	print("Change IP done.")
	url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
	
	headers['Referer'] = ''
	for i, k in user_agents.items():
		print("Request login to {}. UA: {}".format(data['username'], k))
		headers['User-Agent'] = k
		s = requests.session()
		response = s.post(url, data=data, headers=headers)
		html = BeautifulSoup(response.content, "html.parser")
		
		if html.find("li", {"class": "account"}):
			print("login for {} is successful. UA: {}".format(data['username'], response.request.headers['User-Agent']))
			return s
		elif html.find("div", {"class", "captcha"}):
			print("Captcha encountered for {} login. UA: {}".format(data['username'], response.request.headers['User-agent']))
		else:
			print("Error encountered for {} login. UA: {}".format(data['username'], response.request.headers['User-agent']))
		s.cookies.clear()
		s.close()
	return None


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
	for acc in temp_accs:
		validate_accounts('', acc)

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
		if f.read():
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

				if account[0] not in rep['upload_summary']:
					rep['upload_summary'][account[0]] = {
						'links': [],
						'total_post': 0
					}

				for i, k in user_agents.items():
					request_post(i, account, k)

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


def single_post():
	image_dir = "images"
	data_dir = "data"
	start = datetime.now()
	start_time = time.time()
	rep = {}
	with open("{}/{}".format(data_dir, "keywords.txt"), "r", encoding="utf-8") as f:
		keywords = [key.rstrip() for key in f]

		user_agents = {}
		links = []
		data_accounts = []
		with open("data/账号.txt", "r") as f:
			data_accounts = [tuple(acc.rstrip().split("----")) for acc in f.readlines()]
		with open("data/user_agents.txt", "r") as f:
			user_agents = json.loads(f.read())

		url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
		
		
		headers = {}
		headers['Referer'] 		= ''
		for key, value in user_agents.items():
			headers['User-Agent']	= value
			for account in data_accounts:
				data = {
					'username': account[0],
					'password': account[1]
				}
				
				# print("{:15s} {:15s} {}".format(account[0], "POST LOGIN", headers['User-Agent']))
				s = requests.session()
				response = s.post(url, data=data, headers=headers, stream=True)
				html = BeautifulSoup(response.content, "html.parser")
				
				if html.find("li", {"class": "account"}):
					print("{:15s} {:15s} {}".format(account[0], "SUCCESS LOGIN", response.request.headers['User-Agent']))
				elif html.find("div", {"class", "captcha"}):
					print("{:15s} {:15s} {}".format(account[0], "CAPTCHA LOGIN", response.request.headers['User-Agent']))
					s.cookies.clear()
					s.close()
					continue
				else:
					print("{:15s} {:15s} {}".format(account[0], "ERROR LOGIN", response.request.headers['User-Agent']))
					s.cookies.clear()
					s.close()
					continue
			
				headers['Referer'] 			= 'https://imgur.com/'
				headers['Host']				= 'imgur.com'
				headers['Origin']			= 'https://imgur.com'
				headers['Accept-Language']	= 'en-US,en;q=0.8'
				
				upload_captcha_url = "https://imgur.com/upload/checkcaptcha"
				data = {
					'total_uploads': 1,
					'create_album': 'true'
				}
				print("{:15s} {:15s} {}".format(account[0], "SEND CUPLOAD", headers['User-Agent']))
				upload_captcha_html = s.post(upload_captcha_url, data=data, headers=headers)
				# response format should be like this {"data":{"overLimits":0,"upload_count":false,"new_album_id":"90Rxw","deletehash":"zP3uVDBWdasKvnF"},"success":true,"status":200}
				# new_album_id and deletehash key is needed to upload image
				if 'new_album_id' not in upload_captcha_html.json()['data']:
					print("{:15s} {:15s} {}".format(account[0], "CAPTCHA UPLOAD", response.request.headers['User-Agent']))
					return None

				upload_captcha_response = json.loads(upload_captcha_html.text)

				for i in range(20):
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
					rep['upload_summary'][account[0].strip()]['links'].append("http://imgur.com/{}".format(post_html_response['data']['hash']))
					rep['upload_summary'][account[0].strip()]['total_post'] += 1
					print("{}. {} http://imgur.com/{} ({})".format(len(links), account[0], post_html_response['data']['hash'], datetime.now() - start))

					# Update image title and description
					update_url = "http://imgur.com/ajax/titledesc/{}".format(post_html_response['data']['deletehash'])
					headers['Referer'] = 'http://imgur.com/{}'.format(post_html_response['data']['album'])
					keyword = keywords[random.randint(0, len(keywords) - 1)]
					data = {
						'title': keyword,
						'description': "{}&nbsp;&nbsp;{}\n\n{}".format(keyword, '大奖老虎机 http://www.Q82019309.com', desc_link)
					}
					update_html = s.post(update_url, data=data, headers=headers)
				
				s.cookies.clear()
				s.close()	


if __name__ == "__main__":
	global data_dir, image_dir, user_agents, headers
	data_dir = "data"
	image_dir = "images"
	with open("data/user_agents.txt", "r") as f:
		user_agents =  json.loads(f.read())
	# user_agents = load_user_agents()
	headers = {}

	single_post()
	# while True:
		# check_accounts()
		# main()

		# print("Sleeping for 1hr...")
		# time.sleep(3600)