import urllib2
import json
import random

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
    
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    
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
    return get_story()
 

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    # Dispatch to your skill's intent handlers
    if intent_name == "StoryTeller":
        return get_icebreaker_story(intent, session)
    else:
        raise ValueError("Invalid intent")
 

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


#store mp3 on s3 with a suffix 0-5 to get random samples
def getUrl():
    #return "https://s3.amazon.com/gwc/sample_" + random.randint(0, 5) + ".mp3"
    return "https://s3.amazonaws.com/audible-girls-who-code/dreamhouse2.mp3"

def get_icebreaker_story(intent, session):
    
    url = getUrl()
    output = "<speak> Girls who code welcome to Audible. Here is the story you requested:  <break time=\"1s\"/> <audio src=\""  + url + "\"/>  </speak>" 
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = 'Please ask me to tell a story'
   
    return build_response(session_attributes, build_speechlet_response(
          card_title, output, reprompt_text, should_end_session))
  

def get_story(intent, session):
    asin = 'B0118CYHCK'   #TODO: get random ASIN
    
    url = 'https://api.audible.com/1.0/catalog/products/' + asin + '?response_groups=sample'
    response = urllib2.urlopen(url)
    data = json.load(response)
    offset = 10000;
    sample_url = data['product']['sample_url']
    
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = 'Please ask me to tell a story'
   
    return build_response(session_attributes, build_audioplayer_speechlet_response(
          card_title, reprompt_text, should_end_session, sample_url, offset))

# --------------- Helpers that build all of the responses ----------------------
# ADD AudioPlayer here

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_audioplayer_speechlet_response(title, reprompt_text, should_end_session, audioURL, offset):
    return {
        'directives': [ {
           'type': 'AudioPlayer.Play',
           'playBehavior': 'REPLACE_ALL', #Setting to REPLACE_ALL means that this track will start playing immediately
           'audioItem': {
                'stream': {
                    'url': audioURL,
                    'token': "0", #Unique token for the track - needed when queueing multiple tracks
                    'expectedPreviousToken': None, # The expected previous token - when using queues, ensures safety
                    'offsetInMilliseconds': offset
                }
            }
        }],
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + 'Test'
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
 

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }    
