from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
from django.http import HttpResponse
import datetime
from os import listdir, getcwd, path
#class HomePageView(TemplateView):
#    def __init__(self):
#        self.value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
'''
Looking at the input string there are many punctuations in the stories, avoid them!

Ternary

building a ternary search tree!
'''

# Ternary Search Tree Node
class TSTNode:
    def __init__(self, data):
        self.data = data    # character it stores
        self.left = self.right = self.eq = None
        self.isEnd = True
        self.info = []

def filterWord(word):
    mod_word = ""
    mod_words = []
    for c in word:
        if c not in "\"(),;%$*&#-=.:!":
            mod_word += c
        else:
            mod_words.append(str(mod_word.lower()))
            mod_word = ""
    mod_words.append(str(mod_word.lower()))
    return mod_words

def get_text(filePath):
    # make a dictionary and store the word frequencies
    wordList = []
    with open(filePath, 'r') as f:
        while not '*** START' in f.next():
            pass
        line = f.next()
        while not '*** END' in line:
            wordList.extend(line.split())
            line = f.next()
    return wordList

class TernarySearchTree:
    root = None

    def insert(self, word, year, wordCount, totalWordCount):
        self.root = self.insert_TST(self.root, word, year, wordCount, totalWordCount)

    def insert_TST(self, root, word, year, wordCount, totalWordCount):
        if root is None:
            #print word
            root = TSTNode(word[0])

        if root.data > word[0]:
            root.left = self.insert_TST(root.left, word, year, wordCount, totalWordCount)
        elif root.data < word[0]:
            root.right = self.insert_TST(root.right, word, year, wordCount, totalWordCount)
        else:
            if len(word) == 1:
                root.isEnd = True
                root.info.append((year, wordCount, totalWordCount))
            else:
                root.eq = self.insert_TST(root.eq, word[1:], year, wordCount, totalWordCount)
        return root

    def search(self, root, word):

        if root is None:
            return False

        if root.data > word[0]:
            return self.search(root.left, word)
        elif root.data < word[0]:
            return self.search(root.right, word)
        else:
            if len(word) == 1:
                if root.isEnd:
                    return True, root.info
                else:
                    return False, None
            else:
                return self.search(root.eq, word[1:])

def process_corpus(ternarySearchTree):
    basePath = './task'
    years = []
    for dirName in listdir(basePath):
        dirPath = path.join(basePath, dirName)
        if path.isdir(dirPath):
            years.append(dirName)
    yearWordDict = dict()
    for year in years:
        dirPath = path.join(basePath, year)
        wordList = []
        wordFreq = dict()
        for text in listdir(dirPath):
            wordList.extend(get_text(path.join(dirPath, text)))

        totalWordCount = len(wordList)
        for word in wordList:
            words = filterWord(word)
            for mod_word in words:
                if len(mod_word):
                    wordFreq[mod_word] = wordFreq.setdefault(mod_word, 0) + 1

        for word, count in wordFreq.iteritems():
            ternarySearchTree.insert(word, year, count, totalWordCount)
        #yearWordDict[year] = wordFreq

ternarySearchTree = TernarySearchTree()
process_corpus(ternarySearchTree)

print ternarySearchTree.search(ternarySearchTree.root, "supreme")

def get(request):
    context = None
    if len(request.GET) == 3:
        ngram_query = request.GET['ngram_query']
        start = request.GET['start']
        end = request.GET['end']
        context = {'ngram_query': ngram_query, 'start': start, 'end': end}
    return render(request, 'index.html', context)
