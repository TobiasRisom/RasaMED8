import pandas
from actions.utils import plot_handler, globals


class DataHandler:

    def __init__(self, save_plot=False):
        self._plot_handler = plot_handler.PlotHandler(save_plot=save_plot)
        self._default_filters = self._get_default_filters()
        self._filters = self._default_filters

    def timeline(self, y_label: str):
        self._check_value(y_label)
        data = self._get_data()
        data = data[data["QI"] == y_label].dropna()
        filtered_data = self._filter(data)
        dataframe = filtered_data.groupby("YQ")["Value"].mean()
        x = dataframe.index
        y = dataframe.values
        self._plot_handler.plot_timeline(x, y, x_label="Year and Quarter", y_label=self._beautify_label(y_label))

    def distribution(self, x_label: str):
        self._check_value(x_label)
        data = self._get_data()
        data = data[data["QI"] == x_label].dropna()
        filtered_data = self._filter(data)
        x = filtered_data["Value"]
        self._plot_handler.plot_distribution(x,
                                             x_label=self._beautify_label(x_label),
                                             y_label=f"Density")

    def correlation(self, x_label: str, y_label: str):
        self._check_value(x_label)
        self._check_value(y_label)
        data = self._get_data()
        data = data[data["QI"] == x_label].dropna()
        filtered_data = self._filter(data)
        x = filtered_data["Value"]
        y = filtered_data[y_label]
        self._plot_handler.plot_correlation(x, y,
                                            x_label=self._beautify_label(x_label),
                                            y_label=self._beautify_label(y_label))

    def comparison(self, x_label: str, y_label: str):
        self._check_value(y_label)
        data = self._get_data()
        data = data[data["QI"] == y_label].dropna()
        filtered_data = self._filter(data)
        values_list = []
        accepted_comparison_values = globals.ACCEPTED_COMPARISON_VALUES
        if x_label in accepted_comparison_values.keys():
            for possible_value in accepted_comparison_values[x_label]["values"]:
                values_list.append(filtered_data[filtered_data[x_label] == possible_value]["Value"])
            labels_list = accepted_comparison_values[x_label]["labels"]
        else:
            raise globals.ERROR_COMPARISON_VALUE_NOT_ACCEPTED
        self._plot_handler.plot_comparison(values_list,
                                           labels_list,
                                           x_label=self._beautify_label(x_label),
                                           y_label=self._beautify_label(y_label))

    def regression(self):
        pass

    def _get_data(self):
        data = pandas.read_csv(globals.PATH_DATA_FILE)
        return data

    def _get_default_filters(self):
        filters_dict = globals.ACCEPTED_FILTER_VALUES
        default_filters = {}
        for filter_key, filter_value in filters_dict.items():
            default_filters[filter_key] = filter_value.get("default_value")
        return default_filters

    def reset_default_filters(self):
        self._filters = self._default_filters

    def update_filters(self, new_filters: dict = None, filter_name: str = None, new_value: any = None):
        if new_filters is not None:
            self._filters = new_filters
        elif filter_name is not None and new_value is not None:
            if filter_name not in self._default_filters.keys():
                raise Exception(globals.ERROR_UPDATE_FILTERS_NAME)
            if type(new_value) is not globals.ACCEPTED_FILTER_VALUES[filter_name]["type"]:
                raise Exception(globals.ERROR_UPDATE_VALUE_TYPE)
            accepted_values = globals.ACCEPTED_FILTER_VALUES[filter_name]["accepted_values"]
            if type(new_value) is list:
                for value in new_value:
                    if value not in accepted_values:
                        raise Exception(globals.ERROR_UPDATE_VALUE)
            self._filters[filter_name] = new_value
        else:
            raise Exception(globals.ERROR_UPDATE_NAME_AND_VALUE)

    def _filter(self, data):
        filters = self._filters
        for key, value in filters.items():
            default_value = globals.ACCEPTED_FILTER_VALUES[key]["default_value"]
            if value is not default_value:
                if type(value) is list:
                    data = data[data[key].isin(value)]
                else:
                    data = data[data[key] == value]
        return data

    def _beautify_label(self, label):
        self._check_value(label)
        labels = globals.ACCEPTED_SELECTED_VALUES
        return labels[label]

    def _check_value(self, value):
        accepted_values = globals.ACCEPTED_SELECTED_VALUES.keys()
        if value not in accepted_values:
            raise Exception(globals.ERROR_SELECTED_VALUE_NOT_ACCEPTED)