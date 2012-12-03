from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
import re

actions=['page_load','save_URL','redirect']

class Countsperactionbrowser(MRJob):
	INPUT_PROTOCOL = JSONValueProtocol

	def mapper(self, _, log):
		unique_browser = log['browser']
		yield "browser", unique_browser

	def reducer(self, key, browsers ):
		iterable_list = list(browsers)
		number_of_total_actions = len(iterable_list)
		number_of_unique_browsers = len(set(iterable_list))
		yield "counts per action per browser:", float (number_of_total_actions) / float(number_of_unique_browsers) / len(actions)

if __name__ == '__main__':
	Countsperactionbrowser.run()

