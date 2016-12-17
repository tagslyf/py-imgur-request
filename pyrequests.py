import json, uuid
import requests
from lxml import etree

def main():
	url = "http://www.imgur.com"

	s = requests.session()

	# login https://imgur.com/signin?redirect=http%3A%2F%2Fimgur.com%2F
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
	tree = etree.HTML(html.content)

	for a in tree.xpath("//div[@class='dropdown-footer']/a"):
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

	post_url = "https://imgur.com/upload"
	png_file = open('thumbnail00.png', 'rb')
	
	files = {
		'Filedata': ('thumbnail00.png', png_file, 'image/png'),
		'new_album_id': (None, upload_captcha_response['data']['new_album_id'])		
	}

	post_html = s.post(post_url, files=files, headers=headers)

	post_html_response = json.loads(post_html.text)

	# Update image title and description
	update_url = "http://imgur.com/ajax/titledesc/{}".format(post_html_response['data']['deletehash'])
	headers = {
		'User-agent': 'Mozilla/5.0', 
		'referer': 'http://imgur.com/{}'.format(post_html_response['data']['album'])
	}
	data = {
		'title': str(uuid.uuid4()),
		'description': "{} \n http://imgur.com/{}".format(str(uuid.uuid4()), post_html_response['data']['hash'])
	}
	update_html = s.post(update_url, data=data, headers=headers)
	
	# logout
	logout_html = s.post(logout_url, headers = headers)
	headers = {
		'User-agent': 'Mozilla/5.0', 
		'referer': ''
	}

	s.cookies.clear()
	s.close()

if __name__ == "__main__":

	main()