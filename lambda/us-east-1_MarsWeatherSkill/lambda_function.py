# -*- coding: utf-8 -*-

import logging
import os
import ask_sdk_core.utils as ask_utils
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MarsWeatherIntentHandler(AbstractRequestHandler):
    """Handler for both the launch intent and the TiempoMarteIntent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input) or ask_utils.is_intent_name(
            "MarsWeatherIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logging.info("Calling the api")

        nasa_api = os.environ["nasa_api"]
        web = "https://api.nasa.gov/insight_weather/?api_key={api}&feedtype=json&ver=1.0".format(api=nasa_api)
        response = requests.get(web)

        if response.status_code != 200:
            speak_output = ["I can't connect with the NASA webpage to check the official weather"]
        else:
            # Deserialize json
            response = response.json()

            target_sol = max([int(i) for i in response["sol_keys"]])

            sol_info = response[str(target_sol)]

            temperature_celsius = int(sol_info["AT"]["av"])
            temperature_fahrenheit = int(temperature_celsius * (9 / 5) + 32)
            wind = int(sol_info["HWS"]["av"])

            season = sol_info["Season"]

            comment = ""
            if int(temperature_fahrenheit) < 50:
                comment = "I recommend you wearing a coat if you go to Mars."

            speak_output = """There are {} fahrenheit degrees.
            The wind is {} kilometers per hour and the season is {}. This data was registered today by the NASA in 
            Elysium Planitiae.
            {}
            """.format(str(temperature_fahrenheit), str(wind), str(season), comment)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = """The meteorologic data was retrieved from the official page of NASA.
        The data is obtained in Mars every day by a rover in the region Elysium Planitia.
        Data is updated every 24 hours and it is official."""

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("You can ask me about Mars Weather, check it!")
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Bye, ¡Have a nice day on earth!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I couldn't understand what you said, can you repeat it again?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("You can try to ask me about Mars Weather")
                .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(MarsWeatherIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())
# IntentReflectorHandler must be the last one so that it does not overwrite my handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
