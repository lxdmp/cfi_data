# coding=utf-8
import Cfi

if __name__=='__main__':
	o = Cfi.CfiData()
	result = o.getTopSaleDepartment()
	print len(result)
	#print result

	for item in result:
		print str(item)

