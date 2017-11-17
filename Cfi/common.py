# coding=utf-8

def parseStrWithTagPair(s, start_tag, end_tag):
	'''
	根据一对起始标记,从字串中取出一组子字串
	'''
	final_result = []
	if s==None:
		return final_result

	start_poses = []
	end_poses = []
	keys = [start_tag, end_tag]
	poses = [start_poses, end_poses]
	for i in range(len(keys)):
		key = keys[i]
		pos = 0
		while pos>=0:
			new_pos = s.find(key, pos)
			if new_pos<0:
				break
			poses[i].append(new_pos)
			pos = new_pos+len(key)
	
	if len(start_poses)<len(end_poses):
		return final_result
	
	l = min(len(start_poses), len(end_poses))
	for i in range(l):
		seg = s[start_poses[i] : end_poses[i]+len(end_tag)]
		final_result.append(seg)
	return final_result

