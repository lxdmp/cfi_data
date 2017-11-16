# coding=utf-8
import requests
from lxml import etree
import re

# 总体考虑:
# 先获取菜单栏,依据关键字获取数据子页面的链接
class CfiData(object):
	base_url = 'http://data.cfi.net.cn'

	def __init__(self):
		super(CfiData, self).__init__()
		self.getMenu()

	def getMenu(self):
		'''
		获取菜单栏
		'''
		menu_path = 'cfidata.aspx'
		menu_param = {'fr' : 'menu'}
		total_path = '/'.join((self.base_url, menu_path))
		result = requests.get(total_path, data=menu_param)
		if result.status_code!=200:
			raise Exception('无法获取菜单')
		self.menu_content = result.content

	def getTopSaleDepartment(self):
		'''
		获取营业部数据

		- 根据菜单内容获取首页地址;
		- 分析首页获取所有页的地址;
		- 逐页抓取并解析内容.
		'''
		page_urls = {}

		# Step 1
		key_word_in_menu = '证券公司营业部交易龙虎榜'
		l = self.menu_content.split('\n')
		key_line = None
		for line in l:
			if key_word_in_menu in line:
				key_line = line
				break
		if key_line==None:
			raise Exception('无法在菜单中获取关键字\'%s\''%key_word_in_menu)
		key_line = key_line.strip(' \t\r\n')
		key_line = key_line[key_line.index('>')+1 : key_line.rindex('<')] # 第一个节点格式有问题,去掉
		root = etree.fromstring(key_line)
		link_node = root.find('a')
		page_link = link_node.attrib.get('href')
		page_link = '/'.join((self.base_url, page_link))
		page_urls[1] = page_link
		
		first_page = requests.get(page_link)
		if first_page.status_code!=200:
			raise Exception('无法首页内容')
		#print first_page.content
		
		# Step 2
		interested_lines = []
		l = first_page.content.split('\n')
		for line in l:
			if re.search('>[\d]{1,5}<\/a>', line)!=None: # 防止误识别六位交易码
				interested_lines.append(line)
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
			page_urls[page] = '/'.join((self.base_url, page_url))
		
		# Step 3
		#print page_urls
		for page_idx,url in page_urls.items():
			page = requests.get(url)
			if page.status_code!=200:
				raise Exception('无法获取第%d页的内容'%page_idx)
			print '获取页面%d/%d'%(page_idx, len(page_urls))
			with open('%d'%page_idx, 'w') as fd:
				fd.write(page.content)

if __name__=='__main__':
	o = CfiData()
	o.getTopSaleDepartment()

