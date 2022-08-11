import re
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import SliderForm, WordForm
import random


# Create your views here.
def homePage(request):  # view for the home page
    # get amount of consonants on the slider, default - 20
    cntCons = request.session.get('cntCons', 20)
    # save this amount
    request.session['cntCons'] = cntCons

    # get amount of vowels on the slider, default - 10
    cntVowe = request.session.get('cntVowe', 10)
    # save this amount
    request.session['cntVowe'] = cntVowe

    # display html page
    return render(request, 'abcMuse/homePage.html', {'cntCons': cntCons, 'cntVowe': cntVowe})


def playingField(request):  # view for playing field
    # if this is a GET (or any other) request we need to create two random arrays
    if request.method == "GET":
        # create a form instance and populate it with data from the request
        form = SliderForm(request.GET)
        if form.is_valid():  # if we came here from the main page, update sliders' values
            # get the slider number of consonants and slider number of vowels
            cons = form.cleaned_data['consonants']
            vowe = form.cleaned_data['vowels']
            # save these numbers - when the main page will be opened, it'll have last submitted numbers
            request.session['cntCons'] = cons
            request.session['cntVowe'] = vowe
        # get number of consonants and slider number of vowels , default - 20 and 10
        cons = request.session.get('cntCons', 20)
        vowe = request.session.get('cntVowe', 10)
        # create array for consonants
        c = [0 for _ in range(21)]
        for i in range(cons):
            index = random.randint(0, 20)
            c[index] += 1

        # create array for vowels
        v = [0 for _ in range(5)]
        for i in range(vowe):
            index = random.randint(0, 4)
            v[index] += 1

        # display html page
        return render(request, 'abcMuse/playingField.html', {'B': c[0], 'C': c[1], 'D': c[2], 'F': c[3],
                                                             'G': c[4], 'H': c[5], 'J': c[6], 'K': c[7],
                                                             'L': c[8], 'M': c[9], 'N': c[10], 'P': c[11],
                                                             'Q': c[12], 'R': c[13], 'S': c[14], 'T': c[15],
                                                             'V': c[16], 'W': c[17], 'X': c[18], 'Y': c[19],
                                                             'Z': c[20], 'A': v[0], 'E': v[1], 'I': v[2],
                                                             'O': v[3], 'U': v[4], 'score': 0,
                                                             'recognised': ""})
    else:  # if this is a POST request
        # using uncleaned data, because we should only come here after GET request to the same page

        # get arrays c (consonants) and v (vowels) - in strings for the start
        alphaCons = request.POST.get('alphaCons')
        alphaVowe = request.POST.get('alphaVowe')
        # get current score
        score = int(request.POST.get('score'))
        # get string of recognised words
        recognised = request.POST.get('recognised')

        line = ""  # initially there are no lines from "Hamlet" with player's words

        # convert string array to array for both c and v
        c = [int(elem) for elem in alphaCons.split()]
        v = [int(elem) for elem in alphaVowe.split()]

        # create a form instance and populate it with data from the request
        form = WordForm(request.POST)
        if form.is_valid():  # if form (text in input) is valid
            text = form.cleaned_data['words']
            text = text.lower()  # cast to lowercase
            words = text.split()  # split text into separate words
            wordsNumber = words.__len__()

            allWords = request.session.get('allWords', [])  # get list of all valid words, [] - default
            if not allWords:  # if default - than the file isn't open yet
                openWordFiles(request)  # open files
                assignIndexes("bcdfghjklmnpqrstvwxyz", "aeiou", request)
                allWords = request.session.get('allWords', [])  # get list of all words again - now it's valid
            allWords = set(allWords)  # cast list to set for faster implementation

            length = request.session.get('lengthHamlet')  # get the number of lines in "Hamlet" file

            # array for counting the number player's of words in each "Hamlet line
            request.session['count'] = [0 for _ in range(length)]
            for word in words:  # check each word
                if word in allWords:  # if it is valid
                    if wordsNumber > 1:  # if the players entered more than one word
                        check(word, request)  # check "Hamlet" for this word
                    if recognised == "":  # if it's the first word
                        recognised += word  # just add
                    else:  # otherwise
                        recognised += ", " + word  # add comma then this word
                    score = adjust(word, c, v, score, request)  # update score
            count = request.session.get('count')
            hamlet = request.session.get('Hamlet')

            line = "no line has been found"  # set line value to default
            if score <= 0:  # set line value if score isn't positive
                line = "your score isn't positive!"
            if wordsNumber < 2:  # set line value if one or no words at all have been entered
                line = "not enough words were entered"

            # find a string with maximum number of words in it
            maximum = max(count)
            if score > 0 and maximum > 1:  # (only if score is positive and
                # there is at least one line with at least two player's words in it)
                for i in range(length):
                    if count[i] == maximum:
                        line = hamlet[i]

        else:  # otherwise - if input isn't valid
            messages.error(request, 'Error')  # set error message
        # display html page
        return render(request, 'abcMuse/playingField.html', {'B': c[0], 'C': c[1], 'D': c[2], 'F': c[3],
                                                             'G': c[4], 'H': c[5], 'J': c[6], 'K': c[7],
                                                             'L': c[8], 'M': c[9], 'N': c[10], 'P': c[11],
                                                             'Q': c[12], 'R': c[13], 'S': c[14], 'T': c[15],
                                                             'V': c[16], 'W': c[17], 'X': c[18], 'Y': c[19],
                                                             'Z': c[20], 'A': v[0], 'E': v[1], 'I': v[2],
                                                             'O': v[3], 'U': v[4], 'score': score,
                                                             'recognised': recognised, 'line': line})


