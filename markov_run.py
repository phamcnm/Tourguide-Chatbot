import random
import re
import sys
import statistics

class SLM:
	"""
	Class SLM represents an statistical language model
	"""

	def __init__(self, corpus, level, order):
		"""
		Intializer of SLM
		Parameters: 
			corpus a string for the pathfile to the corpus
			level: "word" or "character", the level to train on
			order: an integer representing how many tokens to be considered as one
		"""
		self.corpus = corpus
		self.level = level
		self.order = order
		'''
		self.transitions = {
			(tuple_of_ngram) : 
				[
					(
						['next_token_string'], (lower_bound_float, upper_bound_float)
					),
					(), (), ...
				]
			() : [(), (), ()] ...
		}
		'''
		# will contain either tokenized chars or words in order of appearance in the text
		self.tokenized_list = [];
		self.transitions = {}
		self.mean = -1
		self.standard_deviation = -1

		
	def split_with_word(self, string):
		"""
		Takes in a string and splits it into tokens by words. 
		Tabs, newlines, and punctuations count as tokens
		
		Parameters:
			string: the string to be tokenized
			
		Returns:
			lst: the list of tokens
		"""
		lst = []

		string = string.lower()
		string_length = len(string) 
		token = ""

		for i in range(string_length):
			# append \[smth] operation to the lst and skip one index
			if string[i] == "\\":
				lst.append(string[i] + string[i + 1]) # for \t, \n, etc.
				i+=1
			# append token to lst and reset token
			elif string[i] == " ": 
				# token will be "" when the previous index is a symbol
				if token != "": 
					lst.append(token) 
					token = ""
			# append token to lst, append symbol to lst, and reset token
			elif not string[i].isalpha() and not string[i].isdigit():
				if token != "": 
					lst.append(token) 
					token = ""
				lst.append(string[i]) # append symbol
			# construct token with current character
			else:
				token += string[i]
					
		return lst


	def split_with_character(self, string):
		"""
		Takes in a string and splits it into tokens by characters. 
		Tabs, newlines, and punctuations count as tokens
		
		Parameters:
			string: the string to be tokenized
			
		Returns:
			lst: the list of tokens
		"""
		lst = []

		string = string.lower()
		string_length = len(string) 

		for i in range(string_length):
			# append \[smth] operation to the lst and skip one index
			if string[i] == "\\":
				lst.append(string[i] + string[i + 1]) # for \t, \n, etc.
				i+=1
			# skip when hit space
			elif string[i] == " ": 
				i+=1
			# append current character to the lst
			else:
				lst.append(string[i]) # append symbol

		return lst

		
	def populate_transitions_from_lst(self, lst, p):
		"""
		Helper function for train.
		Populates self.transitions dictionary from a lst of strings that is 
		ordered based on their appearance in the corpus.
		
		Parameters:
			lst: a list of tokens
			p: a number between 0 and 100, the percentage of the lst to be trained on from the beginning
		"""
		if len(lst) < self.order:
			sys.exit("ERROR: The corpus is smaller than the order." +\
			"\nLower the order or change to a bigger corpus")
		
		# to ensure that there is at least one \n in the lst
		lst.insert(0, "\n") 

		t = {} # intermideate dict for transitions later
		ngram_list = ["placeholder"] # the current n-gram
		ngram = () # initialize an empty tuple version of ngram_list

		for i in range(self.order-1):
			ngram_list.append(lst[i]) 
		
		train_till = int(len(lst)/100*p)
		# fill up t below
		for i in range(self.order, train_till): 
			# new ngram
			ngram_list.pop(0)
			ngram_list.append(lst[i-1])
			ngram = tuple(ngram_list) 

			# Special case for new lines
			if ngram_list[0] == "\n":
				tmp_ngram = tuple("\n")
				words_after_gram = []
				for j in range(1, len(ngram_list)):
					words_after_gram.append(ngram_list[j]) 
				words_after_gram.append(lst[i])
				
				if tmp_ngram not in t:
					t[tmp_ngram] = [[],[]]
				
				if words_after_gram in t[tmp_ngram][0]:
					idx = t[tmp_ngram][0].index(words_after_gram)
					t[tmp_ngram][1][idx] += 1
				else:
					t[tmp_ngram][0].append(words_after_gram)
					t[tmp_ngram][1].append(1)
			
			# Normal cases  
			if ngram not in t:
				t[ngram] = [[],[]]

			word_after_gram = [lst[i]]
			if word_after_gram in t[ngram][0]:
				idx = t[ngram][0].index(word_after_gram)
				t[ngram][1][idx] += 1
			else:
				t[ngram][0].append(word_after_gram)
				t[ngram][1].append(1)
			
		# fill up transitions from t, below
		for key in t:
			info = t[key] # ex, [[w1, w2, w3], [1,3,2]]
			value = [] # value in transitions, to be filled
			counts = sum(info[1])
			lo = 0.0
			for idx in range(len(info[0])):
				hi = lo + info[1][idx]/counts
				tup = (info[0][idx], (lo, hi))
				value.append(tup)
				lo = hi
			# value should be filled by now
			self.transitions[key] = value


	def train(self, p=100, chunck_size=1000):
		"""
		Trains a model given the percentage to train.
		The chunk size can be provided to create a z_score_estimator out of this

		Parameters:
			p (optional): a number between 0 and 100 representing how much of the corpus            should be trained from the beginning
			chunck_size (optional): the chunk size for the z score estimator
		"""
		# if token_list is empty, calculate and record the tokenized_list
		if not self.tokenized_list:
			file = open(self.corpus, "r")

			# tokenize each line of the file based on the level parameter
			if self.level == "word":
				corpus_string = (" ").join(file)
				self.tokenized_list = self.split_with_word(corpus_string)

			elif self.level == "character":
				corpus_string = (" ").join(file)
				self.tokenized_list = self.split_with_character(corpus_string)

			else:
				sys.exit("ERROR: Invalid level parameter: " + self.level + \
					"\nlevel should either be \"word\" or \"character\"")

			file.close()

		self.populate_transitions_from_lst(self.tokenized_list, p)

		if p < 100:
			self.z_score_estimator(chunck_size, 100 - p)


	def find_next(self, key):
		"""
		Helper function for generate()
		Probabilistically finds the next word from transitions, given key
		
		Parameters:
			key: a tuple of tokens
		"""
		try:
			words = []
			random_float = random.random()
			candidates = self.transitions[tuple(key)]
			for i in range(len(candidates)):
				bounds = candidates[i][1]
				if random_float < bounds[1]:
					words = (candidates[i][0])
					break
			return words
		# when key is not a valid ngram (key does not exist in transitions)
		except KeyError:
			raise KeyError("ERROR: the key \"{}\" does not exist in the corpus.".format((" ").join(key)))

	
	def eliminate_white_space_on_symbol(self, string):
		"""
		Helper function for generate()
		Removes whitespaces that come before symbols
		"""
		return re.sub("\s+(?=[\W])", "", string)


	def generate(self, length, prompt="\n"):
		""""
		Generates text with the size of a given length based on the trained model. 

		The prompt is an optional starting word(s) for the generated text. The 
		size of the prompt has to be greater than or equal to the order of
		the class, or else the function will use a random text as a starting
		prompt

		Parameters:
			length: the length of the text to be generated (measured by tokens)
			prompt (optinal): text to start off

		Returns:    
			result: generated string or None if prompt is invalid or generate 
					runs into an edge case where focused_phrase is not in the 
					transitions dict
		"""
		tokenized_prompt = [] 
		if self.level == "word":
			tokenized_prompt = self.split_with_word(prompt)

		elif self.level == "character":
			tokenized_prompt = self.split_with_character(prompt)

		else:
			sys.exit("ERROR: Invalid level parameter: " + self.level + \
				"\nlevel should either be \"word\" or \"character\"")

		# Generate the starter of the sentence 
		starter = []
		if len(tokenized_prompt) < self.order:
			# print("NOTICE: The prompt is too short or it is not provided, we will generate a sentence randomly.\n")
			try:
				starter = list.copy(self.find_next("\n"))
			except KeyError as err:
				# print(err) # should never reach this except
				return None
		else:
			starting_point = len(tokenized_prompt) - self.order
			for i in range(self.order):
				starter.append(tokenized_prompt[starting_point + i])
		
		# Generate the rest of the sentence
		next_word = []
		focused_phrase = starter
		result = ""

		for j in range(len(starter)):
				result += starter[j] + " "
		
		for k in range(self.order, length):
			try:
				next_word = self.find_next(focused_phrase)
			# catch edge case when focused_phrase is not in the corpus
			except KeyError as err:
				# print(err)
				return None
			for word in range(len(next_word)):
				result += next_word[word] + " "
			focused_phrase.pop(0)
			focused_phrase.extend(next_word)

		result = self.eliminate_white_space_on_symbol(result)

		return result


	def get_likelihood(self, tokenized_text):
		"""
		Gets the likelihood that a given tokenized_text is generated by this model.
		
		Parameters: 
			tokenized_text: the text as a list of tokens
		Returns:
			raw_score: the sum of probability of all the grams being generated by this model
		"""
		# calculate raw_score and likelihood of every sentence
		ngram_list = ["placeholder"]
		raw_score = 0.0
		for i in range(self.order-1):
			ngram_list.append(tokenized_text[i])
		for i in range(self.order, len(tokenized_text)): 
			# new ngram
			ngram_list.pop(0)
			ngram_list.append(tokenized_text[i-1])
			ngram = tuple(ngram_list)
			curr = tokenized_text[i]

			if ngram in self.transitions:
				# find if the current word is in transitions's value
				values = self.transitions[ngram]
				for v in values: 
					#each v is a tuple, ex, ([“brown”], (0.0, 0.65))
					if v[0][0] == curr:
						score = v[1][1] - v[1][0]
						raw_score += score
		return raw_score


	def z_score_estimator(self, chunk_size, test_size):
		"""
		Calculates the mean and the standard_deviation of the likihoods from the test
		portion of the model's tokenized_list by splitting the test portion into chunks

		Parameters:
			chunk_size: the numbers of words in each chunk
			test_size: the size of the test portion (out of a 100)
		"""
		tokenized_list_length = len(self.tokenized_list)
		# iterate through the chunks
		start = int(tokenized_list_length * (100 - test_size) / 100) 
		
		chunk_raw_scores = []
		if (start + self.order > tokenized_list_length):
			sys.exit("ERROR: The text to be estimated is too small")
		
		while (start < tokenized_list_length):

			end = start + chunk_size
		
			if end > tokenized_list_length - chunk_size: 
				# should just extend to the end
				end = len(self.tokenized_list)
			
			# normalizes the likelihood by dividing with the size
			likelihood_score = self.get_likelihood(self.tokenized_list[start:end]) / (end - start)  
			chunk_raw_scores.append(likelihood_score)
			start = end # increments chunk_size at a time

		# cal sd and mean
		self.standard_deviation = statistics.stdev(chunk_raw_scores)
		self.mean = sum(chunk_raw_scores) / len(chunk_raw_scores)


	def estimate(self, input_text):
		"""
		Finds the z_score of the input_text given the z score estimator

		Parameters:
			input_text: the string that is the input text

		Returns:
			input_z_score: the z_score of the input text estimated by the z_score_estimator of this model
		"""
		tokenized_input = [];

		tokenized_input = self.split_with_word(input_text)

		# calculate likelihood and zscore
		input_likelihood = self.get_likelihood(tokenized_input) / len(tokenized_input)
		input_z_score = (input_likelihood - self.mean) / self.standard_deviation

		return input_z_score
		

