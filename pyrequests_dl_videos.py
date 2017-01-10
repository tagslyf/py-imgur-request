import requests
from datetime import datetime

def download_video():
	# url = "https://redirector.googlevideo.com/videoplayback?expire=1484045177&gir=yes&dur=3123.176&ei=GWd0WITsIM2jYJeYp9AJ&clen=204076649&source=youtube&sparams=clen,dur,ei,gir,id,ip,ipbits,itag,lmt,mime,mm,mn,ms,mv,pl,ratebypass,source,upn,expire&itag=18&lmt=1483668317870478&key=yt6&ratebypass=yes&upn=Al3qTQdeRKU&signature=AAC6C3F6A61B8C87FA066BC59A3FB16A34EA875F.3830FB88810E5B7A185092A70F905ABDFD6AB15F&ip=158.255.5.218&ms=au&mv=u&mt=1484023497&pl=24&mime=video/mp4&id=o-AE7_ieAUS9EEg3ltgBqfO8wWznx2gC8Ek5nWFy4toGNl&mn=sn-gxuo03g-ig3e&mm=31&ipbits=0&signature=&title=/JavSex.net"
	url = "https://video-http.media-imdb.com/MV5BYjhkODYyZjMtZTI4Zi00MTUxLTk5MzYtN2YzMDU1ODVhOWU3XkExMV5BbXA0XkFpbWRiLWV0cy10cmFuc2NvZGU@.mp4?Expires=1484113340&Signature=zUt1wKy8aLdrrWMp06Z48kR9eb2g3ORx~fc54oMW67VNsYqOpBbkVIcQqQu~Yt~Rq8gWQZgT1AUL2P4Pte9liCt9mWRG-siWQyQUP7ONuEpoS6OtHuuSsyex739tRkp6GfrJGDQcUxF2kiLXDey2Zp2bCpwypjwiF46of80q8G4_&Key-Pair-Id=APKAILW5I44IHKUN2DYA"
	# url_id = "o-AE7_ieAUS9EEg3ltgBqfO8wWznx2gC8Ek5nWFy4toGNl"
	url_id = "APKAILW5I44IHKUN2DYA"

	response = requests.get(url)
	print("connected... {}".format(datetime.now() - start))
	filename = "{}.mp4".format(url_id)

	f = open(filename, "wb")
	print("Downloading...")

	for chunk in response.iter_content(chunk_size=255): 
	 	if chunk:
	 		f.write(chunk)

	print("Done...")
	f.close()

if __name__ == "__main__":
	start = datetime.now()
	print("Start: {}".format(start))
	download_video()
	print("Stop: {} {}".format(datetime.now(), datetime.now() - start))