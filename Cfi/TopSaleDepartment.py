# coding=utf-8
import requests
from lxml import etree
import re
import datetime

from common import *

class TopSaleDepartmentRow(object):
	'''
	证券公司营业部交易龙虎榜数据条目

	数据形如:
	<tr><td><nobr>2017-11-16</nobr></td><td><a href="http://quote.cfi.cn/quote_000038.html" target=_blank>000038</a></td><td>深 大 通</td><td>22.660</td><td><font color=red>10.000%</font></td><td>东方证券股份有限公司北京安苑路证券营业部</td><td>0</td><td>1983.203</td><td>日涨幅偏离值达7%</td></tr>

	date : datetime类型,日期
	code : int类型,个股代码
	name : string类型,个股名称
	close : float类型,当天收盘价
	percent : float类型,当天涨跌幅(%)
	departement : string类型,发生的营业部
	buy : float类型,买入金额(万元,None表示该数据不明,原始数据为保留--)
	sell : float类型,卖出金额(万元,None表示不明,原始数据为保留--)
	comment : string类型,备注
	'''
	def __init__(self, line):
		self.original = line
		self.parseLine()

	def __str__(self):
		s = '%s %06d %s %.2f %.2f%% %s %s %s %s' % (\
			str(self.date), self.code, self.name, \
			self.close, self.percent, self.departement, \
			self.buy, self.sell, self.comment)
		return s

	def parseLine(self):
		# 格式不符合xml	
		method_tbl = [
			self.parseDate, 
			self.parseCode, 
			self.parseName, 
			self.parseClose, 
			self.parsePercent, 
			self.parseDepartement, 
			self.parseBuyAmount, 
			self.parseSellAmount, 
			self.parseComment, 
		]
		l = parseStrWithTagPair(self.original, '<td>', '</td>')
		if len(l)!=len(method_tbl):
			raise Exception("数据条目格式可能发生了改变 : %s"%self.original)
		for i in range(len(l)):
			method_tbl[i](l[i])

	def parseDate(self, s):
		'''
		<td><nobr>2017-11-16</nobr></td>
		'''
		root = etree.fromstring(s)
		node = root
		while len(node.getchildren())>0:
			node = node.getchildren()[0]
		t = node.text
		l = t.split('-')
		if len(l)!=3:
			raise Exception('日期数据格式改变 : %s'%s)
		self.date = datetime.date(int(l[0]), int(l[1]), int(l[2]))
	
	def parseCode(self, s):
		'''
		<td><a href="http://quote.cfi.cn/quote_000038.html" target=_blank>000038</a></td>
		'''
		o = re.search('\d{6}', s)
		if o==None:
			raise Exception('代码格式改变:%s'%s)
		code = s[o.start() : o.end()]
		self.code = int(code)

	def parseName(self, s):
		'''
		<td>深 大 通</td>
		'''
		root = etree.fromstring(s)
		node = root
		while len(node.getchildren())>0:
			node = node.getchildren()[0]
		t = node.text
		t = t.replace(' ', '')
		self.name = t

	def parseClose(self, s):
		'''
		<td>22.660</td>
		'''
		root = etree.fromstring(s)
		node = root
		while len(node.getchildren())>0:
			node = node.getchildren()[0]
		t = node.text
		self.close = float(t)

	def parsePercent(self, s):
		'''
		<td><font color=red>10.000%</font></td>
		'''
		o = re.search('[+-]?[\d]+\.[\d]+', s)
		if o==None:
			raise Exception('涨跌幅格式改变:%s'%s)
		percent = s[o.start() : o.end()]
		self.percent = float(percent)

	def parseDepartement(self, s):
		'''
		<td>东方证券股份有限公司北京安苑路证券营业部</td>
		'''
		root = etree.fromstring(s)
		node = root
		while len(node.getchildren())>0:
			node = node.getchildren()[0]
		t = node.text
		t = t.replace(' ', '')
		self.departement = t

	def parseBuyAmount(self, s):
		'''
		<td>0</td>
		'''
		root = etree.fromstring(s)
		node = root
		while len(node.getchildren())>0:
			node = node.getchildren()[0]
		t = node.text
		try:
			self.buy = float(t)
		except Exception,e:
			self.buy = None

	def parseSellAmount(self, s):
		'''
		<td>1983.203</td>
		'''
		root = etree.fromstring(s)
		node = root
		while len(node.getchildren())>0:
			node = node.getchildren()[0]
		t = node.text
		try:
			self.sell = float(t)
		except Exception,e:
			self.sell = None

	def parseComment(self, s):
		'''
		<td>日涨幅偏离值达7%</td>
		'''
		root = etree.fromstring(s)
		node = root
		while len(node.getchildren())>0:
			node = node.getchildren()[0]
		t = node.text
		t = t.replace(' ', '')
		self.comment = t

