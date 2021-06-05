import numpy
from scipy import special


class NeuralNetwork:
    def __init__(self, input_nodes, hidden_nodes, output_nodes, learning_rate):
        """
        Constructs a shallow perceptron network with randomized weights using the provided parameters.

        :param input_nodes: Number of input nodes in the network.
        :param hidden_nodes: Number of hidden nodes in the network.
        :param output_nodes: Number of output nodes in the network.
        :param learning_rate: The factor applied to the activation function when new network weights are learned.
        """
        self.inodes = input_nodes
        self.hnodes = hidden_nodes
        self.onodes = output_nodes
        # Initialize weights and learning-rate between input-hidden and hidden-output layer interfaces
        self.wih = numpy.random.normal(0.0, pow(self.hnodes, -0.5), (self.hnodes, self.inodes))
        self.who = numpy.random.normal(0.0, pow(self.onodes, -0.5), (self.onodes, self.hnodes))
        self.lr = learning_rate
        # activation function is the sigmoid function
        self.activation_function = lambda x: special.expit(x)

    def train(self, input_features, target_class):
        """
        Trains the network to relate the provided features to the provided output node index.
        Formats input/target sample_data prior to passing it for network training.

        :param input_features: a list of normalized feature values (can be string representations)
        :param target_class: the class index which is being represented by the feature values
        :return:
        """
        inputs = numpy.asfarray(input_features)
        targets = numpy.zeros(self.onodes) + 0.01
        targets[int(target_class)] = 0.99
        self._train(inputs, targets)

    def _train(self, inputs_list, targets_list):
        """
        "Raw" network training which expects float arrays corresponding to the input and output node lengths.
        Instead of calling this function directly, use the train(..) method instead, as it is designed to take a list of
        features and a target class index, formatting the input/target lists accordingly.

        :param inputs_list: float array of feature values whose length equals the number of input nodes to the network
        :param targets_list: float array of target values whose length equals the number of output nodes to the network
        :return:
        """
        # query network using the current weights, then adjust weights based on output error vs actual targets list
        return self.query(inputs_list, targets_list)

    def query(self, inputs_list, targets_list=None):
        """
        Accepts a float array of feature values, returning the network output array as a distribution of confidences for
        each target class. If a `targets_list` is provided, the network will train its future outputs towards those
        targets.

        :param inputs_list: a list of feature values whose length matches the number of input nodes to the network
        :param targets_list: (optional) if provided, the network is trained towards these targets for future queries
        :return:
        """
        # convert inputs list to 2d array
        inputs = numpy.array(inputs_list, ndmin=2).T

        # calculate signals into hidden layer
        hidden_inputs = numpy.dot(self.wih, inputs)
        # calculate the signals emerging from hidden layer
        hidden_outputs = self.activation_function(hidden_inputs)

        # calculate signals into final output layer
        final_inputs = numpy.dot(self.who, hidden_outputs)
        # calculate the signals emerging from final output layer
        final_outputs = self.activation_function(final_inputs)

        if targets_list is not None:  # when given a targets list, the network trains towards those targets
            targets = numpy.array(targets_list, ndmin=2).T
            # output layer error is the (target - actual)
            output_errors = targets - final_outputs
            # hidden layer error is the output_errors, split by weights, recombined at hidden nodes
            hidden_errors = numpy.dot(self.who.T, output_errors)

            # update the weights for the links between the hidden and output layers
            self.who += self.lr * numpy.dot((output_errors * final_outputs * (1.0 - final_outputs)),
                                            numpy.transpose(hidden_outputs))

            # update the weights for the links between the input and hidden layers
            self.wih += self.lr * numpy.dot((hidden_errors * hidden_outputs * (1.0 - hidden_outputs)),
                                            numpy.transpose(inputs))

        return final_outputs

    def __repr__(self):
        nrep = "NeuralNetwork(input_nodes: {0}, hidden_nodes: {1}, output_nodes: {2}, learning_rate: {3})".format(
            self.inodes, self.hnodes, self.onodes, self.lr)
        nrep += "\n\nInput-Hidden Layer Weights:\n\t{0}\n\nHidden-Output Layer Weights:\n\t{1}\n\n".format(self.wih,
                                                                                                           self.who)
        return nrep

    def __str__(self):
        nstr = "NeuralNetwork(input_nodes: {0}, hidden_nodes: {1}, output_nodes: {2}, learning_rate: {3})".format(
            self.inodes, self.hnodes, self.onodes, self.lr)
        return nstr


class NetworkTester:
    def __init__(self, training_data, testing_data, input_nodes, hidden_nodes, output_nodes, learning_rate):
        """

        :param training_data:
        :param testing_data:
        :param input_nodes:
        :param hidden_nodes:
        :param output_nodes:
        :param learning_rate:
        """
        self.training_data = training_data
        self.testing_data = testing_data
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes
        self.learning_rate = learning_rate

        self.neural_network = NeuralNetwork(self.input_nodes, self.hidden_nodes, self.output_nodes, self.learning_rate)
        self.__train_all_records__()

    def __train_all_records__(self):
        for record in self.training_data:
            self.__train_one_record__(record[0], record[1])

    def __train_one_record__(self, inputs_list, target_class):
        inputs = numpy.asfarray(inputs_list)
        targets = numpy.zeros(self.output_nodes) + 0.01
        targets[int(target_class)] = 0.99
        self.neural_network.train(inputs, targets)

    def update_network(self, inputs_list, target_class):
        """
        Apply a training record into the network
        :param inputs_list:
        :param target_class:
        :return:
        """
        self.__train_one_record__(inputs_list, target_class)

    def test(self):
        _total = 0
        _pass = 0

        for record in self.testing_data:
            print("Testing Record: {0} ...".format(record[0]), end=" ")
            if int(record[1]) == numpy.argmax(self.neural_network.query(numpy.asfarray(record[0]))):
                print("\t\t !!PASSED!! ", end=" ")
                _pass += 1
            else:
                print("\t\t ==FAILED== ", end=" ")
            print(" ({0})".format("Malignant" if int(record[1]) else "Benign"))
            _total += 1
        return float(_pass)/_total
