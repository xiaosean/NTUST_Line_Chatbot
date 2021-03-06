import urllib.request

from pyquery import PyQuery as pq

class ToeicVocab():
	"""get Toeic vocabulary from Language center department of NTUST
 	
 	Parameters
    ----------
    link : str
        URL link for this week's toeic vocabulary.
	"""
	def __init__(self):
		self.link = ""
		
	def get_image_href(self):
		"""get Toeic vocabulary image's link from Language center department of NTUST
	 	
	 	Returns
	    ----------
	    link : str
	        URL link for this week's toeic vocabulary.
		"""
		web=pq(url="http://fls.ntust.edu.tw/files/11-1094-5131.php?Lang=zh-tw")
		
		for col in web(".col_02").find(".col_02").find(".mm_01").find(".mc"):
			href=web(col).find(".ptname").find("a").attr("href")
			redirect_web= pq(url=href)
			download_href = redirect_web(".col_02").find(".col_middle").find("#Dyn_2_2").find(".mm_01").find("img").attr("src")
			if download_href[:4] != "http":
				download_href = "http://fls.ntust.edu.tw"+redirect_web(".col_02").find(".col_middle").find("#Dyn_2_2").find(".mm_01").find("img").attr("src")			
			print("download_href =", download_href)
			# i only get the newest
			self.link = download_href
			return download_href
		raise ValueError('Sorry can not connect to server')

	def download(self):
		""" Download this week's toeic vocabulary. save a png file"""
		download_href=self.get_image_href()
		title="vocab.png"
		try:
		    # 注意檔名還是不可取?/\之類的奇怪保留字
		    urllib.request.urlretrieve(download_href,title)  
		    # urllib.request.urlretrieve(網址,要取的名子)        
		    print("successful:"+title)
		except Exception:
		    print("failed:"+title)
		else:
		    print("good")


