# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
import math

from rasa.core.actions.forms import FormAction

# This is a simple example for a custom action which utters "Hello World!"

from actions.utils import plot_handler
from actions.utils import predictions
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import FollowupAction
import json
from rasa_sdk.types import DomainDict


# SOCKET = sockets.Socket()
NEWPATIENTDATA = predictions.set_patient_variables('patient1')
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
ALLOWED_FAKEIDS = ["patient1", "patient2"]
ALLOWED_HOSPITALS = ["evergreen", "riverside", "vitality", "horizon", "summit", "pineview", "wellspring", "all"]
isActive = True
class ActionChangeStatus(Action):
    def name(self) -> Text:
        return "change_status"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        status = tracker.get_slot("status")

        if status == "passive":
            isActive = False
        elif status == "active":
            isActive = True
        print(isActive)
        dispatcher.utter_message(text=f"Status is now set to {status}")
        PLOT_HANDLER.change_arg("Status", status)
        response = PLOT_HANDLER.send_args()
        return [SlotSet("status", None)]
class ActionGreeting(Action):

    def name(self) -> Text:
        return "action_greeting"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Hi! I am Rasa, a chatbot designed to help you sort through patient data!")
        if isActive:
            dispatcher.utter_message(text="For example, I contain data for both Patient1 and Patient2. You can ask me to show that data!")


        PLOT_HANDLER.change_arg("plot_type", "bar"),
        PLOT_HANDLER.change_arg("color", "blue"),
        PLOT_HANDLER.change_arg("x-value", "X Axis"),
        PLOT_HANDLER.change_arg("y-value", "Y Axis"),
        PLOT_HANDLER.change_arg("selectedAxis", "x-axis"),
        PLOT_HANDLER.change_arg("year", "2019"),
        PLOT_HANDLER.change_arg("selected_value", None),
        PLOT_HANDLER.change_arg("subject_id", None),
        PLOT_HANDLER.change_arg("data_type,", "shap"),
        PLOT_HANDLER.change_arg("hospital", "Riverside")
        PLOT_HANDLER.change_arg("FakePatient_age", None)
        PLOT_HANDLER.change_arg("FakePatient_onset_to_door", None)
        PLOT_HANDLER.change_arg("FakePatient_door_to_imaging", None)
        PLOT_HANDLER.change_arg("FakePatient_door_to_needle", None)
        PLOT_HANDLER.change_arg("FakePatient_prestroke_mrs", None)
        PLOT_HANDLER.change_arg("FakePatient_nihss_score", None)
        PLOT_HANDLER.change_arg("FakePatient_sys_blood_pressure", None)
        PLOT_HANDLER.change_arg("FakePatient_dis_blood_pressure", None)
        PLOT_HANDLER.change_arg("FakePatient_cholestrol", None)

        response = PLOT_HANDLER.send_args()
        print(response)
        #dispatcher.utter_message(text=f"{response}")

        edit_response = PLOT_HANDLER.edit_data()
        print(edit_response)
        #dispatcher.utter_message(text=f"{edit_response}")

        return [SlotSet("subject_id", None), SlotSet("selected_value", None), SlotSet("hospital", None)]
class ActionChangePlottype(Action):

    def name(self) -> Text:
        return "action_change_plottype"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        plot_type = tracker.get_slot("plot_type")

        #print(plot_type)

        if plot_type:
            if plot_type.lower() not in ALLOWED_PLOT_TYPES:
                dispatcher.utter_message(text=f"Sorry, I can only create {'/'.join(ALLOWED_PLOT_TYPES)} plots.")
                return {"plot_type": None}
            dispatcher.utter_message(text=f"OK! I will create a {plot_type} plot.")

        PLOT_HANDLER.change_arg("type", plot_type)

        response = PLOT_HANDLER.send_args()
        print(response)
        #dispatcher.utter_message(text=f"{response}")

        return []


