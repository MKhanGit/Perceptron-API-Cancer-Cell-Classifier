from APIHelpers import APIResponseStatus


def api_db_check(records_db, args):
    resp = {"status": APIResponseStatus.OK.value}
    status_code = 200
    try:
        inserted_id = str(records_db.write_document(dict(args)))
        resp.update({"db_write_status": inserted_id})
    except TimeoutError:
        status_code = 400
        resp.update({"db_write_status": "TimeoutError",
                     "status": APIResponseStatus.NOK.value})
    try:
        retreived_record = records_db.read_document(dict(args))
        retreived_record.pop("_id")
        resp.update({"db_read_status": retreived_record})
    except ValueError:
        status_code = 400
        resp.update({"db_read_status": "ValueError",
                     "status": APIResponseStatus.NOK.value})
    return resp, status_code


def mongo_db_read_documents(records_db, perceptron_db, args):
    resp = records_db.read_documents(args)
    records = []
    for record in resp:
        record["_id"] = str(record["_id"])
        records.append(record)
    resp = perceptron_db.read_documents(args)
    recordsai = []
    for record in resp:
        record["_id"] = str(record["_id"])
        recordsai.append(record)
    return {"records": records,
            "recordsai": recordsai}


def mongo_db_write_document(records_db, args):
    document = dict(args)
    document_db_id = records_db.write_document(document)
    resp = {
        "document_id": str(document_db_id),
        "status": APIResponseStatus.OK.value
    }
    return resp


def mongo_db_delete_document(records_db, perceptron_db, args):
    delete_count = records_db.remove_documents(dict(args))
    delete_count_ai = perceptron_db.remove_documents(dict(args))
    resp = {
        "deleted_count": delete_count,
        "delete_count_ai": delete_count_ai,
        "status": APIResponseStatus.OK.value
    }
    return resp
