'''
dependency_parsing.py

functions for the dependecy parsing, which is a method
to parse natural language sentences into parts that
depend on each other in natural language grammars

@author: Yuting, PJ, and Minh
@date: 05/14/2021
'''
import spacy

def find_verb_chunk(doc):
	"""
	Returns a dictionary representing a simple verb chunk
	with a subject, verb, object.
	"""
	for noun_chunk in doc.noun_chunks:
		if noun_chunk.root.dep_ != 'nsubj':
			continue
		subj = noun_chunk.root
		verb = subj.head
		for child in verb.children:
			obj = child
			if child.dep_ == 'dobj':
				verb_chunk = {
					"subject": subj,
					"verb": verb,
					"object": obj
				}
				return verb_chunk
		return None


def find_prep_chunk(doc):
	"""
	Returns a dictionary representing a simple verb chunk
	with a subject, verb, object.
	"""
	# “I learn quickly in stress and pain.”
	for noun_chunk in doc.noun_chunks:

		subj = noun_chunk.root # stress
		subj_full = noun_chunk 
		if subj.head.dep_ == 'prep': # head = in
			prep = subj.head
			prep_chunk = {
				"full_subject": subj_full,
				"subject": subj,
				"prep": prep
			}
			return prep_chunk

	return None


def find_subj_chunk(doc):
	"""
	Returns a dictionary representing a subject chunk
	with a subject and an (optional) adjective
	"""
	for noun_chunk in doc.noun_chunks:
		if noun_chunk.root.dep_ != 'nsubj':
			continue
		subj = noun_chunk.root
		adj = None
		for child in subj.children:
			if child.dep_ == 'amod' or child.dep_ == 'acl' or child.dep_ == 'acomp':
				adj = child
				break

		subj_chunk = {
			"subject": subj,
			"adjective": adj
		}

		return subj_chunk

	return None


def find_adv_chunk(doc):
	"""
	Returns a dictionary representing a adverb chunk
	with a subject, a verb and an adverb
	"""
	for noun_chunk in doc.noun_chunks:
		# print("noun_chunk is {}".format(noun_chunk))
		if noun_chunk.root.dep_ != 'nsubj':
			continue
		subj = noun_chunk.root
		if subj.head.dep_ == 'ROOT':
			verb = subj.head
			# print("verb is {}".format(verb))
			for child in verb.children:
				# print("child is {}".format(child))
				# print("child dep is {}".format(child.dep_))
				if child.dep_ == "advmod":
					adverb = child
					adverb_chunk = {
						"subject": subj,
						"verb": verb,
						"adverb": adverb
					}
					return adverb_chunk
		return None


def find_obj_chunk(doc):
	"""
	Returns a dictionary representing an objective chunk
	with an objeect and an (optional) adjective
	"""
	for noun_chunk in doc.noun_chunks:
		if noun_chunk.root.dep_ != 'dobj':
			continue
		obj = noun_chunk.root
		adj = None
		for child in obj.children:
			if child.dep_ == 'amod' or child.dep_ == 'acl' or child.dep_ == 'acomp':
				adj = child
				break

		obj_chunk = {			
			"objective": obj,
			"adjective": adj
		}
		return obj_chunk

	return None


def find_subj_verb_chunk(doc):
	"""
	Returns a dictionary representing a simple verb chunk
	with a subject and verb.
	"""
	for noun_chunk in doc.noun_chunks:
		if noun_chunk.root.dep_ != 'nsubj':
			continue
		subj = noun_chunk.root
		verb = subj.head
		return({					
			"subject": subj,
			"verb": verb
		})

	return None


def find_subj_verb_prep_obj_chunk(doc):
	"""
	Returns a dictionary representing a simple verb chunk
	with a subject, verb, perp, object.
	"""
	for noun_chunk in doc.noun_chunks:
		if noun_chunk.root.dep_ != 'nsubj':
			continue
		subj = noun_chunk.root
		verb = subj.head
		for child in verb.children:
			if child.dep_ == 'prep':
				prep = child
				for prep_child in child.children:
					if prep_child.dep_ == 'pobj':
						obj = prep_child
						subj_verb_prep_obj_chunk = {
							"subject": subj,
							"verb": verb,
							"preposotion": prep,
							"object": obj	
						}
						return subj_verb_prep_obj_chunk

		return None


def print_result(doc):
	for noun_chunk in doc.noun_chunks:
		print("\nnoun_chunk is {}".format(noun_chunk))
		print("noun_chunk.root.text is {}\n".format(noun_chunk.root.text))
		subj = noun_chunk.root
		verb = subj.head
		print("verb(head) is {}".format(verb))
		
		print("head dep is {}".format(verb.dep_))
		for child in verb.children:
			print("child is {} and its dep_ is {}".format(child, child.dep_))
		
		print()
		print("subj is {}".format(subj))
		for child in subj.children:
			print("child is {} and its dep_ is {}".format(child, child.dep_))


def derive_question(doc):
	"""
	Return a string that rephrases an action in the
	doc in the form of a question.
	'doc' is expected to be a spaCy doc.
	"""
	verb_chunk = find_verb_chunk(doc)
	if not verb_chunk:
		return None
	subj = verb_chunk['subject'].text
	obj = verb_chunk['object'].text
	if verb_chunk['verb'].tag_ != 'VB':
		# If the verb is not in its base form ("to ____" form),
		# use the spaCy lemmatizer to convert it to such
		verb = verb_chunk['verb'].lemma_
	else:
		verb = verb_chunk['verb'].text
	question = "Why did {} {} {}?".format(subj, verb, obj)
	return question


def main():
	"""
	Main function for testing
	"""
	test_string = "I strongly disagree with your idea"
	nlp = spacy.load("en_core_web_sm")
	doc = nlp(test_string)

	res = find_adv_chunk(doc)

if __name__ == "__main__":
	main()