class ActionChangeColor(Action):
    def name(self) -> Text:
        return "action_change_color"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        color = tracker.get_slot("color")

       # print(color)

        if color:
            if color.lower() not in ALLOWED_COLORS:
                dispatcher.utter_message(text=f"Sorry, I can only change the color to {'/'.join(ALLOWED_COLORS)}.")
                return {"color": None}
            dispatcher.utter_message(text=f"OK! The color will be changed to {color}.")

        PLOT_HANDLER.change_arg("color", color)
        PLOT_HANDLER.change_arg("data_type", "comparison") # What type of data do we have? Comparison = Compare X to Y

        response = PLOT_HANDLER.send_args()
        print(response)
        #dispatcher.utter_message(text=f"{response}")

        return []

class ActionPredictValue(Action):
    def name(self) -> Text:
        return "action_predict_value"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        value = tracker.get_slot("selected_value")
        subject = tracker.get_slot("subject_id")
        hospital = tracker.get_slot("hospital")

        if hospital is None:
            dispatcher.utter_message(text=f"Error: No valid hospital name has been given.")
            return [SlotSet("subject_id", None), SlotSet("selected_value", None), SlotSet("hospital", None)]
        if value is None and subject is None:
            dispatcher.utter_message(text=f"Error: Please provide the patient and what value to use for the prediction!")
            return [SlotSet("subject_id", None), SlotSet("selected_value", None)]
        if value is None:
            dispatcher.utter_message(text=f"Error: Can't do prediction without knowing what to predict!")
            return [SlotSet("subject_id", None), SlotSet("selected_value", None)]
        if subject is None:
            dispatcher.utter_message(text=f"Error: Can't do prediction without knowing which patient to predict for!")
            return [SlotSet("subject_id", None), SlotSet("selected_value", None)]

        if value:
            if value.lower() not in ALLOWED_SELECTED_VALUES:
                dispatcher.utter_message(text=f"Sorry, I don't recognize that value.")
                return {"selected_value": None}

        if subject:
            if subject.lower() not in ALLOWED_FAKEIDS:
                dispatcher.utter_message(text=f"Sorry, I do not recognize the patient id.")
                return {"subject_id": None}

        dispatcher.utter_message(text=f"Predicting {value} for {subject}...")

        PLOT_HANDLER.change_arg("selected_value", value)
        PLOT_HANDLER.change_arg("subject_id", subject)
        PLOT_HANDLER.change_arg("data_type", "shap")  # What type of data do we have? shap = shap values
        PLOT_HANDLER.change_arg("plot_type", "bar") # Using bar chart for clarity

        # If the value we're predicting is discharge_mrs, we need to check if the features we are predicting it from
        # are missing or not
        if value == "discharge_mrs":
            missing_value_check, missing_values = predictions.check_nan_variables(subject)
            if not missing_value_check:
                dispatcher.utter_message(text=f"Missing values! Cannot predict discharge_mrs.")
                dispatcher.utter_message(text=f"List of missing values: {missing_values}")
                return [SlotSet("subject_id", None),
                        SlotSet("selected_value", None)]

        prediction_value, feature_list, feature_response = predictions.prediction_and_feature_importance()
        print(feature_response)
        #dispatcher.utter_message(text=f"Response from predictions: {feature_response}")  # 200 for success

        # If the value is not discharge_mrs, we want to change the value in the code
        if value != 'discharge_mrs':
            patient_values = predictions.set_patient_variables(subject)
            if patient_values[value] is None:
                patient_values[value] = prediction_value
                print(f"{value} is now: {patient_values[value]}")
        if value != 'discharge_mrs':
            PLOT_HANDLER.change_arg("FakePatient_" + str(value), float(prediction_value[0]))
        PLOT_HANDLER.change_arg("x-value", "Feature")
        PLOT_HANDLER.change_arg("y-value", "SHAP Value")

        if subject.lower() == "patient1":
            PLOT_HANDLER.change_arg("FakePatient_age", 1.21)
        elif subject.lower() == "patient2":
            PLOT_HANDLER.change_arg("FakePatient_age", 1.65)

        response = PLOT_HANDLER.send_args()
        print(response)
        #dispatcher.utter_message(text=f"Response from send_args: {response}") # 200 for success

        dispatcher.utter_message(text=f"Prediction is {prediction_value} for {value}, {subject}")

        dispatcher.utter_message(text=f"Graph is displaying SHAP values for the 10 most important related features for {value}.")
        if isActive:
            if value != 'discharge_mrs':
                if patient_values['door_to_needle'] == None:
                    dispatcher.utter_message(text=f"Do you want to predict door_to_needle now or see model accuracy?")
                if patient_values['door_to_imaging'] == None:
                    dispatcher.utter_message(text=f"Do you want to predict door_to_imaging now or see model accuracy?")
                if patient_values['door_to_imaging'] != None and patient_values['door_to_needle'] != None:
                    dispatcher.utter_message(text=f"Do you want to predict discharge_mrs now or see model accuracy?")
            else:
                dispatcher.utter_message(text=f"Do you want to see the model accuracy?")

        return []