def train_multiple_models(path_list, SLM_parameter_list, train_size=100, chunk_size=250):
	"""
	Trains multiple models from the given list of corpora path.
	There is an option to train on only a percentage of the corpora given.

	Parameters: 
		path_list: a list of strings of the path to the corpora
		SLM_parameter_list: parameters to initalize the SLMs
		train_size (optinal): a number between 0 and 100 representing how much of the   
							corpora should be trained fro the beginning
		
	Returns:
		model_list: the trained models as a list
	"""
	path_len = len(path_list)
	parameter_len = len(SLM_parameter_list)
	
	model_list = []

	if (path_len != parameter_len):
		sys.exit("ERROR: the sizes of path_list and SLM_parameter_list do not match.")

	for i in range(path_len):
		path = path_list[i]
		level = SLM_parameter_list[i][0]
		order = SLM_parameter_list[i][1]

		slm = SLM(path, level, order)
		slm.train(train_size, chunk_size)
		
		model_list.append(slm)

	return model_list


def estimate_tokenized_list_with_models(tokenized_list, model_list, chunk_size):
	"""
	Splits the given tokenized_list into chunks of length chunk_size. With each chunk size, 
	calculates the z-scores with the estimate function of each model in model_list and return
	the mean z-scores for the given tokenized_list associated with the models in model_list

	Parameters:
		tokenized_list: the list of tokens to be estimated by the z_score estimators of the models
		model_list: the list of SLMs
		chunk_size: chunk to split the tokenized_list
	
	Returns:
		mean_z_scores: a list of the mean z scores of the tokenized list estimated by the models 
	"""
	z_scores = []
	# initalize lists to hold z-scores for each model
	for i in range(len(model_list)):
		z_scores.append([]) 

	tokenized_length = len(tokenized_list)

	# iterate through the chunks
	start = 0
	while (start < tokenized_length):

		end = start + chunk_size
	
		if end > tokenized_length - chunk_size: 
			# should just extend to the end
			end = tokenized_length
		
		chunk_tokenized_list = tokenized_list[start: end]
		chunk_text = (" ").join(chunk_tokenized_list)
		
		# estimate chunk text with all models
		for i in range(len(model_list)):
			res = model_list[i].estimate(chunk_text)    
			z_scores[i].append(res) 

		start = end # increments chunk_size at a time

	# calculate means for each corpus
	mean_z_scores = []
	for i in range(len(z_scores)):
		tmp_mean_z_score = sum(z_scores[i]) / len(z_scores[i])
		mean_z_scores.append(tmp_mean_z_score)

	return mean_z_scores


