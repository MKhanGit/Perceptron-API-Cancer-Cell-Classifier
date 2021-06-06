import json
import dill
import csv
from neural_network import NeuralNetwork


def load_config_data(config_file='config.json'):
    """
    Load system configuration settings from a local JSON file into memory.

    :param config_file: path to a JSON configuration file
    :return: a JSON (dictionary) object loaded into memory from the provided file
    """
    with open(config_file, 'r') as config_file:
        return json.load(config_file)


def save_pretrained_network(neural_network_obj, outputfile):
    """
    Take a NeuralNetwork class object and serialize it to a file for later use.

    :param neural_network_obj: NeuralNetwork class object for serialization to file.
    :param outputfile: location of file to save the serialized object to.
    :return: boolean representing if the operation was successful.
    """
    if isinstance(neural_network_obj, NeuralNetwork):
        with open(outputfile, "wb") as fh:
            dill.dump(neural_network_obj, fh)
            return True
    else:  # object passed for serialization was not a `NeuralNetwork` class object
        return False


def load_pretrained_network(inputfile):
    """
    Load a serialized NeuralNetwork class object from file into memory.

    :param inputfile: location of file containing serialized NeuralNetwork object
    :return: NeuralNetwork object, returns None if the loaded object type is incorrect.
    """
    with open(inputfile, 'rb') as fh:
        loaded_obj = dill.load(fh)
        if isinstance(loaded_obj, NeuralNetwork):
            return loaded_obj
        else:  # object loaded from file was not a `NeuralNetwork` class object
            return None


def read_data_csv(csvfile):
    """
    Returns a list of tuples of the format ([features], target) from a CSV file, where the class is given by column "n"
    and the [features] list is given by columns ["0", "1", ... "n-1"].

    :param csvfile: path to a csv file containg feature/target values
    :return: a list of tuples of the format ([features], target)
    """
    segmented_data = list()
    with open(csvfile, 'r') as csvfh:
        for row in csv.reader(csvfh):
            segmented_data.append((row[:-1], row[-1]))
        return segmented_data