class TopSaleDepartment(object):
	'''
	获取"证券公司营业部交易龙虎榜"页面数据
	'''
	def __init__(self, parent):
		super(TopSaleDepartment, self).__init__()
		self.parent = parent
	

	def getFirstPageUrl(self):
		'''
		根据导航菜单内容获取首页地址
		'''
		key_word_in_menu = '证券公司营业部交易龙虎榜'
		l = self.parent.getNavMenu().split('\n')
		key_line = None
		for line in l:
			if key_word_in_menu in line:
				key_line = line
				break
		if key_line==None:
			raise Exception('无法在导航菜单中获取关键字\'%s\''%key_word_in_menu)
		key_line = key_line.strip(' \t\r\n')
		key_line = key_line[key_line.index('>')+1 : key_line.rindex('<')] # 第一个节点格式有问题,去掉
		root = etree.fromstring(key_line)
		link_node = root.find('a')
		page_link = link_node.attrib.get('href')
		page_link = '/'.join((self.parent.baseUrl, page_link))
		return page_link

	def getPageUrls(self, first_page_url):
		'''
		抓取首页获取所有页的地址
		'''
		print '获取各数据页地址...'
		first_page = requests.get(first_page_url)
		if first_page.status_code!=200:
			raise Exception('无法首页内容')
		#print first_page.content
		
		interested_lines = []
		l = first_page.content.split('\n')
		for line in l:
			if re.search('>[\d]{1,5}<\/a>', line)!=None: # 防止误识别六位交易码
				interested_lines.append(line)
		result = {}
		for item in interested_lines:
			# 格式不符合xml
			snd_pos = item.rfind('<')
			first_pos = item[:snd_pos].rfind('>')
			first_pos += 1
			link = item[0:first_pos]
			page = item[first_pos:snd_pos]
			href_part = link.split(' ')[1]
			page_url = href_part[href_part.index('=')+1:]
			page = int(page)
			#print page_url
			#print page
			result[page] = '/'.join((self.parent.baseUrl, page_url))
		return result

	def getEveryPageContent(self, page_urls):
		'''
		逐页抓取并获取内容.
		'''
		final_result = []
		for page_idx,url in page_urls.items():
			print '获取页面%d/%d, %s'%(page_idx, len(page_urls), url)
			
			page = requests.get(url)
			if page.status_code!=200:
				raise Exception('无法获取第%d页的内容'%page_idx)
			#with open('%d'%page_idx, 'w') as fd:
			#	fd.write(page.content)
			
			target_line = None
			for line in page.content.split('\n'):
				if '</td></tr></table>' in line:
					target_line = line
					break

			if target_line==None:
				continue
			
			segs = parseStrWithTagPair(target_line, '<tr>', '</tr>')
			for seg in segs:
				row = TopSaleDepartmentRow(seg)
				final_result.append(row)
		
		return final_result
		
	def getContent(self):
		'''
		- 根据导航菜单内容获取首页地址;
		- 抓取首页获取所有页的地址;
		- 逐页抓取并解析内容.
		'''
		page_urls = {}

		# Step 1
		page_urls[1] = self.getFirstPageUrl()
		#print '首页地址 : %s' % page_urls[1]
		
		# Step 2
		left_page_urls = self.getPageUrls(page_urls[1])
		page_urls = dict(page_urls, **left_page_urls)
		
		# Step 3
		#print page_urls
		return self.getEveryPageContent(page_urls)
		
