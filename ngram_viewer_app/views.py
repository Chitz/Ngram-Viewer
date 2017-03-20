from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
from django.http import HttpResponse
from datetime import datetime
from os import listdir, getcwd, path
from constants import ALPHANUMERIC, NGRAMS, FULL_STOP_DELIMITER, CORPUS_BASE_PATH
from graphos.renderers import gchart
from graphos.sources.simple import SimpleDataSource

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
        self.isEnd = False
        self.trieGram = None
        self.yearMap = dict()
        self.yearWordCount = dict()

class TernarySearchTree:
    root = None

    def insert(self, word, year, yearWordCount):
        self.root = self.insert_TST(self.root, word, year, yearWordCount)

    def insert_TST(self, root, word, year, totalWordCount):
        if root is None:
            root = TSTNode(word[0][0])
        if root.data > word[0][0]:
            root.left = self.insert_TST(root.left, word, year, totalWordCount)
        elif root.data < word[0][0]:
            root.right = self.insert_TST(root.right, word, year, totalWordCount)
        else:
            if len(word[0]) == 1:
                root.isEnd = True
                # map of year and count freq
                root.yearMap[year] = root.yearMap.setdefault(year, 0) + 1
                root.yearWordCount[year] = totalWordCount
                # generate Trie at this node
                if len(word) > 1:
                    if root.trieGram is None:
                        root.trieGram = Trie()
                    root.trieGram.insert(root.trieGram.root, word[1:],year, totalWordCount)
            else:
                root.eq = self.insert_TST(root.eq, [word[0][1:]] + word[1:], year, totalWordCount)
        return root

    def search(self, root, word):

        if root is None:
            return False, None

        if root.data > word[0][0]:
            return self.search(root.left, word)
        elif root.data < word[0][0]:
            return self.search(root.right, word)
        else:
            if len(word[0]) == 1:
                if root.isEnd:
                    if len(word) > 1:
                        if root.trieGram is None:
                            return False, (None, None)
                        return root.trieGram.search(root.trieGram.root, word[1:])
                    else:
                        return True, (root.yearMap, root.yearWordCount)
                else:
                    return False, None
            else:
                return self.search(root.eq, [word[0][1:]] + word[1:])

class TrieNode:
    def __init__(self, data):
        self.data = data
        self.isEnd = False
        self.yearMap = dict()
        self.yearWordCount = dict()
        self.child = dict()

class Trie:
    root = None

    def insert(self, root, words, year, totalWordCount):
        if root is None:
            root = TrieNode(words[0][0])
        _root = root
        for word in words:
            for char in word:
                if ord(char) not in root.child:
                    root.child[ord(char)] = TrieNode(char)
                root = root.child[ord(char)]
            root.isEnd = True
            root.yearMap[year] = root.yearMap.setdefault(year, 0) + 1
            root.yearWordCount[year] = totalWordCount
        self.root = _root

    def search(self, root, words):
        if root is None:
            return False, None

        for word in words:
            for char in word:
                if ord(char) not in root.child:
                    return False, None
                root = root.child[ord(char)]
        if root is not None and root.isEnd:
            return True, (root.yearMap, root.yearWordCount)

        return False, None

def filterWord(word):
    mod_word = ""
    mod_words = []
    for c in word:
        if c not in ALPHANUMERIC:
            mod_word += c
        else:
            if len(mod_word):
                mod_words.append(str(mod_word.lower()))
            mod_word = ""
    if len(mod_word):
        mod_words.append(str(mod_word.lower()))
    return mod_words

def splitNgrams(words):
    if len(words) < NGRAMS:
        return words
    ngramWordList = [words[i:i+NGRAMS] for i in xrange(len(words))]
    return ngramWordList

def get_text(filePath):
    # make a dictionary and store the word frequencies
    wordList = []
    with open(filePath, 'r') as f:
        while not '*** START' in f.next():
            pass
        line = f.next()
        sentence = ""
        while not '*** END' in line:
            # call filter word
            if '.' in line:
                sentence += line.split(FULL_STOP_DELIMITER)[0]
                _wordList = []
                for word in sentence.split():
                    _wordList.extend(filterWord(word))
                wordList.extend(splitNgrams(_wordList))
                sentence = "".join(line.split(FULL_STOP_DELIMITER)[1:])
                # split in group of NGRAM (5 in this case) words
            else:
                sentence += line
            line = f.next()
    return wordList

def process_corpus(ternarySearchTree):
    basePath = CORPUS_BASE_PATH
    years = []
    for dirName in listdir(basePath):
        dirPath = path.join(basePath, dirName)
        if path.isdir(dirPath):
            years.append(int(dirName))
    for year in years:
        print "### Processing for year", year
        print
        dirPath = path.join(basePath, str(year))
        wordList = []
        for text in listdir(dirPath):
            print "#### Processing Corpa", text
            wordList.extend(get_text(path.join(dirPath, text)))

        totalWordCount = len(wordList)
        print
        print "###### Total Word Count For Year", year, totalWordCount
        for words in wordList:
            ternarySearchTree.insert(words, year, totalWordCount)
        print

start = datetime.now()
ternarySearchTree = TernarySearchTree()
process_corpus(ternarySearchTree)
end = datetime.now()
print "##### Time taken to process corpus", end-start

def processResult(ngram_queries, start, end):
    start = int(str(start))
    end = int(str(end))
    distribution = dict()
    header = ['Year']
    data = [[str(start + i)] + [0] * len(ngram_queries.split(',')) for i in xrange(end - start + 1)]
    counter = 0
    for ngram_query in ngram_queries.split(','):
        ngram_query = str(ngram_query).lower()
        header.append(ngram_query)
        distribution[ngram_query] = dict()
        isFound, result = ternarySearchTree.search(ternarySearchTree.root, ngram_query.split())
        #print isFound, result
        if isFound:
            yearMap, yearWordCount = result
            for year in yearMap:
                if start <= year <= end:
                    nGramWordCount = yearWordCount[year]/len(ngram_query)
                    dist = round(yearMap[year] / (nGramWordCount * 1.0), 7)
                    distribution[str(ngram_query)][year] = (yearMap[year], nGramWordCount,
                                                            dist)
                    data[year - start][counter + 1] = dist
        counter += 1
    data.insert(0, header)
    return distribution, data

def get(request):
    context = dict()
    showResult = False
    if len(request.GET) == 3:
        ngram_query  = request.GET['ngram_query']
        start = request.GET['start']
        end = request.GET['end']
        showResult = True
        result, data = processResult(ngram_query, start, end)
        g_chart = gchart.LineChart(SimpleDataSource(data=data), options={'title': 'Ngram Viewer'})
        context = {'ngram_query': ngram_query, 'start': start, 'end': end, 'result': result}
        context['g_chart'] = g_chart
    context['showResult'] = showResult
    return render(request, 'index.html', context)
