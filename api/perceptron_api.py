import random
import flask
from flask_cors import cross_origin
import numpy
import uuid
import os
from APIHelpers import APIResponseStatus, db_helper, io_helper, cache_helper, debug_helper
from neural_network import NeuralNetwork
import sample_data.setup_sample_neural_network

# Load API configuration settings
config_data = io_helper.load_config_data()

# Load MongoDB connection
records_db = db_helper.DBConnection(config_data['mongo_host'], config_data['mongo_port'],
                                    config_data['mongo_database'],
                                    config_data['data_collection'])

perceptron_db = db_helper.DBConnection(config_data['mongo_host'], config_data['mongo_port'],
                                       config_data['mongo_database'],
                                       config_data['metadata_collection'])

# Load global cached storage for uncommited NeuralNetwork objects (i.e. data currently being manipulated by users)
perceptron_cache = cache_helper.GlobalCacheHelper(max_size=int(config_data['flask_cache_max_size']))

# optionally populate the database with sample records and save a trained Perceptron Network to disk
if config_data['load_sample_network_on_start']:
    sample_data.setup_sample_neural_network.main()

app = flask.Flask(__name__)
app.config['DEBUG'] = False


@app.errorhandler(404)
@cross_origin()
def api_invalid_page(e):
    return {'status': APIResponseStatus.NOT_FOUND_404.value, 'error': str(e)}, 404


@app.route('/api/v1/perceptron', methods=['GET', 'POST'])
@cross_origin()
def api_status_check():
    """
    Root endpoint which can be used to determine basic API status.

    This method can also be used as a template for other endpoints.

    :return:
    """
    resp = {"status": APIResponseStatus.OK.value}
    status_code = 200
    try:
        # TODO: (optional) Perform several internal API functions to verify "sanity checks" here
        pass
    except AttributeError and ValueError:
        resp.update({"status": APIResponseStatus.ERROR.value})
        status_code = 400
    return resp, status_code


@app.route('/api/v1/perceptron/records/random', methods=['GET', 'POST'])
@app.route('/api/v1/perceptron/records', methods=['GET', 'POST'])
@cross_origin()
def records_query():
    """
    Allows the API to query the DB for testing/training records which match the provided arguments

    :return:
    """
    req_rng = 'random' in flask.request.url_rule.rule
    max_records = 0
    request_json = flask.request.get_json()
    if request_json is None:
        request_json = dict(flask.request.values)
    if req_rng and 'max' not in request_json:
        return {"status": APIResponseStatus.MISSING_ARGS.value}, 400
    resp = {"status": APIResponseStatus.OK.value}
    status_code = 200
    try:
        if req_rng:
            max_records = int(request_json["max"])
            request_json.pop("max")
        records = list()
        for record in records_db.read_documents(request_json):
            record.pop("_id")
            records.append(record)
        if req_rng:
            records = random.sample(records, min([max_records, len(records)]))
        resp.update({"filter": request_json, "records": records})
    except AttributeError:
        resp.update({"status": APIResponseStatus.ERROR.value})
        status_code = 400
    return resp, status_code


@app.route('/api/v1/perceptron/metadata', methods=['GET', 'POST'])
@cross_origin()
def metadata_query():
    """
    Returns a list of records from the AI metadata collection, which map network names to their serialized file

    :return:
    """
    resp = {"status": APIResponseStatus.OK.value}
    status_code = 200
    try:
        records = list()
        for record in perceptron_db.read_documents(dict(flask.request.args)):
            record.pop("_id")
            records.append(record)
        resp.update({"records": records})
    except AttributeError and ValueError:
        resp.update({"status": APIResponseStatus.ERROR.value})
        status_code = 400
    return resp, status_code


