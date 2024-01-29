
import cloudinary
from cloudinary.uploader import upload

import csv
# from cloudinary.utils import cloudinary_url

from app.utils.settings import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET
)


def upload_from_stream(
    stream,
    public_id: str,
    folder: str = "election_data"
):
    try:

        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )

        res = upload(
            stream,
            folder=folder,
            public_id=public_id,
            overwrite=True,
            resource_type='image'
        )

        return res['url']
    except Exception as e:
        print(e)
        return None


def csv_to_dict(data: str):
    data = data.split("\n")

    reader = csv.DictReader(data)

    return [dict(row) for row in reader]
