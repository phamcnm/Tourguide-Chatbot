'''
building.py

This building class stores information about the Carleton buildings
It gets that from json files in the building_grammars folder

@author: Yuting, PJ, and Minh
@date: 05/14/2021
'''

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
        