class ActionModelAccuracy(Action):
    def name(self) -> Text:
        return "action_model_accuracy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        value = tracker.get_slot("selected_value")
        subject = tracker.get_slot("subject_id")

        print(f"hello, value is {value} and subject is {subject}")

        dispatcher.utter_message(text=f"Showing accuracy of latest prediction: {value} for {subject}:")
        dispatcher.utter_message(text=f"Root Mean Squared Error for prediction is: {predictions.latest_prediction_value}.")
        dispatcher.utter_message(text=f"Graph shows predicted values compared to real values.")

        PLOT_HANDLER.change_arg("data_type", "comparison")
        PLOT_HANDLER.change_arg("x-value", "Real Values")
        PLOT_HANDLER.change_arg("y-value", "Predicted Values")

        accuracy_response = predictions.model_accuracy()
        print(accuracy_response)
        #dispatcher.utter_message(text=f"Response from model_accuracy: {accuracy_response}")  # 200 for success

        response = PLOT_HANDLER.send_args()
        print(response)
        #dispatcher.utter_message(text=f"Response from send_args: {response}")  # 200 for success

        return [SlotSet("subject_id", None),
                SlotSet("selected_value", None)]

class ActionCollectAndShowNewPaitentData(Action):
    #Does not actually show data yet, but does collect it and send it to plot_args.json
    def name(self) -> Text:
        return "action_show_specified_fake_patient"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        subject_id = tracker.get_slot("subject_id")
        subjectdata = predictions.set_patient_variables(subject_id)
        if subject_id:
            if subject_id.lower() not in ALLOWED_FAKEIDS:
                dispatcher.utter_message(text=f"Sorry, I can only show the patients with missing data.")
                return [SlotSet("subject_id", None)]
            dispatcher.utter_message(text=f"OK! the data for {subject_id} will be shown in the table in the bottom tab")
            #for key, value in subjectdata.items():
            #    dispatcher.utter_message(text=f"{key},{value}")
            PLOT_HANDLER.change_arg("subject_id", subject_id)
            PLOT_HANDLER.change_arg("FakePatient_age", None)
            for key, value in subjectdata.items():
                PLOT_HANDLER.change_arg("FakePatient_" + str(key), value)
            response = PLOT_HANDLER.send_args()
            if isActive:
                return [FollowupAction("followaction_predict_After_showdata")]
            else:
                return [SlotSet("subject_id", None)]
        return []

class FollowupActionPredictsetup(Action):
    def name(self) -> Text:
        return "followaction_predict_After_showdata"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        subject_id = tracker.get_slot("subject_id")
        subjectdata = predictions.set_patient_variables(subject_id)
        selected_value = tracker.get_slot("selected_value")
        if subject_id == "patient1":
            dispatcher.utter_message(text=f"Do you want to run a prediction with this patient?")
        elif subject_id == "patient2":
            for key, value in subjectdata.items():
                if value is None:
                    dispatcher.utter_message(text=f"This patient is missing some data.")
                    dispatcher.utter_message(text=f"Do you want to try to predict what this data should be?")
                    return []
            dispatcher.utter_message(text=f"This patient's data is restored, do you want to run a prediction")
        return []


