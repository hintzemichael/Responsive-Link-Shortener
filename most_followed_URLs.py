'''This program returns the URL that gets the most redirects'''

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
import re

actions=['page_load','save_URL','redirect']

class MostfollowedURLs(MRJob):
	INPUT_PROTOCOL = JSONValueProtocol

	'''maps all the URL and their count'''
	def get_urls(self, _, log):
		if log['action'] == 'redirect':
			yield log['url'], 1

	'''sums the counts of each URL and maps them into the same metric'''
	def sum_counts(self, url, counts):
		total_of_url = sum(counts)
		yield 'max', (total_of_url, url)

	'''gets the URL that has the max counts'''
	def get_max(self, metric, url_counts):
		yield 'max', max(url_counts)

	def steps(self):
		return [self.mr(self.get_urls, self.sum_counts),self.mr(reducer=self.get_max)]

if __name__ == '__main__':
	MostfollowedURLs.run()