def train_markov(path):
	path_list = [path]
	SLM_parameter_list = [["word", 3]]
	train_size = 90 #80%
	chunk_size = 500
	model_list = train_multiple_models(path_list, SLM_parameter_list, train_size, chunk_size)
	return model_list[0]


def main():
	"""
	the main function to run tests
	"""
	# Authorship Attribution Experiment
	# initialize the SLMs for the experiment
	# path1 = "./corpora/donald_trump_collected_tweets.txt"
	path1 = "./our_corpora/crazy_rich_asian_script.txt"
	path2 = "./our_corpora/hamilton_the_musical_full_script.txt"
	path3 = "./our_corpora/jane_eyre.txt"

	path_list = [path1, path2, path3]
	SLM_parameter_list = [
		["word", 3],
		["word", 3],
		["word", 3]
	]

	train_size = 80 #80%
	test_size = 100 - train_size
	chunk_size = 500
	model_list = train_multiple_models(path_list, SLM_parameter_list, train_size, chunk_size)

	z_mean_scores = []
	# iterate thorugh each corpus
	for model in model_list:
		corpus_tokenized_list = model.tokenized_list

		corpus_length = len(corpus_tokenized_list)
		# iterate through the chunks
		start = int(corpus_length * train_size / 100) 
		test_portion_text = corpus_tokenized_list[start:] # uses the last 20% of the text

		tmp_z_mean_scores = estimate_tokenized_list_with_models(test_portion_text, model_list, chunk_size)
		z_mean_scores.append(tmp_z_mean_scores)
	print("\n----Mean Z Scores Matrix----\n")
	print(z_mean_scores)

	print("\n----Generating Words-----\n")
	word_length = 35
	for i in range(len(model_list)):
		print("Generating words from model {i} with length {length}:\n".format(i = i, length = word_length))
		print(model_list[i].generate(word_length))
		print("\n")
	
if __name__ == "__main__":
	main()
