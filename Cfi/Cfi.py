# coding=utf-8
import requests
from lxml import etree
import re

from TopSaleDepartment import TopSaleDepartment

# 总体考虑:
# 先获取菜单栏,依据关键字获取数据子页面的链接
class CfiData(object):
	base_url = 'http://data.cfi.net.cn'

	def __init__(self):
		super(CfiData, self).__init__()
		self.getNavMenu()

	@property
	def baseUrl(self):
		return self.base_url

	def getNavMenu(self):
		'''
		获取"导航菜单"页面内容
		'''
		store_key = 'menu_content'
		
		if self.__dict__.has_key(store_key) and self.__dict__[store_key]!=None:
			return self.__dict__[store_key]
		else:
			menu_path = 'cfidata.aspx'
			menu_param = {'fr' : 'menu'}
			total_path = '/'.join((self.base_url, menu_path))
			print '获取导航菜单页面...'
			result = requests.get(total_path, data=menu_param)
			if result.status_code!=200:
				raise Exception('无法获取导航菜单页面')
			self.__dict__[store_key] = result.content
			return self.__dict__[store_key]

	def getTopSaleDepartment(self):
		'''
		获取"证券公司营业部交易龙虎榜"页面数据
		'''
		o = TopSaleDepartment(self)
		return o.getContent()
		
