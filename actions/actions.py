# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from actions.utils import plot_handler
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

# SOCKET = sockets.Socket()
PLOT_HANDLER = plot_handler.PlotHandler()
ALLOWED_PLOT_TYPES = []
ALLOWED_SELECTED_VALUES = []



class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "ActionHelloWorld"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Here is your info")

        return []

class ValidateCreatePlotForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_create_plot_form"

    def validate(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        plot_type = tracker.get_slot("plot_type")
        selected_value = tracker.get_slot("selected_value")

        if plot_type:
            if plot_type.lower() not in ALLOWED_PLOT_TYPES:
                dispatcher.utter_message(text=f"Sorry, I can only create {'/'.join(ALLOWED_PLOT_TYPES)} plots.")
                return {"plot_type": None}
            dispatcher.utter_message(text=f"OK! I will create a {plot_type} plot.")

        if selected_value:
            if selected_value.lower() not in ALLOWED_SELECTED_VALUES:
                dispatcher.utter_message(text=f"Sorry, I can only show {'/'.join(ALLOWED_SELECTED_VALUES)} values.")
                return {"selected_value": None}
            dispatcher.utter_message(text=f"OK! I will use {selected_value} as the selected value.")

        return {"plot_type": plot_type, "selected_value": selected_value}



