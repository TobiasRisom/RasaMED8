import base64
import math

import pandas as pd
from sklearn.model_selection import train_test_split
#from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor
# import xgboost as xgb
import shap
import numpy as np
import os
import json
import gzip
import requests

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

iamafakepatient_values = {
            'age': 65,
            'nihss_score': 2,
            'covid_test': 1,
            'door_to_imaging': 44,
            'bleeding_source': 1,
            'door_to_needle': 35,
            'risk_smoker': 1,
            'cholesterol': 3.4,
        }

ihavelostdataid_values = {
            'age': 52,
            'nihss_score': 3,
            'covid_test': 1,
            'door_to_imaging': None,
            'bleeding_source': 3,
            'door_to_needle': None,
            'risk_smoker': 0,
            'cholesterol': 2.3,
        }

def set_patient_variables(subject_id):
    # Sets the values for the patient based on the id
    if subject_id == "iamafakepatient":
        # Fill in the values for the new patient's features
        return iamafakepatient_values
    if subject_id == "ihavelostdataid":
        return ihavelostdataid_values


# A check to see if any NaN values need to be predicted before we can move on with predicting the MRS
def check_nan_variables(subject_id):
    patient_variables = set_patient_variables(subject_id)
    nan_variables = [key for key, value in patient_variables.items() if isinstance(value, float) and math.isnan(value)]
    if nan_variables:
        return False, nan_variables
    else:
        return True, None

