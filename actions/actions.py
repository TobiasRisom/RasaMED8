# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from rasa.core.actions.forms import FormAction

# This is a simple example for a custom action which utters "Hello World!"

from actions.utils import plot_handler
from actions.utils import predictions
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

# SOCKET = sockets.Socket()
NEWPATIENTDATA = predictions.new_patient_features
PLOT_HANDLER = plot_handler.PlotHandler()
ALLOWED_PLOT_TYPES = ["line", "bar", "pie", "barh"]
ALLOWED_SELECTED_VALUES = ["age", "gender", "hospital_stroke", "hospitalized_in", "department_type", "stroke_type",
                           "nihss_score", "thrombolysis", "no_thrombolysis_reason", "door_to_needle", "door_to_imaging",
                           "onset_to_door", "imaging_done", "imaging_type", "dysphagia_screening_type",
                           "before_onset_antidiabetics", "before_onset_cilostazol", "before_onset_clopidrogel",
                           "before_onset_ticagrelor", "before_onset_ticlopidine", "before_onset_prasugrel",
                           "before_onset_dipyridamol", "before_onset_warfarin", "risk_hypertension", "risk_diabetes",
                           "risk_hyperlipidemia", "risk_congestive_heart_failure", "risk_smoker",
                           "risk_previous_ischemic_stroke", "risk_previous_hemorrhagic_stroke",
                           "risk_coronary_artery_disease_or_myocardial_infarction", "risk_hiv", "bleeding_source",
                           "discharge_mrs", "discharge_nihss_score", "three_m_mrs", "covid_test",
                           "physiotherapy_start_within_3days", "occup_physiotherapy_received", "glucose", "cholesterol",
                           "sys_blood_pressure", "dis_blood_pressure", "perfusion_core", "hypoperfusion_core",
                           "stroke_mimics_diagnosis", "prestroke_mrs", "tici_score", "prenotification", "ich_score",
                           "hunt_hess_score"]
ALLOWED_COLORS = ["red", "green", "blue"]
ALLOWED_AXIS = ["x-axis", "y-axis"]
ALLOWED_YEARS = ["all", "2018", "2019", "2020", "2021","2022","2023"]
ALLOWED_FAKEIDS = ["imafakepatient"]
def sendFPData():
    for key, value in NEWPATIENTDATA.items():
        PLOT_HANDLER.change_arg("FakePatient_"+str(key), value)

    response = PLOT_HANDLER.send_args()
    response = PLOT_HANDLER.edit_data()

class ActionGreeting(Action):

    def name(self) -> Text:
        return "ActionHelloWorld"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Hi! I am Rasa, a chatbot designed to help you sort through patient data!")
        dispatcher.utter_message(text="Here is a list of actions I can perform:")
        dispatcher.utter_message(text="- Spiders")
        dispatcher.utter_message(text="- Spiders")
        dispatcher.utter_message(text="- Spiders")

        return []
class ActionChangePlottype(Action):

    def name(self) -> Text:
        return "action_change_plottype"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        plot_type = tracker.get_slot("plot_type")

        print(plot_type)

        if plot_type:
            if plot_type.lower() not in ALLOWED_PLOT_TYPES:
                dispatcher.utter_message(text=f"Sorry, I can only create {'/'.join(ALLOWED_PLOT_TYPES)} plots.")
                return {"plot_type": None}
            dispatcher.utter_message(text=f"OK! I will create a {plot_type} plot.")

        PLOT_HANDLER.change_arg("type", plot_type)

        response = PLOT_HANDLER.send_args()
        dispatcher.utter_message(text=f"{response}")

        return []


class ActionChangeColor(Action):
    def name(self) -> Text:
        return "action_change_color"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        color = tracker.get_slot("color")

        print(color)

        if color:
            if color.lower() not in ALLOWED_COLORS:
                dispatcher.utter_message(text=f"Sorry, I can only change the color to {'/'.join(ALLOWED_COLORS)}.")
                return {"color": None}
            dispatcher.utter_message(text=f"OK! The color will be changed to {color}.")

        PLOT_HANDLER.change_arg("color", color)
        PLOT_HANDLER.change_arg("data_type", "comparison") # What type of data do we have? Comparison = Compare X to Y

        response = PLOT_HANDLER.send_args()
        dispatcher.utter_message(text=f"{response}")

        response = PLOT_HANDLER.edit_data()
        dispatcher.utter_message(text=f"{response}")

        return []

