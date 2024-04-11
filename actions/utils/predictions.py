import pandas as pd
from sklearn.model_selection import train_test_split
#from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor
# import xgboost as xgb
import shap
import numpy as np

# Load the data
data = pd.read_csv('dataREanonymized_long2.csv', low_memory=False)

# Turn some non-numeric values into numeric values (causes error atm)
#data['Value'] = pd.to_numeric(data['Value'].map({'female': 0, 'male': 1}), errors='coerce')

# Specify the target variable you want to predict
target_variable = 'onset_to_door'

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
imputer = SimpleImputer(strategy='mean')
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
print(f'Root Mean Squared Error: {accuracy}')

feature_importances = gbr.feature_importances_
# Sort feature importances
sorted_indices = feature_importances.argsort()[::-1]
# Print top 10 important features
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
