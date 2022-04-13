'''
grammar.py
Parses and generates grammar for koffee

@author: Yuting, PJ, and Minh
@date: 05/14/2021
'''

import json
import random
import sys
class NonterminalSymbol:
	def __init__(self):
		self.rules = [] # list of ProductionRules

	def add_rule(self, rule): # ruls is a ProductionRules Object
		self.rules.append(rule)
		

class ProductionRule:
	def __init__(self, non_terminal_symbol_obj, symbol, body):
		self.head = non_terminal_symbol_obj
		self.symbol = symbol # symbol of head
		self.body = body # list of string, Call_Promise, and/or Set_Variable


class Call_Promise:
	"""
	Promises the generate function that the value will either be in
	the self.grammars_dict or the self.variables dictionary
	"""

	def __init__(self, value):
		self.value = value # string


class Set_Variable:
	"""
	Tells the generate function that it should call the set_variable
	with the self.key and self.value
	"""
	def __init__(self, key, value):
		self.key = key # string
		self.value = value # string/Call_Promise/Set_Variable


class Parse_Result:
	def __init__(self, body, left_string):
		self.left_string = left_string #string
		self.body = body #list


class Grammar:
	def __init__(self, json_path):
		with open(json_path, 'r') as json_file:
			data = json.load(json_file)
		self.grammars_dict = {} # string -> NonterminalSymbol
		self.variables = {}

		self.parsed_data = self.parse_json(data)


	def get_string_from_token(self, token):
		"""
		Constructs a string from a given token

		Checks the type of the token and deals with it accordingly

		If token is a string, returns the token
		If token is a Callable_Promise, treats the token as either a variable or a nonterminal
			-> 	for variable, returns the val from the self.variables dictionary
			-> 	for nonterminal, randomly chooses a production rule and recursively calls 
					get_string_from_production_rule
		If token is a Set_Variable, calls set_variable and return an empty string

		Parameters:
		token: str, Call_Promise object, or Set_Variable object

		Return:
		a string from the given token
		"""

		if type(token) == str:
			return token

		elif type(token) == Call_Promise:
			token = token.value
			if token in self.variables:
				return self.variables[token]

			elif token in self.grammars_dict:
				random_production_rule = random.choice(self.grammars_dict[token].rules)
				return self.get_string_from_production_rule(random_production_rule)

			else: #SHOULD NOT EVER REACH THIS
				print("ERROR: reaches else in Call_Promise case of get_string_from_token.")

		elif type(token) == Set_Variable:
			self.set_variable(token.key, token.value)
			return ""

		else: #SHOULD NOT EVER REACH THIS
			print("ERROR: reaches else in get_string_from_token.")


	def get_string_from_production_rule(self, production_rule):
		"""
		Constructs a string from a given production_rule

		Parameters:
		production_rule: a production rule with body as a list that 
		consists of string(s), Callable_Promise(s) and/or Set_Variable(s)

		Return:
		a string from the given production_rule
		"""
		res_string = ""
		token_list = production_rule.body
		for token in token_list:
			res_string += self.get_string_from_token(token)
		return res_string


	def set_variable(self, key, token):
		self.variables[key] = self.get_string_from_token(token)


	def generate(self, start_symbol):
		"""
		Generates text based on the grammar loaded and stored in this program.
		It usses the get_string_from_production_rule() as a helper function
		
		Parameters: 
		start_symbol: a string to start the sentence
		Returns: 
		the string generated
		"""
		if start_symbol not in self.grammars_dict:
			sys.exit("ERROR: Invalid start_symbol.")

		random_production_rule = random.choice(self.grammars_dict[start_symbol].rules)
		return self.get_string_from_production_rule(random_production_rule)


	def parse_value(self, value, body):
		"""
		Parse the String formatted production rule and append it to the body list
		
		Note that this function only parses out one chunck of the string, the rest of the string
		will be returned.
		
		ex: "Today, [alien:alienCreature] #alien# showed up in front of #boyName#."
		This function will be called five times:
			1st time:
				-body = ["Today, "]
				-subtracted string = "[alien:alienCreature] #alien# showed up in front of #boyName#."
			2nd time:
				-body = ["Today, ", Set_Variable]
				-subtracted string = "#alien# showed up in front of #boyName#."
			3rd time:
				-body = ["Today, ", Set_Variable, Call_Promise]
				-subtracted string = "showed up in front of #boyName#."
			.
			.
			.
			
		Parameters:
		value: str
		body: list

		Return:
		a Parse_Result that includes the subtracted string and the modified body list
		"""
		first_char = value[0]
		i = 0
		if first_char == '#':
			symbol_name = ""
			i += 1 
			while i < len(value) and value[i] != '#':
				symbol_name += value[i]
				i += 1
			i += 1
			# set callable
			new_callable = Call_Promise(symbol_name) #COMMENT THIS OUT FOR VISIBLE
			# new_callable = "callable: <{}>".format(symbol_name) #VISIBLE
			body.append(new_callable)

		elif first_char == '[':
			# only set self.variables
			token_key = "" 
			token_value = ""
			i += 1 
			while value[i] != ':':
				token_key += value[i]
				i += 1 
			i += 1 # skips :
			while value[i] != ']':
				token_value += value[i]
				i += 1 
			i += 1 

			# checks if the value is a Callable Object or not
			if token_value[0] == "#":
				token_value = token_value[1:len(token_value) - 1]
				token_value = Call_Promise(token_value) #COMMENT THIS OUT FOR VISIBLE
				# token_value = "callable: <{}>".format(token_value) #VISIBLE

			new_set_variable = Set_Variable(token_key, token_value) #COMMENT THIS OUT FOR VISIBLE
			# new_set_variable = "key: <{}> val:<{}>".format(token_key, token_value) #VISIBLE
			body.append(new_set_variable)

		else:
			string_name = ""
			while i < len(value) and value[i] != '#' and value[i] != '[':
				string_name += value[i]
				i += 1
			body.append(string_name)

		return Parse_Result(body, value[i:])


	def parse_json(self, data):
		"""
		Parses the json formatted dictionary into self.grammars_dict: a dictionary whose keys are NonterminalSymbol.
		This method will use parse_value() as a helper function

		Parameters: 
		data: the json formatted dictionary
		"""
		for key in data:
			# set Nonterminal for the key nonterminal
			nonterminal = NonterminalSymbol() #COMMENT THIS OUT FOR VISIBLE
			# nonterminal = [] #VISIBLE
			self.grammars_dict[key] = nonterminal
			data_value = data[key] 

			for value in data_value:
		# create productionRule
				body = []
				while not len(value) == 0:
					parse_result = self.parse_value(value, body)
					value = parse_result.left_string
					body = parse_result.body
				new_production_rule = ProductionRule(nonterminal, key, body)
				# nonterminal.append(body) #VISIBLE
				nonterminal.add_rule(new_production_rule) #COMMENT THIS OUT FOR VISIBLE


