import re
import sys
import bisect

RE_TAB = re.compile('\t')
ROOT_TAG = "@#r$%"
BLANK_FIELD = '_'

class TSVReader:
    def __init__(self, form=-1, lemma=-1, pos=-1, feats=-1, dhead=-1, deprel=-1):
        self.form   = form
        self.lemma  = lemma
        self.pos    = pos
        self.feats  = feats
        self.dhead  = dhead
        self.deprel = deprel

    def __iter__(self):
        return self

    def open(self, fin):
        self.fin = fin

    def close(self):
        if self.fin: self.fin.close()

    def next(self):
        list = []

        for line in self.fin:
            line = line.strip()

            if not line:
                if not list: continue
                break

            list.append(RE_TAB.split(line))

        if list: return self.toNodeList(list)
        else: raise StopIteration

    def toNodeList(self, list):
        nodes = [NLPNode()]
        for i,values in enumerate(list): nodes.append(self.create(i+1, values))

        if self.dhead >= 0:
            for i,values in enumerate(list): self.initDependencyHead(i+1, values, nodes)

        return nodes

    def create(self, id, values):
        f = l = p = t = None
        if self.form  >= 0: f = values[self.form]
        if self.lemma >= 0: l = values[self.lemma]
        if self.pos   >= 0: p = values[self.pos]
        if self.feats >= 0: t = values[self.feats]
        return NLPNode(id, f, l, p, t)

    def initDependencyHead(self, id, values, nodes):
        headID = int(values[self.dhead])
        nodes[id].setDependencyHead(nodes[headID], values[self.deprel])

class NLPNode:
    def __init__(self, id=0, form=ROOT_TAG, lemma=ROOT_TAG, pos=ROOT_TAG, feats=BLANK_FIELD, dhead=None, deprel=None):
        self.id                 = id
        self.word_form          = form
        self.lemma              = lemma
        self.part_of_speech_tag = pos
        self.feats              = feats
        self.dependency_head    = dhead
        self.dependency_label   = deprel
        self.dependent_list     = []

    def __gt__(self, other):
        return self.id > other.id

    def __str__(self):
        l = [str(self.id), self.word_form, self.lemma, self.part_of_speech_tag, str(self.feats)]

        if self.dependency_head:
            l.append(str(self.dependency_head.id))
            l.append(self.dependency_label)

        return '\t'.join(l)

#   ==================== GETTERS ====================

    def getWordForm(self):
        return self.word_form

    def getLemma(self):
        return self.lemma

    def getPartOfSpeechTag(self):
        return self.part_of_speech_tag

    def getDependencyHead(self):
        return self.dependency_head

    def getDependencyLabel(self):
        return self.dependency_label

    def getDependentList(self):
        return self.dependent_list

    def getSubNodeList(self):
        list = []
        self.getSubNodeListAux(self, list)
        list.sort()
        return list

    def getSubNodeListAux(self, node, list):
        list.append(node)

        for child in node.getDependentList():
            self.getSubNodeListAux(child, list)

#   ==================== SETTERS ====================

    def setWordForm(self, form):
        self.word_form = form

    def setLemma(self, lemma):
        self.lemma = lemma

    def setPartOfSpeechTag(self, tag):
        self.part_of_speech_tag = tag

    def setDependencyHead(self, node, label=None):
        if self.dependency_head != None:
            self.dependency_head.dependent_list.remove(self)

        if node != None:
            bisect.insort(node.dependent_list, self)

        self.dependency_head = node
        self.setDependencyLabel(label)

    def setDependencyLabel(self, label):
        self.dependency_label = label


# code to print in pretty colors src: http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python

# def toRed(prt): return "\033[91m{}\033[00m" .format(prt)
# def toGreen(prt): return "\033[92m{}\033[00m" .format(prt)
# def toYellow(prt): return "\033[93m{}\033[00m" .format(prt)
# def toPurple(prt): return "\033[94m{}\033[00m" .format(prt)
# def toCyan(prt): return "\033[96m{}\033[00m" .format(prt)


filename = sys.argv[1]
reader = TSVReader(1,2,3,4,5,6)
reader.open(open(filename))

# set q == to the search term

if len(sys.argv) > 2:
    q = sys.argv[2].lower()

summarize = False

if len(sys.argv) > 3:
    if sys.argv[3].lower() == "-s":
        summarize = True

# find first occurance of q, get the lemma, store q as the lemma

lemmas = dict()

for nodes in reader:
    for i in range(1,len(nodes)):
        node = nodes[i] # node is a word

        if node.word_form.lower() == q:

            if node.lemma not in lemmas:
                lemmas[node.lemma] = 0

            lemmas[node.lemma] += 1

            break

# lemmas now includes a tally of all possible lemmas the word can be.

count = 0

for l in lemmas.items():
    if (l[1] > count): q = l[0]

# q is now == to the lemma that occured the most

reader = TSVReader(1,2,3,4,5,6)
reader.open(open(filename))

relevantNodes = list()

#convenient node to sentance func

def nodesToSentance(nodes, cutoff = 1):
    s = ""

    for i in range(cutoff,len(nodes)):
        node = nodes[i]

        word = " " + node.word_form
        
        if node.dependency_label == "punct" or node.dependency_label == "case":
            word = word.strip()

        if node.lemma == q: 
            s += word #toGreen(word)
        else:
            s += word

    return s.strip()

for nodes in reader:

    relevant = False

    for i in range(1,len(nodes)):
        node = nodes[i] # node is a word
        if node.lemma == q:
            relevant = True
            break

    if relevant:


        if not summarize:
            print nodesToSentance(nodes)
        else:
            relevantNodes += [nodes[1:]] # remove the weird @#r$% stuff

# if no -s, we are done here

if not summarize:
    sys.exit()

# assign a score (# of occurences) to each noun

nounScores = dict()

for nodes in relevantNodes:
    for n in nodes:
        if n.word_form.lower() != q:

            if n.part_of_speech_tag[0:2] == "NN":
                if n.lemma not in nounScores:
                    nounScores[n.lemma] = 0

                nounScores[n.lemma] += 1

sentancesWithScores = list()

sentanceScores = list()

# assign each sentance a score. score == sum of noun scores + the distance from the sentance to the last occurence of a sentance with q in it

for i,nodes in enumerate(relevantNodes):

    nounScore = 0
    positionScore = len(relevantNodes) - i

    for n in nodes:
        if n.lemma in nounScores:
            nounScore += nounScores[n.lemma]

    score = nounScore*positionScore

    sentancesWithScores += [(nodesToSentance(nodes,0),score)]

    sentanceScores += [nounScore*positionScore]

#########

summaryLength = 5

if len(sys.argv) > 4:
    l = int(sys.argv[4])
    if l > 0:
        summaryLength = l


sentanceScores.sort()

summaryLength = min(summaryLength, len(sentancesWithScores))

thresh = sentanceScores[summaryLength*-1]

count = 0

for s in sentancesWithScores:
    if s[1] >= thresh:
        print count+1, "- " + s[0]

        count += 1
        if count >= summaryLength:
            break










