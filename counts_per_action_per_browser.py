'''This program returns counts per action per browser'''

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
from itertools import izip
from collections import defaultdict

class Countsperactionbrowser(MRJob):
	INPUT_PROTOCOL = JSONValueProtocol

	'''mapper will map browser name as a key, and action type and count as a tuple'''
	def mapper(self, _, log):
		yield log['browser'], (log['action'],1)
		
	'''reducer will aggregate all the values of per action per browser into a dicionary'''
	def reducer(self, browser, action_counts):
		action_type, action_count = izip(*action_counts)
		action_list = zip(action_type, action_count)
		d1 = defaultdict(list)
		for k,v in action_list:
			d1[k].append(v)
			d = dict( (k,sum(tuple(v))) for k,v in d1.iteritems() )
		yield browser, d

if __name__ == '__main__':
	Countsperactionbrowser.run()