def main():
	"""
	Idea:
	The program parses the json file into self.grammars_dict where it stores the string symbol
	for each nontermial as keys and NonterminalSymbol Object as values. The body of each 
	NonterminalSymbol Object will be a list that consists of string, Set_Variable, and/or 
	Call_Promise which are being parsed out by our helper function. The NonterminalSymbol's
	body is basically storing a list of "commands" of what the generate function should do.

	If the generate sees a string, it will just use it. If the generate sees a Set_Variable 
	Object, it will call the set_variable function and stores the runtime variable in the 
	self.variables dictionary. If the generate sees a Call_Promise object, it will check if the
	value of Call_Promise exists in self.variables dictionary or self.grammars_dict (the Call_Promise
	object promises generate that the value inside should exists in one of the dictionary).

	For the input, the program takes in a .json file with a very similar set notations like
	Tracey's input but with some limitations. 

	Limitations:
	1) No square bracket without : inside.
		Ex:
			{
				"origin": [
					"[#setBoyDetails#]#story#" 	(Not Allowed)
				],
				"setBoyDetails": [
					"[boyName:#name#][boyAge:#age#][boyHobby:#hobby#]"
				]
				...
			}
			
			{
				"origin": [
					"#setBoyDetails##story#" 	(Allowed)
				],
				"setBoyDetails": [
					"[boyName:#name#][boyAge:#age#][boyHobby:#hobby#]"
				]
				...
			}

			(The output is similar to Tracey's)

	2) No modifiers.
		No #__.captaize#, #__.a#, #__.s#, etc.

	3) No nested # signs.
		Ex:
			"##setBoyDetails#story#" 			(Not Allowed)
			"#setBoyDetails##story#" 			(Allowed)

	4) Set_Variable can either be a string or a Nonterminal (not both).
		Ex:
			"[alien:#alienCreature# is bad]" 	(Not Allowed)
			"[alien:is bad]" 					(Allowed)
			"[alien:#alienCreature#]" 			(Allowed)

	NOTE:
		VISIBLE comments are the lines of code that are used to print out the self.grammars_dict.
			(Since self.grammars_dict stores objects, we had no way of seeing what self.variables are
				inside the dictionary but to replace the object with strings)
	"""
	# use json lib to read json file
	json_path = "./example.json"
	data = {}
	with open(json_path, 'r') as json_file:
		data = json.load(json_file)
	parsed_data = parse_json(data)

	# print(self.grammars_dict) #VISIBLE
	generated_string = generate("origin") #COMMENT THIS OUT FOR VISIBLE
	print(generated_string) #COMMENT THIS OUT FOR VISIBLE


if __name__ == "__main__":
	main()
