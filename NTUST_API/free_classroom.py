import time

from pyquery import PyQuery as pq
import pandas as pd
import requests

class FreeClassroom():
	"""get Free classroom from NTUST website
 	
 	Parameters
    ----------
    QUERY_URL : str
        URL link for getting all classroom's status.
	POST_DATA : dict
		data for pass CSRF (Cross Site Request Forgery).
	period_dict : dict
		mapping current hours to period.

	See also
	--------
	CSRF absract: https://blog.davidh83110.com/%E8%B3%87%E8%A8%8A%E5%AE%89%E5%85%A8/%E9%A7%AD%E5%AE%A2%E6%8A%80%E8%A1%93/owasp%20top10/2016/09/09/csrf.html

	"""
	def __init__(self):
		self.QUERY_URL = "http://stuinfo.ntust.edu.tw/classroom_user/classroom_usecondition.aspx"
		self.POST_DATA = {
		    "__EVENTTARGET": "classlist_ddl",
		    "__EVENTARGUMENT": "",
		    "__VIEWSTATE": "dDw1NTk0MzU4NjE7dDw7bDxpPDE+Oz47bDx0PDtsPGk8Mz47aTw0Pjs+O2w8dDxAMDw7Ozs7Ozs7Ozs7Pjs7Pjt0PDtsPGk8NT47PjtsPHQ8QDA8cDxwPGw8U0Q7PjtsPGw8U3lzdGVtLkRhdGVUaW1lLCBtc2NvcmxpYiwgVmVyc2lvbj0xLjAuNTAwMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODk8MjAxOC0wNC0yND47Pjs+Pjs+Ozs7Ozs7Ozs7Oz47Oz47Pj47Pj47Pj47PmUcY2TfSubkXSYlZ7kORruwsd/3",
		    "__VIEWSTATEGENERATOR": "D2C5BC33",
		    "classlist_ddl": "TR"
		}
		self.period_dict ={
		    "8":"第一節",
		    "9":"第二節",
		    "10":"第三節",
		    "11":"第四節",
		    "12":"第五節",
		    "13":"第六節",
		    "14":"第七節",
		    "15":"第八節",
		    "16":"第九節",
		    "17":"第十節",
		    "18":"第十一節",
		    "19":"第十二節",
		    "20":"第十三節",
		    "21":"第十四節"
		}

	def get_classroom_table(self):
		"""get classroom from NTUST website
	 	
	 	Returns
	    ----------
		df : pandas DataFrame
			the classroom status table
		"""
		page = requests.post(self.QUERY_URL, data=self.POST_DATA)
		pq_page = pq(page.text)
		if pq_page('table').eq(0):
			data = [[pq(child).text() for child in pq(tr).children()] for tr in pq_page('table').eq(0).find("tr") if(len(pq(tr).text()))]
		else:
			raise ValueError('Sorry can not connect to server')
		df = pd.DataFrame(data=data[1:-1], columns=data[0])
		return df

	def get_free_classroom(self):
		"""get Free classroom from NTUST website
	 	
	 	Returns
	    ----------
		info : str
			free classrooms
		"""
		df = self.get_classroom_table()
		t = time.gmtime(time.time())
		hour = (t.tm_hour + 8)%24
		priod = self.period_dict.get(str(hour), "")
		if priod:
		    return df[df[priod]==""]["教室"].values
		return None