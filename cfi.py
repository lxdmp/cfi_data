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
		print '获取菜单...'
		result = requests.get(total_path, data=menu_param)
		if result.status_code!=200:
			raise Exception('无法获取菜单')
		self.menu_content = result.content

	def getTopSaleDepartment(self):
		'''
		获取营业部数据

		- 根据菜单内容获取首页地址;
		- 抓取首页获取所有页的地址;
		- 逐页抓取并解析内容.
		'''
		page_urls = {}
		print '获取营业部数据...'

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
		
		# Step 2
		print '获取各数据页地址...'
		first_page = requests.get(page_link)
		if first_page.status_code!=200:
			raise Exception('无法首页内容')
		#print first_page.content
		
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

			if target_line!=None:
				start_key = '<tr>'
				end_key = '</tr>'
				start_poses = []
				end_poses = []
				keys = [start_key, end_key]
				poses = [start_poses, end_poses]
				for i in range(len(keys)):
					key = keys[i]
					pos = 0
					while pos>=0:
						new_pos = target_line.find(key, pos)
						if new_pos<0:
							break
						poses[i].append(new_pos)
						pos = new_pos+len(key)
				assert(len(start_poses)==len(end_poses))
				final_result = []
				for i in range(len(start_poses)):
					interested_item_line = target_line[start_poses[i] : end_poses[i]+len(end_key)]
					interested_item = {}
					'''
					数据形如:
					<tr><td><nobr>2017-11-16</nobr></td><td><a href="http://quote.cfi.cn/quote_000038.html" target=_blank>000038</a></td><td>深 大 通</td><td>22.660</td><td><font color=red>10.000%</font></td><td>东方证券股份有限公司北京安苑路证券营业部</td><td>0</td><td>1983.203</td><td>日涨幅偏离值达7%</td></tr>
					'''
					start_key = '<td>'
					end_key = '</td>'
					start_poses = []
					end_poses = []
					keys = [start_key, end_key]
					poses = [start_poses, end_poses]
					for idx in range(len(keys)):
						key = keys[i]
						pos = 0
						while pos>0:
							new_pos = target_line.find(key, pos)
							if new_pos<0:
								break
							poses[i].append(new_pos)
							pos = new_pos+len(key)
					assert(len(start_poses)==len(end_poses))



					final_result.append(interested_item)

		return final_result

if __name__=='__main__':
	o = CfiData()
	o.getTopSaleDepartment()

