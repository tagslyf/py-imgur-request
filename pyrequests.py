import json, os, random, requests, uuid
from lxml import etree

def main():
	keywords = []
	links = []
	if os.path.isfile("keywords.txt"):
		with open("keywords.txt", "r") as file_open:
			keywords = [key.rstrip() for key in file_open]
	url = "http://www.imgur.com"
	print("Requesting {}".format(url))

	s = requests.session()

	# login
	login_url = "https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F"
	logout_url = ""
	login_data = {
		'username': 'mmkronald', 
		'password': '123qwe!!'
	}
	headers = {
		'User-agent': 'Mozilla/5.0', 
		'referer': ''
	}
	html = s.post(login_url, login_data, headers = headers)
	print("LOGIN", html, type(html), login_data)
	tree = etree.HTML(html.content)
	print(tree.xpath("//div[@class='dropdown-footer']"), "Captcha", tree.xpath("//div[@class='captcha']"))
	for a in tree.xpath("//div[@class='dropdown-footer']/a"):
		print(a, a.text, "https:{}".format(a.xpath('@href')[0]))
		if a.text == "logout":
			logout_url = "https:{}".format(a.xpath('@href')[0])

	# upload URL http://imgur.com/upload; need to send request first in captcha URL https://imgur.com/upload/checkcaptcha
	headers = {
		'User-Agent': 'Mozilla/5.0', 
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
	upload_captcha_html = s.post(upload_captcha_url, headers=headers, data=data)
	upload_captcha_response = json.loads(upload_captcha_html.text)
	print("UPLOAD CAPTCHA", upload_captcha_html, upload_captcha_response)
	# print("UPLOAD CAPTCHA", upload_captcha_html, upload_captcha_response, upload_captcha_response['data']['new_album_id'])

	post_url = "https://imgur.com/upload"
	png_file = open('thumbnail00.png', 'rb')
	
	files = {
		'Filedata': ('thumbnail00.png', png_file, 'image/png'),
		'new_album_id': (None, upload_captcha_response['data']['new_album_id'])		
	}

	post_html = s.post(post_url, files=files, headers=headers)
	
	# print("POST UPLOAD", post_html, post_html.headers['Content-Type'], "|||", post_html.request.headers['Content-Type'])
	# print(post_html.text, type(post_html.text), "DELETEHASH: {}".format(json.loads(post_html.text)['data']['deletehash']))

	post_html_response = json.loads(post_html.text)
	print("POST UPLOAD", post_html, post_html_response)

	# Update image title and description
	update_url = "http://imgur.com/ajax/titledesc/{}".format(post_html_response['data']['deletehash'])
	headers = {
		'User-agent': 'Mozilla/5.0', 
		'referer': 'http://imgur.com/{}'.format(post_html_response['data']['album'])
	}
	keyword = keywords[random.randint(0, len(keywords) - 1)]
	link = ""
	try:
		link = links[random.randint(0, len(links) - 1)]
	except :
		pass
	data = {
		'title': keyword,
		'description': "{}&nbsp;&nbsp;{}\n\n{}".format(keyword, '大奖老虎机 http://www.Q82019309.com', link)
	}
	print("UPDATE URL: {}".format(update_url))
	print("UPDATE HEADERS: {}".format(headers))
	print("UPDATE DATA: {}".format(data))
	update_html = s.post(update_url, data=data, headers=headers)
	print("UPDATE IMAGE TITLE/DESCRIPTION", update_html)
	
	# logout
	logout_html = s.post(logout_url, headers = headers)
	headers = {
		'User-agent': 'Mozilla/5.0', 
		'referer': ''
	}
	print("LOGOUT", logout_html)

	s.cookies.clear()
	s.close()
	links.append("http://imgur.com/{}".format(post_html_response['data']['hash']))
	print("http://imgur.com/{}".format(post_html_response['data']['hash']))

if __name__ == "__main__":
	main()