from grammar import *
import json 

class Building:
    """
    A class to represent a building
    """
    def __init__(self, json_path, name):
        self.name = name
        self.grammar = Grammar(json_path)

    def generate_fact(self, start_symbol) -> str:
        """
        Generates fact(string) from the grammar json
        """
        return self.grammar.generate(start_symbol)