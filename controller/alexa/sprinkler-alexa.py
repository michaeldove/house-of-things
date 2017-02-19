from __future__ import print_function
import isodate

TOPIC = 'home/sprinkler'

################################################################################
# IoT Platform Helpers 
################################################################################

def publish_iot(sprinkler_index, enable, duration):
    import boto3
    import json
    client = boto3.client('iot-data')
    payload = json.dumps({'sprinkler_index':sprinkler_index,
                          'sprinkler_enable': enable,
                          'sprinkler_duration': duration})
    client.publish(topic=TOPIC, payload=payload)
    
################################################################################
# Alexa generic speechlet helpers
################################################################################

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
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

def get_slot_value(slots, name):
    if name in slots:
        return slots[name].get('value', None)
    return None

################################################################################
# Skill specific response handling
################################################################################

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes 
    we could add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to my home."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what to control."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Hear from you next time."
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


################################################################################
# Business intent handling
################################################################################

SECONDS_IN_DAY = 86400

def is_valid_duration(duration):
    from datetime import timedelta
    not_gte_day = duration.total_seconds() < SECONDS_IN_DAY
    if not (duration.__class__ is timedelta):
        not_gte_day &= (duration.days + duration.years) == 0
    return not_gte_day

def manual_sprinkler(intent, session):
    session_attributes = session.get('attributes', {})
    card_title = intent['name']
    slots = intent['slots']
    should_end_session = True
    duration_iso = get_slot_value(slots, 'Duration')
    speech_output = None
    if duration_iso:
        duration = isodate.parse_duration(duration_iso) 
        if not is_valid_duration(duration):
            speech_output = "Duration must be less than a day."
        elif duration.total_seconds() == 0:
            speech_output = "Tell me a duration higher than 0 seconds."
        else:
            duration_seconds = int(duration.total_seconds())
            publish_iot(0, 1, duration_seconds)
            speech_output = "I'm turning on your sprinkler for " + str(duration_seconds) + " seconds."
    else:
        speech_output = "Please tell me a valid duration."
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, speech_output, should_end_session))

################################################################################
# Alexa event handling
################################################################################

def on_session_started(session_started_request, session):
    """Called when the session starts"""
    pass

def on_launch(launch_request, session):
    """Called when the user launches the skill without specifying what they
    want
    """
    return get_welcome_response()


def on_intent(intent_request, session):
    """Called when the user specifies an intent for this skill"""
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SprinklerIntent":
        return manual_sprinkler(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    pass


################################################################################
# Lambda entrypoint
################################################################################

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

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
