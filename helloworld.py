import urllib2
import json
import random

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
   
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
    
    #if event['session']['new']:
    #    on_session_started({'requestId': event['request']['requestId']},
    #                       event['session'])
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])
 

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_icebreaker_story()
 

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    print("intent" + intent_name)
    # Dispatch to your skill's intent handlers
    if intent_name == "StoryTeller":
        return get_story(intent, session)
    elif intent_name == "AMAZON.StopIntent":
        return on_session_ended(intent, session)
    elif intent_name == "AMAZON.PauseIntent":
        return on_session_ended(intent, session)       
    else:
        raise ValueError("Invalid intent")
   
#This is the function we will focus on    
def get_story(intent, session):
    asin = 'B0118CYHCK'   #TODO: get random ASIN    
    url = 'https://api.audible.com/1.0/catalog/products/' + asin + '?response_groups=sample,product_desc,contributors,product_attrs'
    
    
    # Build up output using SSML 
    # https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/speech-synthesis-markup-language-ssml-reference                          
    output = "<speak>  Hello World </speak>" 
    
    
    session_attributes = {}
    card_title = intent['name']
    reprompt_text = 'Please ask me to tell a story'
    should_end_session = True
   
    return build_response(session_attributes, build_speechlet_response(
          card_title, output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------
def on_session_ended(session_ended_request, session):
    return build_response({}, build_stop_response())

def getSample(data):
    return data['product']['sample_url']
    
def getTitle(data): 
    return data['product']['title']
    
def getBookMetadata(url):
    response =  urllib2.urlopen(url)
    return json.load(response)
    
def getAuthor(data):
    return data['product']['authors'][0]['name']
    
def getSummary(data):
    return data['product']['merchandising_summary']
    
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_audioplayer_speechlet_response(title, reprompt_text, should_end_session, audio_url, offset, output):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'directives': [ {
           'type': 'AudioPlayer.Play',
           'playBehavior': 'REPLACE_ALL', #Setting to REPLACE_ALL means that this track will start playing immediately
           'audioItem': {
                'stream': {
                    'url': audio_url,
                    'token': "0", #Unique token for the track - needed when queueing multiple tracks
                    'offsetInMilliseconds': offset
                }
            }
        }],
        'shouldEndSession': should_end_session
    }
    
def build_stop_response():
    return {
        
        'directives': [ {
           "type": "AudioPlayer.ClearQueue",
           "clearBehavior" : "CLEAR_ALL"
           
        }],
        'shouldEndSession': True
    }    
 

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    
def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print k
                dumpclean(v)
            else:
                print '%s : %s' % (k, v)
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print v
    else:
        print obj    
    
