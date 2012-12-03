from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
import re

actions=['page_load','save_URL','redirect']

class MostfollowedURLs(MRJob):
	INPUT_PROTOCOL = JSONValueProtocol

	def get_urls(self, _, log):
		if log['action'] == 'redirect':
			yield log['url'], 1


	def sum_counts(self, url, counts):
		total_of_url = sum(counts)
		yield 'max', (total_of_url, url)

	def get_max(self, metric, url_counts):
		yield 'max', max(url_counts)

	def steps(self):
		return [self.mr(self.get_urls, self.sum_counts),self.mr(reducer=self.get_max)]

	

if __name__ == '__main__':
	MostfollowedURLs.run()