def prediction_and_feature_importance():

    with open("actions/utils/plot_args.json", 'r') as json_file:
        config = json.load(json_file)

    target_variable = config['visualization']['selected_value']

    new_patient_data = set_patient_variables('iamafakepatient')

    # Load the data
    #OBS, USE THIS LINE FOR RUNNING "RASA RUN ACTIONS":
    data = pd.read_csv('actions/utils/dataREanonymized_long2.csv', low_memory=False)

    # USE THIS LINE FOR JUST RUNNING PREDICTIONS.PY:
    #data = pd.read_csv('dataREanonymized_long2.csv', low_memory=False)

    # Turn some non-numeric values into numeric values (causes error atm)
    #data['Value'] = pd.to_numeric(data['Value'].map({'female': 0, 'male': 1}), errors='coerce')

    # Specify the target variable you want to predict
    #target_variable = 'onset_to_door'

    # Extract all unique predictor variable names from the "variable" column
    predictor_variables = data['variable'].unique()

    # Remove the target variable from the predictor variables list
    predictor_variables = [var for var in predictor_variables if var != target_variable]

    # Define the order of categories in the "TAB" column
    category_order = ['PC', 'Bleeding', 'Imaging', 'Treatment', 'PO', 'Discharge']

    # Map category names to their positions in the order of occurrence
    category_positions = {category: index for index, category in enumerate(category_order)}

    # Get the category of the target variable
    target_category = data.loc[data['variable'] == target_variable, 'TAB'].iloc[0]

    # Sort data to one hospital
    data = data[data['site_id'].isin(["Pineview"])]

    # Filter predictor variables based on the category order
    predictor_variables_filtered = []
    predictor_variables_filtered_names = []
    for var in predictor_variables:
        #print(var) # prints every category and there are so many categories like omg
        var_category = data.loc[data['variable'] == var, 'TAB'].iloc[0]
        if category_positions[var_category] < category_positions[target_category]:
            predictor_variables_filtered.append(var)
            predictor_variables_filtered_names.append(data.loc[data['variable'] == var, 'INDICATOR'].iloc[0])

    # If the target variable is from the "PC" category, print a message and exit
    if target_category == 'PC':
        print("The target variable is from the 'PC' category, and it cannot be predicted.")
        exit()


    # Convert non-numeric values in 'Value' column to NaN
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')

    # Pivot the data to wide format based on the 'variable' column
    data_wide = data.pivot_table(index=['YQ', 'subject_id'], columns='variable', values='Value').reset_index()

    # Impute attempt
    imputer = SimpleImputer(strategy='median')
    data_wide_imputed = imputer.fit_transform(data_wide.iloc[:, 2:])  # Exclude non-numeric columns 'YQ' and 'subject_id'

    # Convert the imputed array back to a DataFrame
    data_wide_imputed_df = pd.DataFrame(data_wide_imputed, columns=data_wide.columns[2:])

    # Combine 'YQ' and 'subject_id' columns with the imputed data
    data_wide_imputed_df[['YQ', 'subject_id']] = data_wide[['YQ', 'subject_id']]

    data_wide = data_wide_imputed_df

    # Fill missing values with 0 if needed
    #data_wide.fillna(0, inplace=True)

    # Drop NaN values for the target variable
    # data_wide.dropna(subset=[target_variable], inplace=True)


    if data_wide.shape[0] == 0:
        print("No samples left after removing rows with NaN values. Cannot proceed with model training.")
        exit()

    # Convert non-numeric variables to numeric if needed
    for var in data_wide.columns:
        if var != 'YQ' and var not in predictor_variables_filtered:
            try:
                if not pd.api.types.is_numeric_dtype(data_wide[var]):
                    data_wide[var] = pd.to_numeric(data_wide[var], errors='coerce')
            except KeyError:
                print(f"Skipping variable {var} due to KeyError")

    filtered_indices = [i for i, var in enumerate(predictor_variables_filtered) if var in data_wide.columns]
    predictor_variables_filtered = [predictor_variables_filtered[i] for i in filtered_indices]

    # Remove corresponding indices from predictor_variables_filtered_names
    predictor_variables_filtered_names = [predictor_variables_filtered_names[i] for i in filtered_indices]

    # Split the data into training and testing sets
    X = data_wide[predictor_variables_filtered]
    y = data_wide[target_variable]

    # In long format, we don't need to split the data; each record is independent
    # So, we can directly use all data for training
    X_train, X_test, y_train, y_test = X, X, y, y  # Just for consistency
    # Build the Gradient Boosting Regressor model
    gbr = XGBRegressor()
    gbr.fit(X_train, y_train)

    # Predict on the testing set (we're using the same data for training and testing in this case)
    y_pred = gbr.predict(X_test)

    # Calculate accuracy (RMSE in this case)
    accuracy = mean_squared_error(y_test, y_pred, squared=False)
    #print(f'Root Mean Squared Error: {accuracy}')

    feature_importances = gbr.feature_importances_
    # Sort feature importances
    sorted_indices = feature_importances.argsort()[::-1]
    # Print top 10 important features
    # AND put them in a returnable object

    top_ten_features = []

    print('Top 10 Feature Importances:')
    for i in sorted_indices[:10]:
        print(f'{predictor_variables_filtered_names[i]}: {feature_importances[i]}')

    explainer = shap.TreeExplainer(gbr)

    shap_values = explainer.shap_values(X_test)

    mean_shap_values = np.abs(shap_values).mean(axis=0)

    # Get indices of features sorted by importance
    sorted_indices = np.argsort(mean_shap_values)[::-1][:10]

    print("Top", 10, "most important features::::::::::::::::::::::::::::::::::::::::::::::")
    for i in sorted_indices[:10]:
        print(f"{predictor_variables_filtered_names[i]}: {mean_shap_values[i]}")
        top_ten_features.append({"variable": predictor_variables_filtered_names[i], "Value": mean_shap_values[i]})

    # Convert the list to a DataFrame
    top_ten_features_df = pd.DataFrame(top_ten_features)

    # Rename the columns
    top_ten_features_df = top_ten_features_df.rename(columns={"variable": "Value_x", "Value": "Value_y"})

    # Creates data.json with the new values
    json_data = top_ten_features_df.to_json(orient='records')

    with open("actions/utils/data.json", 'w') as json_file:
        json_file.write(json_data)

    # Create a DataFrame for the new patient with the same columns as the imputed data
    new_patient_df = pd.DataFrame(columns=data_wide.columns, index=[0])

    for feature, value in new_patient_data.items():
        if feature in predictor_variables_filtered:
            new_patient_df[feature] = value

    print("Data Wide:")
    print(data_wide.iloc[0])
    print("New Patient:")
    print(new_patient_df.iloc[0])

    new_patient_df = new_patient_df.iloc[:, :-2]

    # Use the imputer to fill missing values in the new patient data
    new_patient_df_imputed = pd.DataFrame(imputer.transform(new_patient_df), columns=new_patient_df.columns)

    # Convert the imputed array back to a DataFrame
    new_patient_df_imputed = pd.DataFrame(new_patient_df_imputed, columns=predictor_variables_filtered)

    #print("New Patient Imputed:")
    #print(new_patient_df_imputed.iloc[0])

    # Use the trained model to predict the target variable for the new patient
    predicted_value = gbr.predict(new_patient_df_imputed)

    print("Median target variable:", data_wide[target_variable].median())
    print("Predicted target variable value for the new patient:", predicted_value)

    with open("actions/utils/data.json", 'r') as json_file:
        config = json.load(json_file)

    compressed_content = gzip.compress(json.dumps(config).encode("utf-8"))
    compressed_content_decoded = base64.b64encode(compressed_content).decode("utf-8")

    payload = {"file_type": "data", "file_content": compressed_content_decoded}

    response = requests.post("http://localhost:3000/rasa-webhook", json=payload)

    return predicted_value, top_ten_features, response
