import glob
import math
import os, sys
import operator
import time
import unicodedata

'''
	BASIC FUNCTIONS
	We need these methods for basic operation of the application.
'''
def get_exec_path():
	if ("win" in sys.platform): app = "\\";
	else: app = "/";
	return sys.path[0] + app;

def get_encoding(): return "latin1";

def not_combining(char):
	# Source: http://stackoverflow.com/questions/930303/python-string-cleanup-manipulation-accented-characters/931051#931051
	return unicodedata.category(char) != 'Mn';

def remove_accents(text):
	# Source: http://stackoverflow.com/questions/930303/python-string-cleanup-manipulation-accented-characters/931051#931051
	encoding = get_encoding();
	unicodeText = unicodedata.normalize('NFD',text.decode(encoding));
	return filter(not_combining,unicodeText).encode(encoding);

def remove_duplicates(seq, idfun = None):
	# Source: http://www.peterbe.com/plog/uniqifiers-benchmark (f5)
	if idfun is None:
		def idfun(x): return x;
	seen = {};
	result = [];
	for item in seq:
		marker = idfun(item);
		if marker in seen:
			continue;
		seen[marker] = 1;
		result.append(item);
	return result;

'''
	DICTIONARY FUNCTIONS
	We need these methods for working our dictionary.
'''
def load_dictionary():
	# Loads all dictionary files in /dictionary/ into one array.
	# NOTE: Dictionaries should have an extension that is a NUMBER (NOT txt). That number should indicate the dictionary's commonness.
	dictFiles = glob.glob(os.path.join(get_exec_path()+"dictionary","*.*"));
	dictionaries = [];
	for f in dictFiles:
		try:
			name = f[0:f.rindex(".")];
			ext = f[f.rindex(".")+1:];
			dictionaries.append([name,ext]);
		except:
			pass;
	dictionaries = sorted(dictionaries,key=operator.itemgetter(1,0));
	dictionary = [];
	for element in dictionaries:
		infile = element[0]+"."+element[1];
		file = open(infile,"r");
		newEntries = file.readlines();
		for i in range(len(newEntries)):
			newEntries[i] = [remove_accents(newEntries[i]).strip(),int(element[1])];
		dictionary.extend(newEntries);
		file.close();
	newDictionary = remove_duplicates(dictionary,lambda x:x[0]);
	return newDictionary;

'''
	CRC FUNCTIONS
	We need these methods for calculating distance, priority, and commonness of keystroke combinations.
'''
def calculate_priority(distance, dictionary):
	# This formula can be anything; it uses the keystroke distance sum, 0 being best, and a number 0+ for the dictionary, where 0 is the most common.
	return distance * dictionary;

def letter_distance(origin, char, keyboard):
	# Find out how far apart two letters are based on our provided keyboard layout.
	originCoord = [-1,-1];
	charCoord = [-1,-1];
	for i in range(len(keyboard)):
		row = keyboard[i];
		if (origin in row):
			originCoord[1] = i;
			originCoord[0] = row.index(origin);
		if (char in row):
			charCoord[1] = i;
			charCoord[0] = row.index(char);
	return abs(charCoord[0] - originCoord[0]) + abs(charCoord[1] - originCoord[1]);

def letter_distances_all(word, keyboard):
	# Compute all two-letter distances into a hash-map for quick access.
	global globalChars;
	distances = {};
	for c in word:
		for l in globalChars:
			distances[c+l] = letter_distance(c,l,keyboard);
	return distances;

def word_distance(word, comparison, table):
	# Computes total distance of keystrokes for a word; that is, if the first letter is 1 off and the second letter is 4 off, returns 5.
	if (len(word) != len(comparison)): return -1;
	distance = 0;
	for i in range(len(word)):
		try:
			w = word[i];
			c = comparison[i];
			distance += table[w+c];
		except:
			return -1;
	return distance;

'''
	MAIN FUNCTION
	We need these method to actually get suggestions for a given string.
'''
def get_suggestions(string, keyboard):
	# Our main function that uses all means necessary to list out all possible suggestions for a string from a given keyboard. Sorts using 'calculate_priority'.
	global dictionary;
	
	string = string.lower();
	possibilities = [];
	distances = letter_distances_all(string,keyboard);
	wordlength = len(string);
	
	for entry in dictionary:
		e = entry[0];
		if (len(e) < wordlength): continue;
		eLeft = e[0:wordlength];
		dist = word_distance(string,eLeft.lower(),distances);
		if (dist <= wordlength and dist >= 0):
			possibilities.append([e,calculate_priority(dist,entry[1]),len(e)]);
	
	possibilities = sorted(possibilities,key=operator.itemgetter(2,1));
	return possibilities;

# Initialization...
print "PRELOADING DICTIONARY...";
start = time.time();

dictionary = load_dictionary();

print "TIME SPENT (Loading Dictionaries):\t"+str(round(time.time() - start,6));

# You can have however many rows/cols you want in the keyboard.
# _ is a blank character, as in, there is no key there.
row1 = "q w e r t y u i o p _".split();
row2 = "a s d f g h j k l _ '".split();
row3 = "_ z x c v b n m , . _".split();
keyboard = [row1,row2,row3];

# This will simply add all your characters from the keyboard into a global array.
globalChars = "";
for row in keyboard:
	for c in row:
		if (c != "_"):
			globalChars += c;

print "INITIALIZATION COMPLETE";

# Run our main code!
string = "";
while (string != "_quit"):
	string = raw_input("Enter string to generate suggestions for, or enter '_quit' to exit: ");

	print "STARTING, string is \""+string+"\"...";
	start = time.time();

	possibilities = get_suggestions(string,keyboard);

	print "TIME SPENT (Generating Suggestions):\t"+str(round(time.time() - start,6));

	print len(possibilities),"possibilites, showing top 10:";
	for p in possibilities[0:10]:
		print "\t",p[0];

