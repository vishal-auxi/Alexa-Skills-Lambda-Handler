"""
AWS lambda code by end of part 2 of programming alexa series
"""

import requests

# from modules import *

url = ""

ppt_title = ""
ppt_slide_count = -1


# from insults import get_insult


# --------------- Helpers that build all of the responses ----------------------

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


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "What would you like to do today?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I don't know if you heard me, what would you like me to do?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_ppt_response():
    session_attributes = {}
    card_title = "Question"
    speech_output = "Ok. What's the title of the Presentation?"
    reprompt_text = "I would like to know the itle of the Presentation"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_ppt_name(intent, session):
    session_attributes = {}
    card_title = "PPTTitle"

    title = intent['slots']['pptName']['value']
    global ppt_title
    ppt_title = title

    data = {
        "req": "create_ppt",
        "title": title
    }

    success = False
    response = None
    try:
        response = requests.post(url=url, json=data)
        if response.status_code == 200:
            response = response.json()
            success = True
        elif response.status_code == 404:
            success = False
    except Exception as err:
        print(f'Error occurred: {err}')
        success = False

    if success:
        speech_output = "Created a presentation on " + response["title"]
        reprompt_text = "I said presentation on " + response["title"] + " is created"
        should_end_session = False
    else:
        speech_output = "Cannot create a presentation on " + title
        # speech_output = "Okay. How many slides does it have?"
        reprompt_text = "I said I was not able to create a presentation on " + title

        should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_ppt_count_response(intent, session):
    session_attributes = {}
    card_title = "PPTTitle"

    subject = intent['slots']['subject']['value']
    count = intent['slots']['count']['value']

    try:
        source = intent['slots']['source']['value']
        if source.lower() != "wikipedia" and source.lower() != "wiki":
            speech_output = "Cannot create a presentation on " + subject + " using " + source + " as source"
            reprompt_text = "I said I did not create a presentation on " + subject + " using " + source + " as source"
            should_end_session = False
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))
    except Exception as e:
        print("no source in create_ppt_count_response: " + e)

    if intent['confirmationStatus'] == "DENIED":
        speech_output = "Did not create a presentation on" + subject
        reprompt_text = "I said I did not create a presentation on " + subject
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    global ppt_title
    ppt_title = subject

    if int(count) > 0:
        data = {
            "req": "create_ppt_count",
            "title": subject,
            "count": int(count)
        }
    else:
        data = {
            "req": "create_ppt",
            "title": subject
        }

    success = False
    response = None
    try:
        response = requests.post(url=url, json=data)
        if response.status_code == 200:
            response = response.json()
            success = True
        elif response.status_code == 404:
            success = False
    except Exception as err:
        print(f'Error occurred: {err}')
        success = False

    if success:
        speech_output = "Created a presentation of " + str(response["count"]) + " slides on " + response["title"]
        reprompt_text = "I said presentation of " + str(response["count"]) + " slides on " + response[
            "title"] + " is created "
        should_end_session = False
    else:
        speech_output = "Cannot create a presentation on " + subject
        reprompt_text = "I said I was not able to create a presentation on " + subject

        should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_team_slide_response(intent, session):
    session_attributes = {}
    card_title = "TeamSlide"

    data = {
        "req": "create_team_slide",
        "people": []
    }

    try:
        if 'value' in intent['slots']['people']:
            data["people"] = [intent['slots']['people']['value']]
        else:
            input_list = intent['slots']['people']['slotValue']['values']
            people = [i["value"] for i in input_list]
            data["people"] = people
    except Exception as err:
        print(f'Cannot access people: {err}')

    response = requests.post(url=url, json=data)
    response = response.json()
    speech_output = response["message"]
    reprompt_text = "I said " + speech_output
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_pie_chart_response(intent, session):
    session_attributes = {}
    card_title = "PieChart"

    data = {
        "req": "create_pie_chart",
        "categories": [],
        "percentages": []
    }

    try:
        input_categories_list = intent['slots']['categories']['slotValue']['values']
        data["categories"] = [i["value"] for i in input_categories_list]

        input_percentages_list = intent['slots']['percentages']['slotValue']['values']
        data["percentages"] = [i["value"] for i in input_percentages_list]
    except Exception as err:
        print(f'Cannot access people: {err}')

    response = requests.post(url=url, json=data)
    response = response.json()
    speech_output = response["message"]
    reprompt_text = "I said " + speech_output
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_chart_response(intent, session):
    session_attributes = {}
    card_title = "Chart"

    data = {
        "req": "create_pie_chart",
        "categories": [],
        "percentages": [],
        "values": [],
        "title": ""
    }

    try:
        print("***")
        s = intent['slots']
        data["title"] = s['ChartTitle']['value']
        data["categories"] = [s['FirstLabel']['value'], s['SecondLabel']['value'], s['ThirdLabel']['value']]

        if "pie" in s['ChartType']['value'].lower():
            data['req'] = "create_pie_chart"
            data["percentages"] = [s['FirstValue']['value'], s['SecondValue']['value'], s['ThirdValue']['value']]
        elif "bar" in s['ChartType']['value'].lower():
            data['req'] = "create_bar_chart"
            data["values"] = [s['FirstValue']['value'], s['SecondValue']['value'], s['ThirdValue']['value']]

        response = requests.post(url=url, json=data)
        response = response.json()
        speech_output = response["message"]

    except Exception as err:
        print(f'Cannot access slots: {err}')
        speech_output = "Couldn't create the chart due to an error in processing the input"

    reprompt_text = "I said that I " + speech_output
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_org_chart(intent, session):
    session_attributes = {}
    card_title = "OrgSlide"

    data = {
        "req": "create_org_chart",
        "people": []
    }

    try:
        first_level = intent['slots']['FirstLevel']['value']
        second_level = intent['slots']['SecondLevel']['value']

        data["people"] = [first_level.split(), second_level.split()]

    except Exception as err:
        print(f'Cannot access people: {err}')

    response = requests.post(url=url, json=data)
    response = response.json()
    speech_output = response["message"]
    reprompt_text = "I said " + speech_output
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts.
        One possible use of this function is to initialize specific
        variables from a previous state stored in an external database
    """
    # Add additional code here as needed
    pass


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    # Dispatch to your skill's launch message
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "CreatePPTIntent":
        return create_ppt_response()
    elif intent_name == "PPTNameIntent":
        return get_ppt_name(intent, session)
    elif intent_name == "CreatePPTSubjectCountIntent":
        return create_ppt_count_response(intent, session)
    elif intent_name == "CreateTeamSlideIntent":
        return create_team_slide_response(intent, session)
    elif intent_name == "CreatePieChartIntent":
        return create_pie_chart_response(intent, session)
    elif intent_name == "CreateChartIntent":
        return create_chart_response(intent, session)
    elif intent_name == "CreateOrgChartIntent":
        return create_org_chart(intent, session)
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
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("Incoming request...")

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
