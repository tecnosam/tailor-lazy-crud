from pymongo import MongoClient

from pymongo.errors import DuplicateKeyError

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

    try:
        if 'id' in document:
            document['id'] = str(document['id'])

        result = db[collection].insert_one(document)
        return result
    except DuplicateKeyError:

        return -1


def __push_to_array(
    collection,
    field,
    obj,
    query
):

    if 'id' in obj:
        obj['id'] = str(obj['id'])

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

        return __push_to_array(
            collection,
            field,
            value,
            query
        )

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


def get_documents(
    collection: str,
    query: dict,
    lookups: dict = None
):

    if __is_field(collection):

        collection, field = collection.split('.')

        results = get_objects_in_array(
            collection,
            field,
            query
        )

    else:

        pipeline = [
            {"$project": {'_id': 0}}
        ]

        if query:
            pipeline.append(
                {'$match': query}
            )

        if lookups:

            for field, foreign in lookups.items():

                foreign_collection, foreign_field = foreign.split('.')
                pipeline.append({
                    "$lookup": {
                        'from': foreign_collection,
                        'localField': field,
                        'foreignField': foreign_field,
                        'as': foreign_collection,
                        "pipeline": [
                            {"$project": {"_id": 0}}
                        ]
                    }
                })

            print(pipeline)

        results = db[collection].aggregate(pipeline)

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

    result = db[collection].find_one(query, {'_id': 0})
    return result


def get_document_by_id(collection, documentUUId):

    documentUUId = str(documentUUId)
    return get_document(collection, {'id': documentUUId})


def update_document(key, query, update):

    try:
        update.pop('id', '')

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
    except DuplicateKeyError:

        return -1


def delete_document(key, query):

    if __is_field(key):

        collection, field = key.split('.')

        return __delete_from_array(collection, field, query)

    return __delete_document(key, query)
