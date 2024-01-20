from pymongo import MongoClient

from uuid import UUID


client = MongoClient()

db = client['stylors']


def __is_field(key: str):

    """
        If the key is a field
        and not a collection
    """

    return '.' in key


def __push_document(
    collection,
    document,
):

    result = db[collection].insert_one(document)
    return result


def __push_to_array(
    collection,
    field,
    obj,
    query
):

    update = {'$push': {field: obj}}

    result = db[collection].update_one(query, update)

    return True


def __delete_document(collection, query):

    result = db[collection].delete_one(query)
    return result


def __delete_from_array(
    collection,
    field,
    query
):

    update = {'$pull': {field: query}}

    result = db[collection].update_many({}, update)

    return True


def add_to_db(key, value, query=None):

    query = query if query else {}

    if __is_field(key):

        collection, field = key.split('.')

        __push_to_array(
            collection,
            field,
            value,
            query
        )

        return True

    return __push_document(key, value)


def get_objects_in_array(collection, field, query):
    pipeline = [
        {'$match': {field: {'$exists': True}}},
        {'$unwind': f"${field}"},
    ]

    if query:
        for k, v in query.items():

            pipeline.append({'$match': {f"{field}.{k}": v}})

    results = db[collection].aggregate(pipeline)

    return results


def get_documents(collection, query):

    if __is_field(collection):

        collection, field = collection.split('.')

        results = get_objects_in_array(
            collection,
            field,
            query
        )

    else:
        results = db[collection].find(query)

    return list(results)


def get_document(collection, query):

    if __is_field(collection):

        try:
            collection, field = collection.split('.')

            results = get_objects_in_array(
                collection,
                field,
                query
            )

            return next(results)
        except StopIteration:
            return None

    result = db[collection].find_one(query)
    return result


def get_document_by_id(collection, documentUUId):

    documentUUId = UUID(documentUUId)
    return get_document(collection, {'id': documentUUId})


def update_document(key, query, update):

    if __is_field(key):

        collection, field = key.split('.')

        query = {
            f'{field}.{k}': v
            for k, v in query.items()
        }

        update = {
            f'{field}.$.{k}': v
            for k, v in update.items()
        }

        return db[collection].update_many(
            query,
            {"$set": update}
        )

    return db[key].update_one(
        query,
        {'$set': update}
    )


def delete_document(key, query):

    if __is_field(key):

        collection, field = key.split('.')

        return __delete_from_array(collection, field, query)

    return __delete_document(key, query)