class ActionPredictValue(Action):
    def name(self) -> Text:
        return "action_predict_value"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        value = tracker.get_slot("selected_value")
        subject = tracker.get_slot("subject_id")

        if value:
            if value.lower() not in ALLOWED_SELECTED_VALUES:
                dispatcher.utter_message(text=f"Sorry, I don't recognize that value.")
                return {"selected_value": None}

        if subject:
            if subject.lower() != 'iamafakepatient':
                dispatcher.utter_message(text=f"Sorry, I do not recognize the patient id.")
                return {"subject_id": None}

        dispatcher.utter_message(text=f"OK! Predicting {value} for {subject}...")

        PLOT_HANDLER.change_arg("selected_value", value)
        PLOT_HANDLER.change_arg("subject_id", subject)
        PLOT_HANDLER.change_arg("data_type", "shap")  # What type of data do we have? shap = shap values

        prediction_value, feature_list, feature_response = predictions.prediction_and_feature_importance()
        dispatcher.utter_message(text=f"Response from predictions: {feature_response}")  # 200 for success

        response = PLOT_HANDLER.send_args()
        dispatcher.utter_message(text=f"Response from send_args: {response}") # 200 for success

        dispatcher.utter_message(text=f"Prediction is **{prediction_value}** for {value}, {subject}")

        dispatcher.utter_message(text=f"Graph is displaying SHAP values for the 10 most important related features for {value}!")

        return []

class ActionCollectAndShowNewPaitentData(Action):
    #Does not actually show data yet, but does collect it and send it to plot_args.json
    def name(self) -> Text:
        return "action_show_specified_fake_patient"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        fake_patient_id = tracker.get_slot("fake_patient_id")

        print(fake_patient_id)

        if fake_patient_id:
            if fake_patient_id.lower() not in ALLOWED_FAKEIDS:
                dispatcher.utter_message(text=f"Sorry, I can only show the patients with missing data.")
                return {"fake_patient_id": None}
            dispatcher.utter_message(text=f"OK! here is the data for {fake_patient_id}")
            sendFPData()
        return []

class ActionChangeDatabeingShowcased(Action):
    def name(self) -> Text:
        return "action_change_data"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        selected_axis = tracker.get_slot("selected_axis")
        axis_value = tracker.get_slot("selected_value")

        print(selected_axis)
        print(axis_value)

        if axis_value and selected_axis:
            if axis_value.lower() not in ALLOWED_SELECTED_VALUES:
                dispatcher.utter_message(text=f"Sorry, I can only show data point that exist in the datasheet.")
                axis_value = None
                return {"selected_value": None}
            if selected_axis.lower() not in ALLOWED_AXIS:
                dispatcher.utter_message(text=f"Sorry, I can only show data point that exist in the datasheet.")
                selected_axis = None
                return {"selected_axis": None}
            if axis_value and selected_axis:
                dispatcher.utter_message(text=f"Okay, I will show {axis_value} along the {selected_axis}")
                if selected_axis == "x-axis":
                    PLOT_HANDLER.change_arg("x-value", axis_value)
                elif selected_axis == "y-axis":
                    PLOT_HANDLER.change_arg("y-value", axis_value)
                selected_axis = None
                axis_value = None
                return {"selected_value": None, "selected_axis": None}
        elif axis_value and selected_axis is None:
            dispatcher.utter_message(text=f"Okay, which axis should I show {axis_value} along?")
        elif selected_axis and axis_value is None:
            dispatcher.utter_message(text=f"Okay, which data point should I show along the {selected_axis}?")
        return []

class ActionChangeSelectedvalue(Action):

    def name(self) -> Text:
        return "action_change_selectedvalue"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        selected_value = tracker.get_slot("selected_value")

        if selected_value:
            if selected_value.lower() not in ALLOWED_SELECTED_VALUES:
                dispatcher.utter_message(text=f"Sorry, I can only create {'/'.join(ALLOWED_SELECTED_VALUES)} plots.")
                return {"selected_value": None}
            dispatcher.utter_message(text=f"OK! I will create a {selected_value} plot.")

        PLOT_HANDLER.change_arg("variable", selected_value)

        response = PLOT_HANDLER.edit_data()
        dispatcher.utter_message(text=f"{response}")

        return []

class ActionChangeYear(Action):

    def name(self) -> Text:
        return "action_change_year"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        selected_year = tracker.get_slot("year")

        if selected_year:
            if selected_year.lower() not in ALLOWED_SELECTED_VALUES:
                dispatcher.utter_message(text=f"Sorry, I only have data for the following years: {'/'.join(ALLOWED_YEARS)}")
                return {"selected_value": None}
            dispatcher.utter_message(text=f"OK! Year has been changed to {selected_year}.")

        PLOT_HANDLER.change_arg("year", selected_year)

        response = PLOT_HANDLER.edit_data()
        dispatcher.utter_message(text=f"{response}")

        return []

class PrefillSlots(Action):
    def name(self) -> Text:
        return "action_prefill_slots"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Logic to pre-fill slots
        plot_type = "line"

        return [
            SlotSet("plot_type", plot_type)
        ]


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "ActionHelloWorld"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Here is your INFO")

        return []