class FollowPredictionAffirm(Action):
    def name(self) -> Text:
        return "followaction_affirm_predict"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        subject_id = tracker.get_slot("subject_id")
        subjectdata = predictions.set_patient_variables(subject_id)
        selected_value = tracker.get_slot("selected_value")
        if subject_id == "patient1":
            SlotSet("selected_value", "discharge_mrs")
            PLOT_HANDLER.change_arg("selected_value", selected_value)
            response = PLOT_HANDLER.send_args()
            return [FollowupAction("action_predict_value_active")]
        if subject_id == "patient2":
            if subjectdata.door_to_imaging is None or subjectdata.door_to_needle is None:
                return []
            PLOT_HANDLER.change_arg("selected_value", selected_value)
            response = PLOT_HANDLER.send_args()
            return [SlotSet("selected_value", "discharge_mrs")]
        return []

class FollowActionDeny(Action):
    def name(self) -> Text:
        return "follow_Denial_Wipe_Slots"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("subject_id", None), SlotSet("selected_value", None), SlotSet("hospital", None)]
class ActionPredictValueActive(Action):
    def name(self) -> Text:
        return "action_predict_value_active"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"Okay! Please tell me what value to do a prediction for!")

        check = predictions.active_ask_for_value()

        if check == 0:
            dispatcher.utter_message(text=f"I can currently predict the missing door_to_imaging and door_to_needle!")
            dispatcher.utter_message(text=f"I can NOT predict discharge_mrs before you have predicted those!")
            return []
        elif check == 1:
            dispatcher.utter_message(text=f"I can currently predict the missing door_to_imaging value!")
            dispatcher.utter_message(text=f"After you predict it, I can predict the missing discharge_mrs score!")
            return []
        elif check == 2:
            dispatcher.utter_message(text=f"I can currently predict the missing door_to_needle value!")
            dispatcher.utter_message(text=f"After you predict it, I can predict the missing discharge_mrs score!")
            return []
        elif check == 3:
            dispatcher.utter_message(text=f"I can currently predict the missing discharge_mrs value!")
            return []
        return []

class ActionChangeDatabeingShowcased(Action):
    def name(self) -> Text:
        return "action_change_data"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        selected_axis = tracker.get_slot("selected_axis")
        selected_value = tracker.get_slot("selected_value")

       # print(selected_axis)
       # print(selected_value)

        if selected_value and selected_axis:
            if selected_value.lower() not in ALLOWED_SELECTED_VALUES:
                dispatcher.utter_message(text=f"Sorry, I can only show data point that exist in the datasheet.")
                selected_value = None
                return [SlotSet("selected_value", None)]
            if selected_axis.lower() not in ALLOWED_AXIS:
                dispatcher.utter_message(text=f"Sorry, I can only show data point that exist in the datasheet.")
                selected_axis = None
                return [SlotSet("selected_axis", None)]
            if selected_value and selected_axis:
                dispatcher.utter_message(text=f"Okay, I will show {selected_value} along the {selected_axis}")
                if selected_axis == "x-axis":
                    PLOT_HANDLER.change_arg("x-value", selected_value)
                elif selected_axis == "y-axis":
                    PLOT_HANDLER.change_arg("y-value", selected_value)
                response = PLOT_HANDLER.send_args()
                selected_axis = None
                selected_value = None
                return [SlotSet("selected_axis", None),("selected_value", None)]
        elif selected_value and selected_axis is None:
            dispatcher.utter_message(text=f"Okay, which axis should I show {selected_value} along?")
        elif selected_axis and selected_value is None:
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
        print(response)
        #dispatcher.utter_message(text=f"{response}")

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
        print(response)
        #dispatcher.utter_message(text=f"{response}")

        return []

class ActionChangeHospital(Action):

    def name(self) -> Text:
        return "action_change_hospital"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        hospital = tracker.get_slot("hospital")

        if hospital:
            if hospital.lower() not in ALLOWED_HOSPITALS:
                dispatcher.utter_message(text=f"Hospital not found. Allowed hospitals are: {'/'.join(ALLOWED_HOSPITALS)}.")
                return [SlotSet("hospital", None)]
            dispatcher.utter_message(text=f"OK! I will use data from {hospital}.")

        PLOT_HANDLER.change_arg("hospital", hospital)

        response = PLOT_HANDLER.send_args()
        print(response)
        #dispatcher.utter_message(text=f"Response from send_args: {response}")

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