@app.route('/api/v1/perceptron/update', methods=['GET', 'POST'])
@app.route('/api/v1/perceptron/create', methods=['GET', 'POST'])
@cross_origin()
def create_neural_network():
    """
    Creates a new NeuralNetwork object with the given parameters, saving the serailized object to disk and creating a
    metadata entry in the db. The NeuralNetwork object is then loaded into global cache for further operations.

    :return:
    """
    # TODO: This method should require a token or other authentication
    resp = {'status': APIResponseStatus.OK.value}
    status_code = 200
    required_args = {"name", "input", "hidden", "output", "learningrate"}
    update_request = 'update' in flask.request.url_rule.rule
    db_record_exists = perceptron_db.record_exists({"network_id": flask.request.args['name']})
    if required_args.intersection(set(flask.request.args)) == required_args:
        if db_record_exists and not update_request:
            return {'status': APIResponseStatus.ERROR_DUPLICATE_ENTRY.value}, 400
        elif not db_record_exists and update_request:
            update_request = False  # treat as a new network to create if no record currently exists
        try:
            # create new network class object with provided params
            new_neural_network = NeuralNetwork(int(flask.request.args['input']),
                                               int(flask.request.args['hidden']),
                                               int(flask.request.args['output']),
                                               float(flask.request.args['learningrate']))
            # setup metadata entry for tracking serialized file location via the db
            network_storage_document = {"network_id": flask.request.args['name'],
                                        "saved_data": "{0}/{1}_{2}_perceptron_network.bin".format(
                                            config_data['trained_networks_directory'],
                                            uuid.uuid1(),
                                            flask.request.args['name'])}
            # load the newly generated network into the global cache for fast access (i.e. for training operations)
            perceptron_cache.add(network_storage_document['network_id'], (new_neural_network,
                                                                          network_storage_document['saved_data']))
            # create a snapshot of the initialized class object and serialize it to the location given in the metadata
            io_helper.save_pretrained_network(new_neural_network, network_storage_document['saved_data'])
            # save metadata entry to db
            if update_request:
                # cleanup the old serialized object from disk, then replace its metadata entry as well
                os.remove(perceptron_db.read_document({"network_id": flask.request.args['name']})["saved_data"])
                db_update_count = perceptron_db.update_document({"network_id": flask.request.args['name']},
                                                                network_storage_document)
                resp.update({'documents_updated': db_update_count})
            else:
                db_storage_id = perceptron_db.write_document(network_storage_document)
                resp.update({'document_id': str(db_storage_id)})

        except ValueError:
            resp.update({'status': APIResponseStatus.VALUE_ERROR.value})
            status_code = 400
    else:
        resp.update({'status': APIResponseStatus.NO_ID_ERROR.value})
        status_code = 400
    return resp, status_code


@app.route('/api/v1/perceptron/commit', methods=['GET', 'POST'])
@cross_origin()
def commit_network_training():
    """
    Forces any operations done to a NeuralNetwork object while in the global cache to be written to disk. The object is
    removed (popped) from the global cache in the process.
    This can be called after training a network to ensure that the new weights are stored to disk.

    :return:
    """
    resp = {'status': APIResponseStatus.OK.value}
    status_code = 200
    if "name" in flask.request.args:
        # Remove cached instance and commit to file (if cached)
        if flask.request.args['name'] in perceptron_cache.keys():
            cached_network = perceptron_cache.pop(flask.request.args['name'])
            io_helper.save_pretrained_network(cached_network[0], cached_network[1])
            resp.update({"network": cached_network[1]})
        else:
            resp.update({'status': APIResponseStatus.NO_UNCOMMITED_CHANGES.value})
            status_code = 400
    else:
        resp.update({'status': APIResponseStatus.MISSING_ARGS.value})
        status_code = 400
    return resp, status_code


