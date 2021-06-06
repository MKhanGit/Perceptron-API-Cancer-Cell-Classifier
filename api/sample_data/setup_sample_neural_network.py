import csv
import os
import time
import numpy
from APIHelpers import db_helper, io_helper
from neural_network import NeuralNetwork

config_data = io_helper.load_config_data()

mongo_db = db_helper.DBConnection(config_data['mongo_host'], config_data['mongo_port'], config_data['mongo_database'],
                                  config_data['data_collection'])
mongo_metadata_db = db_helper.DBConnection(config_data['mongo_host'], config_data['mongo_port'],
                                           config_data['mongo_database'],
                                           config_data['metadata_collection'])


def main(timeout=20):
    start_time = time.time()
    test_doc = {"test_docment": str(1)}
    mongo_db.write_document(test_doc)

    wait_for_db = True
    while wait_for_db:
        if mongo_db.record_exists(test_doc):
            wait_for_db = False
        elif (time.time() - start_time) >= timeout:
            break
        else:
            try:
                mongo_db.write_document(test_doc)
            except TimeoutError:
                pass
    if not wait_for_db:
        mongo_db.remove_document(test_doc)
        write_data_db()
        trained_networks = list()
        record_count = 0
        for _ in range(config_data['sample_training_iterations']):
            record_count, trained_network = train_network_db()
            pass_rate, test_count = test_network_db(trained_network)
            trained_networks.append((trained_network, pass_rate))
            # print("[Breast Cancer Classifier] Sample Neural Network trained on {0} records ...".format(record_count))
            # print("[Breast Cancer Classifier] Sample Neural Network tested on "
            #       "{1} records with {0:.2f}% PassRate!".format(pass_rate, test_count))
        trained_networks.sort(key=lambda x: x[1], reverse=True)
        print("[Breast Cancer Classifier] After {0} training iterations on {1} records, "
              "deploying Sample Network with {2:.2f}% Accuracy...".format(config_data['sample_training_iterations'],
                                                                          record_count,
                                                                          trained_networks[0][1]))
        write_network_metadata(trained_networks[0][0])


def write_data_db():
    # Write sample data to Mongo DB (if not previously loaded)
    # Training Records
    with open(config_data["sample_network_training_data_csv"]) as csvfile:
        csv_rows = csv.reader(csvfile)
        for i, row in enumerate(csv_rows):
            if mongo_db.record_exists({"record_id": "BC_Sample_Train_{0}".format(i)}):
                continue
            document = dict()
            features = {str(k): v for k, v in enumerate(row[:-1])}
            target = {"record_id": "BC_Sample_Train_{0}".format(i), "training_record": str(True),
                      "target_class": str(row[-1])}
            document.update(features)
            document.update(target)
            mongo_db.write_document(document)
    # Testing Records
    with open(config_data["sample_network_testing_data_csv"]) as csvfile:
        csv_rows = csv.reader(csvfile)
        for i, row in enumerate(csv_rows):
            if mongo_db.record_exists({"record_id": "BC_Sample_Test_{0}".format(i)}):
                continue
            document = dict()
            features = {str(k): v for k, v in enumerate(row[:-1])}
            target = {"record_id": "BC_Sample_Test_{0}".format(i), "training_record": str(False),
                      "target_class": str(row[-1])}
            document.update(features)
            document.update(target)
            mongo_db.write_document(document)


def train_network_db():
    sample_network = NeuralNetwork(input_nodes=config_data['sample_network_input_nodes'],
                                   hidden_nodes=config_data['sample_network_hidden_nodes'],
                                   output_nodes=config_data['sample_network_output_nodes'],
                                   learning_rate=config_data['sample_network_learn_rate'])
    rcount = 0
    for record in mongo_db.read_documents({"training_record": str(True),
                                           "record_id": {"$regex": "BC_Sample_Train_.*?"}}):
        rcount += 1
        features = [record[str(i)] for i in range(config_data['sample_network_input_nodes'])]
        target_class = int(record['target_class'])
        sample_network.train(features, target_class)
    return rcount, sample_network


def write_network_metadata(neural_network):
    io_helper.save_pretrained_network(neural_network,
                                      os.path.join(config_data['trained_networks_directory'],
                                                   config_data['sample_network_file']))
    network_storage_document = {"network_id": config_data['sample_network_name'],
                                "saved_data": os.path.join(config_data['trained_networks_directory'],
                                                           config_data['sample_network_file'])}
    if mongo_metadata_db.record_exists({"network_id": config_data['sample_network_name']}):
        mongo_metadata_db.remove_document({"network_id": config_data['sample_network_name']})
    mongo_metadata_db.write_document(network_storage_document)


def test_network_db(neural_network):
    # small test which checks the pass-rate against the db testing records
    total_tests = 0
    passed_tests = 0
    for testing_record in mongo_db.read_documents({"training_record": str(False),
                                                   "record_id": {"$regex": "BC_Sample_Test_.*?"}}):
        total_tests += 1
        features = [testing_record[str(i)] for i in range(config_data['sample_network_input_nodes'])]
        target_class = int(testing_record['target_class'])
        network_outputs = neural_network.query(numpy.asfarray(features))
        if numpy.argmax(network_outputs) == target_class:
            passed_tests += 1
    return (float(passed_tests) / total_tests) * 100, total_tests


if __name__ == '__main__':
    main()
