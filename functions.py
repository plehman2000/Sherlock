import spacy
import requests
import spacy
import openai
from youtube_transcript_api import YouTubeTranscriptApi




nlp = spacy.load('en_core_web_lg')

openai.organization = "org-xYSZAaZqytg7EQ0juDkS4z5D"
openai.api_key = "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"

def get_ents(text):
    #show entities in text
    exclusionList = ['PERSON', 'TIME', 'DATE', 'CARDINAL', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'PRODUCT', 'NORP']
    doc = nlp(text)
    entities = []
    if doc.ents:
        for ent in doc.ents:
            if ent.label_  in exclusionList:
                pass
            else:
                entities.append([ent.text, ent.label_])
 
    if entities:
        return entities
    else:
        return 0
    

def stampsToEnts(srt):
    #associate time stamps with entities
    stampList = []
    for dict in srt:
        stampList.append([dict['text'], dict['start']])

    entList = []
    for text, start in stampList:
        entList.append([get_ents(text), start])

    #return entList

    entStamped = []
    for ents, time in entList:
        if ents != 0:
            entStamped.append([ents, time])
    return entStamped

def creatEntityDefinitions(ents):
    #given entity list from stampsToEnts, returns a dictionary with keywords and their 1 sentence wikipedia definitions
    ent_dict = {}
    for ent_list, _ in ents:
        for ent in ent_list:
            if ent[0] in ent_dict:
                pass
            else:
                ent_dict[ent[0]] = wikiExplainer(ent[0], False, 1)

    return ent_dict


def getFullScript(srt):
    #turn timestamped transcript into string
    script = ""
    for dictionary in srt:
       # print(dictionary)
        script += dictionary['text'] + " "
    return script


def getTranscriptFromURL(vidcode):
    #gets timestamped transcript from URL
    vidcode = vidcode[vidcode.find('v='):][2:]
    if (vidcode[vidcode.find('&t')]):
        vidcode = vidcode.split('&')[0]
        try:
            srt = YouTubeTranscriptApi.get_transcript(vidcode)
            return srt
        except:
            return -1
    

def getSummary(textList, engineChoice=0, sentences_per_chunk=4):
    #Summarizes list of strings using openai api
    #Running this function costs me money so please don't unless necessary for testing/compatibility purposes - Patrick
    engineChoices = ['text-davinci-001', 'text-curie-001']
    summaries = []
    for text_to_summarize in textList: 
        #sentence_amount = int(len(text_to_summarize.split()) / (3*15))
        text_to_summarize = text_to_summarize + "." #to prevent period at the start of output
        if (sentences_per_chunk * 32) > 2049:
            token_amount = 2049 
        else:
            token_amount = sentences_per_chunk * 20
        #return [f"Summarize this for a second-grade student and write only {sentence_amount} sentences:\n" + text_to_summarize, token_amount]
        comp =  openai.Completion.create(
        engine=engineChoices[engineChoice],
        prompt=f"Summarize this for a second-grade student and write only {sentences_per_chunk} sentences:\n" + text_to_summarize,
        max_tokens=token_amount,
        temperature=0.5
        )
        summaries.append((comp.choices[0]['text']).replace('\n', ""))
    return summaries
    
def splitTranscript(script_string, limit=910):
    #Splits transcripts string into list of chunks of length 'limit
    tokenCount = len(script_string.split(' '))
    numSplits = int(tokenCount/limit)
    transcript_list = []

    splitString = script_string.split(' ')
    #print(numSplits)
    #print(f'splitstring: {splitString}')
    ind = 0
    for ind in range(0,numSplits*limit, limit):
        if ind != numSplits:
            script = splitString[ind:ind+limit]
            #print(script)
            transcript_list.append(  ' '.join(script))
        else:
            break
    last_slice = splitString[ind+limit:]
    last_script = ' '.join(last_slice )
    transcript_list.append(last_script)
    return transcript_list


def getSummaryFromTranscript(transcript, token_limit=896):
    #Running this function costs me money so please don't unless necessary for testing/compatibility purposes - Patrick
    script_string = [getFullScript(transcript)]
    if len(script_string[0].split(' ')) > token_limit:
        script_string = splitTranscript(script_string[0], token_limit)

    summary = getSummary(script_string)
    return summary


def wikiExplainer(title, removeEscapeChars=True, explainerLength=3):
    
    response = requests.get(
         'https://en.wikipedia.org/w/api.php',
         params={
             'action': 'query',
             'format': 'json',
             'titles': title,
             'prop': 'extracts',
             'exintro': True,
             'explaintext': True,
         }).json()
    response = requests.get("https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exlimit=max&explaintext&exintro&titles=" + title.replace(" ", "_") + "|" + title.replace(" ", "_") + "&redirects=").json()
    explainer = next(iter(response['query']['pages'].values()))
    if 'extract' in explainer:
        explainer = explainer['extract']
        if removeEscapeChars:
            explainer = ''.join(c for c in explainer if c.isalnum() or c==' ')
            explainer = explainer.replace("\n", " ")
    else:
        explainer = ""


    doc = nlp(explainer)
    explainer = ""
    for j,sentence in enumerate(doc.sents):
        if(j+1 > explainerLength):
            break
        else:
            explainer += str(sentence.text) + " "
    return explainer
