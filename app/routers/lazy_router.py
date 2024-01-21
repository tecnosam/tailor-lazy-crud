from typing import Any
from uuid import UUID

from starlette.requests import Request

from pydantic import ValidationError

from fastapi import (
    APIRouter,
    Path,
    Body,
    HTTPException
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
    delete_document
)


router = APIRouter(prefix='/api/lazy', tags=['Lazy Router'])

lazy_map = {
    'users': {'model': User, 'key': 'users'},
    'tailors': {'model': Tailor, 'key': 'tailors'},
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

        return value
    except ValidationError as exc:

        raise HTTPException(
            status_code=412,
            detail=exc.errors()
        )


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

        update_document(
            key,
            {'id': resourceId},
            value
        )

        return True
    except ValidationError as exc:

        raise HTTPException(
            status_code=412,
            detail=exc.errors()
        )


@router.delete("/{resource}/{resourceId}")
def delete_resource_route(
    resource: str = Path(),
    resourceId: str = Path()
):

    lazy_args = lazy_map[resource]
    key = lazy_args['key']
    delete_document(key, {'id': resourceId})

    return True