@app.route('/api/v1/perceptron/query', methods=['GET', 'POST'])
@app.route('/api/v1/perceptron/train', methods=['GET', 'POST'])
@cross_origin()
def query_neural_network():
    """
    Handles querying and training of a stored NeuralNetwork object.

    If accessed on the "query" endpoint only a list of
    feature values is required, for which the response will contain an identified class as well as raw network outputs.

    If accessed on the "train" endpoint, a list of features as well as a target class is required. The network will
    internally query itself using the feature values, then correct the internal weights based on the relative error from
    the target class.

    :return: JSON response with either an "OK" status for training or a network response for queries
    """
    # setup the response and validate the required arguments
    resp = {'status': APIResponseStatus.OK.value}
    status_code = 200
    required_args = {"name", "features"}
    training_request = 'train' in flask.request.url_rule.rule
    request_json = flask.request.get_json()
    if request_json is None:
        return {'status': APIResponseStatus.ERROR.value}, 400
    if training_request:
        required_args.add("target")
    if required_args.intersection(set(request_json)) == required_args:
        perceptron_network, save_data_path = None, None
        # Look for the requested Perceptron Network in the cache, othwerise load it from disk based on db metadata
        if request_json['name'] in perceptron_cache.keys():
            cached_perceptron_network = perceptron_cache.read(request_json['name'])
            perceptron_network = cached_perceptron_network[0]
            save_data_path = cached_perceptron_network[1]
        else:
            if perceptron_db.record_exists({"network_id": request_json['name']}):
                perceptron_network_doc = perceptron_db.read_document({"network_id": request_json['name']})
                perceptron_network = io_helper.load_pretrained_network(perceptron_network_doc['saved_data'])
                save_data_path = perceptron_network_doc['saved_data']
        if perceptron_network is not None:
            try:
                # Based on the endpoint used, 'features' will either be used to query the network for a classification,
                # or used to train the network towards a provided target class
                inputs = numpy.asfarray(request_json['features'].strip(",").split(','))  # TODO: Improve parsing method
                if training_request:  # Updates the internal network weights after the query is complete
                    target_class = int(request_json['target'])
                    perceptron_network.train(inputs, target_class)
                else:  # Query the network to receive a classification only
                    network_outputs = perceptron_network.query(inputs)
                    resp.update({"identified_class": int(numpy.argmax(network_outputs)),
                                 "raw_network_output": network_outputs.T.tolist()})
                # Place recently queried network into cache (overwrite if already in cache)
                perceptron_cache.add(request_json['name'], (perceptron_network, save_data_path))
            except ValueError:  # unexpected values were passed in the request, i.e. chars, additional punctuation, etc.
                resp.update({'status': APIResponseStatus.VALUE_ERROR.value})
                status_code = 400
        else:  # the requested network was NOT found in either global cache or via a db entry
            resp.update({'status': APIResponseStatus.NO_RECORD.value})
            status_code = 400
    else:  # the request did not provide all of the required arguments
        resp.update({'status': APIResponseStatus.MISSING_ARGS.value})
        status_code = 400
    return resp, status_code


@app.route('/api/v1/perceptron/delete', methods=['GET', 'POST'])
@cross_origin()
def delete_neural_network():
    # setup the response and validate the required arguments
    resp = {'status': APIResponseStatus.OK.value, "deleted_count": 0}
    status_code = 200
    required_args = {"name"}
    if required_args.intersection(set(flask.request.args)) == required_args:
        try:
            if flask.request.args['name'] in perceptron_cache.keys():
                perceptron_cache.pop(flask.request.args['name'])
            if perceptron_db.record_exists({'network_id': flask.request.args['name']}):
                os.remove(perceptron_db.read_document({'network_id': flask.request.args['name']})["saved_data"])
                deleted_count = perceptron_db.remove_document({'network_id': flask.request.args['name']})
                resp.update({"deleted_count": deleted_count})
        except ValueError:
            resp.update({'status': APIResponseStatus.VALUE_ERROR.value})
            status_code = 400
    else:
        resp.update({'status': APIResponseStatus.NO_ID_ERROR.value})
        status_code = 400
    return resp, status_code


# Optional debug endpoints for directly interacting with the backend database
@app.route('/api/v1/perceptron/dbtest', methods=['GET', 'POST'])
def api_db_check():
    if config_data['flask_enable_debug_endpoints']:
        resp, status_code = debug_helper.api_db_check(records_db, flask.request.args)
    else:
        resp, status_code = {'status': APIResponseStatus.DEBUG_DISABLED.value}, 400
    return resp, status_code


@app.route('/api/v1/read', methods=['GET', 'POST'])
def mongo_db_read_documents():
    if config_data['flask_enable_debug_endpoints']:
        resp, status_code = debug_helper.mongo_db_read_documents(records_db, perceptron_db, flask.request.args), 200
    else:
        resp, status_code = {'status': APIResponseStatus.DEBUG_DISABLED.value}, 400
    return resp, status_code


@app.route('/api/v1/write', methods=['GET', 'POST'])
def mongo_db_write_document():
    if config_data['flask_enable_debug_endpoints']:
        resp, status_code = debug_helper.mongo_db_write_document(records_db, flask.request.args), 200
    else:
        resp, status_code = {'status': APIResponseStatus.DEBUG_DISABLED.value}, 400
    return resp, status_code


@app.route('/api/v1/delete', methods=['GET', 'POST'])
def mongo_db_delete_document():
    if config_data['flask_enable_debug_endpoints']:
        resp, status_code = debug_helper.mongo_db_delete_document(records_db, perceptron_db, flask.request.args), 200
    else:
        resp, status_code = {'status': APIResponseStatus.DEBUG_DISABLED.value}, 400
    return resp, status_code


if __name__ == "__main__":
    app.run(config_data['flask_host'], config_data['flask_port'])
