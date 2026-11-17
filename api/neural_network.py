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
        self.wih = numpy.random.normal(0.0, pow(self.hnodes, -0.5), (self.hnodes, self.inodes))
        self.who = numpy.random.normal(0.0, pow(self.onodes, -0.5), (self.onodes, self.hnodes))
        self.lr = learning_rate
        self.activation_function = lambda x: special.expit(x)

    def train(self, input_features, target_class):
        """
        Trains the network to relate the provided features to the provided output node index.
        Formats input/target sample_data prior to passing it for network training.

        :param input_features: a list of normalized feature values (can be string representations)
        :param target_class: the class index which is being represented by the feature values
        :return:
        """
        inputs = numpy.asarray(input_features, dtype=float)
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
        inputs = numpy.array(inputs_list, ndmin=2).T

        hidden_inputs = numpy.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)

        final_inputs = numpy.dot(self.who, hidden_outputs)
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