def openWordFiles(request):  # open file with valid words, open file with "Hamlet" tragedy, save info
    f = open('abcMuse/templates/abcMuse/popular_words.txt', 'r')
    request.session['allWords'] = f.read().split()

    f = open('abcMuse/templates/abcMuse/hamlet.txt', 'r')
    hamlet = f.read().split('\n')
    request.session['Hamlet'] = hamlet
    request.session['lengthHamlet'] = hamlet.__len__()


def assignIndexes(consonants, vowels, request):  # assign each consonant and vowel an index
    consIndexes = {}
    voweIndexes = {}

    for i in range(21):
        consIndexes[consonants[i]] = i
    for i in range(5):
        voweIndexes[vowels[i]] = i

    # save dictionaries with indexes
    request.session['consIndexes'] = consIndexes
    request.session['voweIndexes'] = voweIndexes


def check(word, request):  # try to find current word in "Hamlet" lines
    hamlet = request.session.get('Hamlet')
    count = request.session.get('count')
    i = 0
    for line in hamlet:  # check each line
        line = line.lower()  # cast to lowercase
        line = re.sub(r'[^\w\s]', ' ', line)  # replace all punctuation marks by a space
        if word in line.split():  # if word in line words
            count[i] += 1  # then update number for this line
        i += 1
    request.session['count'] = count  # save count in current session


def adjust(word, c, v, score, request):  # adjust score according to the word
    #  get indexes
    consIndexes = request.session.get('consIndexes', {})
    voweIndexes = request.session.get('voweIndexes', {})

    vowels = set('aeiou')  # set of vowels
    for element in word:  # run over each element in word
        if element in vowels:  # if this element is a vowels
            if v[voweIndexes[element]] > 0:  # if there are elements like this left
                v[voweIndexes[element]] -= 1
                score += 1  # add score
            else:  # otherwise
                score -= 1  # reduce score
        else:  # otherwise (if element is a consonant)
            if c[consIndexes[element]] > 0:  # if there are elements like this left
                c[consIndexes[element]] -= 1
                score += 1  # add score
            else:
                score -= 1  # reduce score
    return score  # return changed score
