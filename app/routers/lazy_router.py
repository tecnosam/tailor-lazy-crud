from typing import Any
from uuid import UUID

from starlette.requests import Request

from pydantic import ValidationError

from fastapi import (
    APIRouter,
    Path,
    Query,
    Body,
    HTTPException,

    UploadFile
)

from app.models import (
    User,
    Tailor,
    Product,
    Order,
)

from app.utils.mongo_utils import (
    get_documents,
    get_document_by_id,
    add_to_db,
    update_document,
    delete_document,

    db
)

from app.utils.file_utils import (
    upload_from_stream
)


router = APIRouter(prefix='/api/lazy', tags=['Lazy Router'])

lazy_map = {
    'users': {'model': User, 'key': 'users', 'unique': ['email']},
    'tailors': {'model': Tailor, 'key': 'tailors', 'unique': ['email']},
    'products': {'model': Product, 'key': 'products'},
    'orders': {
        'model': Order,
        'key': 'orders',
        'lookups': {
            'product_id': 'products.id',
            'tailor_id': 'tailors.id',
            'user_id': 'users.id'
        }
    }
}


for value in lazy_map.values():

    if 'unique' in value:

        key = value['key']
        for field in value['unique']:
            db[key].create_index(field, unique=True)


@router.get("/{resource}")
def get_resource_route(
    resource: str = Path()
):

    lazy_args = lazy_map[resource]
    key = lazy_args['key']

    lookups = lazy_args.get('lookups')
    return get_documents(key, {}, lookups)


@router.get('/{resource}/{resourceId}')
def get_single_resource_route(
    resource: str = Path(),
    resourceId: str = Path()
):
    lazy_args = lazy_map[resource]
    key = lazy_args['key']
    return get_document_by_id(key, resourceId)


@router.post("/{resource}")
async def add_resource_route(
    *,
    resource: str = Path(),
    body: Any = Body(None)
):

    try:
        lazy_args = lazy_map[resource]

        Model = lazy_args['model']
        key = lazy_args['key']

        value = Model(**body).model_dump()
        print(value)

        response = add_to_db(key, {**value})

        if response == -1 or response is None:

            raise HTTPException(
                status_code=400,
                detail=f"{resource}: Value already exists"
            )

        return value
    except ValidationError as exc:

        raise HTTPException(
            status_code=412,
            detail=exc.errors()
        )


@router.post("/{resource}/{resourceId}/add-image")
def upload_image_route(
    *,
    resource: str = Path(),
    resourceId: str = Path(),
    file: UploadFile
):

    lazy_args = lazy_map[resource]

    key = lazy_args['key']

    url = upload_from_stream(
        stream=file.file,
        public_id=f"{resourceId}-{file.filename}",
        folder=f"stylors/lazy/{resource}"
    )

    response = add_to_db(
        f"{key}.images",
        {'url': url},
        {'id': resourceId}
    )

    print("Response from images", response)

    return True


@router.put("/{resource}/{resourceId}")
async def update_resource_route(
    body: Any = Body(None),
    resource: str = Path(),
    resourceId: str = Path()
):

    try:
        lazy_args = lazy_map[resource]

        Model = lazy_args['model']
        key = lazy_args['key']

        value = Model(**body).model_dump()

        response = update_document(
            key,
            {'id': resourceId},
            value
        )

        if response == -1 or response is None:

            raise HTTPException(
                status_code=400,
                detail="Entity already exists"
            )

        return True
    except ValidationError as exc:

        raise HTTPException(
            status_code=412,
            detail=exc.errors()
        )


@router.delete("/{resource}/{resourceId}/remove-image")
def delete_image_route(
    resource: str = Path(),
    resourceId: str = Path(),

    image_url: str = Query()
):

    lazy_args = lazy_map[resource]

    key = lazy_args['key']

    delete_document(f"{key}.images", {'url': image_url})

    return True


@router.delete("/{resource}/{resourceId}")
def delete_resource_route(
    resource: str = Path(),
    resourceId: str = Path()
):

    lazy_args = lazy_map[resource]
    key = lazy_args['key']
    delete_document(key, {'id': resourceId})

    return True
