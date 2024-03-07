import matplotlib.figure
import matplotlib.pyplot as plt
import datetime
import seaborn
import pickle
import numpy as np
from actions.utils import globals
from sklearn import linear_model, ensemble
import json
import requests


class PlotHandler:
    def __init__(self, save_plot=False):
        self._date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._plot_name = None
        self._save = save_plot
        self.json_file_path = "actions/utils/plot_args.json"
        self.website_url = "http://localhost:3000/rasa-webhook"

    def change_arg(self, arg, value):
        with open(self.json_file_path, 'r') as json_file:
            config = json.load(json_file)

        config['visualization'][arg] = value

        with open(self.json_file_path, 'w') as json_file:
            json.dump(config, json_file, indent=2)
            print(json.dumps(config, indent=2))

    def send_args(self):
        with open(self.json_file_path, 'r') as file:
            json_data = json.load(file)

        response = requests.post(self.website_url, json=json_data)
        return response


    def plot_timeline(self, x, y, x_label: str = None, y_label: str = None):
        self._plot_name = "timeline"

        self.change_plot_type(self._plot_name)

        plot, ax = plt.subplots()
        if x_label is not None:
            ax.set_xlabel(x_label)
        if y_label is not None:
            ax.set_ylabel(y_label)
        ax.plot(x, y, marker="o")
        ax.tick_params(axis="x", rotation=90)
        for i in range(len(x)):
            ax.text(x[i], y[i] * 1.05, str(round(y[i])), color='black', fontsize=12, ha='center', va='bottom')
        plot.subplots_adjust(bottom=0.20)
        ax.tick_params(axis='both', which='both', color='b', grid_alpha=0.5, grid_linewidth=0.5)
        if self._save:
            self._save_plot_to_img(plot)
        return plot

    def plot_distribution(self, x, x_label: str = None, y_label: str = None):
        self._plot_name = "distribution"

        self.change_plot_type(self._plot_name)

        if x_label is not None:
            plt.xlabel(x_label)
        if y_label is not None:
            plt.ylabel(y_label)
        plot = seaborn.kdeplot(x).get_figure()
        plt.xlim(0, max(x))
        plt.tick_params(axis='both', which='both', color='b', grid_alpha=0.5, grid_linewidth=0.5)
        plt.grid(True)
        if self._save:
            self._save_plot_to_img(plot)
        return plot

    def plot_correlation(self, x, y, x_label: str = None, y_label: str = None):
        self._plot_name = "correlation"

        self.change_plot_type(self._plot_name)

        plot, ax = plt.subplots()
        if x_label is not None:
            ax.set_xlabel(x_label)
        if y_label is not None:
            ax.set_ylabel(y_label)
        ax.scatter(x, y)
        ax.tick_params(axis='both',
                       which='both',
                       color='b',
                       grid_alpha=0.5,
                       grid_linewidth=0.5)
        ax.grid(True)
        if self._save:
            self._save_plot_to_img(plot)
        return plot

    def plot_comparison(self, values_list: list, labels_list: list, x_label: str = None, y_label: str = None):
        self._plot_name = "comparison"

        self.change_plot_type(self._plot_name)

        plot, ax = plt.subplots()
        if x_label is not None:
            ax.set_xlabel(x_label)
        if y_label is not None:
            ax.set_ylabel(y_label)
        ax.boxplot(values_list, showfliers=False)
        ax.tick_params(axis='both', which='both', color='b', grid_alpha=0.5, grid_linewidth=0.5)
        ax.grid(True)
        ax.set_xticklabels(labels_list)
        if self._save:
            self._save_plot_to_img(plot)
        return plot

    def plot_regression(self, x, y, regression_type: str = "linear", x_label: str = None, y_label: str = None, polynomial_degree: int = 2):
        self._plot_name = "regression"

        self.change_plot_type(self._plot_name)

        if regression_type == "linear":
            model = linear_model.LinearRegression()
        elif regression_type == "logistic":
            model = linear_model.LogisticRegression()
        elif regression_type == "random_forest":
            model = ensemble.RandomForestRegressor()
        else:
            raise Exception("ERROR")

        plot, ax = plt.subplots()
        if x_label is not None:
            ax.set_xlabel(x_label)
        if y_label is not None:
            ax.set_ylabel(y_label)

        model.fit(x, y)
        ax.scatter(x, y)
        if regression_type == "linear" or "random_forest":
            ax.plot(x, model.predict(x), color='red', label='Regression')
        elif regression_type == "logistic":
            ax.plot(np.sort(x.squeeze()), model.predict_proba(np.sort(x))[:, 1], color='red', label='Regression')

        if self._save:
            self._save_plot_to_img(plot)
        return plot

    def _save_plot_to_img(self, plot: matplotlib.figure.Figure):
        plot.savefig(f"{globals.PATH_SAVE_PLOT}/{self._plot_name}_{self._date}.png")

    def _save_plot_to_obj(self, plot: matplotlib.figure.Figure):
        with open(globals.PATH_SAVE_OBJECT, "wb") as file:
            pickle.dump(plot, file)

    def _get_obj_to_plot(self):
        with open(globals.PATH_SAVE_OBJECT, "rb") as file:
            return pickle.load(file)
