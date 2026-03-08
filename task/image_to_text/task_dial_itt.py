import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = "dialx-banner.png"
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = "image/png"
    # TODO:
    #  1. Create DialBucketClient

    dial_bucket_client = DialBucketClient(api_key=API_KEY, base_url=DIAL_URL)

    #  2. Open image file
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    #  3. Use BytesIO to load bytes of image
    img_buffer = BytesIO(img_bytes)

    #  4. Upload file with client
    async with dial_bucket_client:
        response = await dial_bucket_client.put_file(
            name="dialx-banner", mime_type=mime_type_png, content=img_buffer
        )

        return Attachment(
            title=file_name,
            url=response.get("url"),
            type=mime_type_png,
        )

    #  5. Return Attachment object with title (file name), url and type (mime type)


def start() -> None:
    # TODO:
    #  1. Create DialModelClient
    dial_client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        api_key=API_KEY,
        deployment_name="gpt-4o",
    )

    #  2. Upload image (use `_put_image` method )
    attachment = asyncio.run(_put_image())

    #  3. Print attachment to see result
    print(attachment)

    #  4. Call chat completion via client with list containing one Message:
    #    - role: Role.USER
    #    - content: "What do you see on this picture?"
    #    - custom_content: CustomContent(attachments=[attachment])

    prompt = Message(
        role=Role.USER,
        content="What do you see on this picture?",
        custom_content=CustomContent(attachments=[attachment])
    )

    dial_client.get_completion(messages=[prompt])

    #  ---------------------------------------------------------------------------------------------------------------
    #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
    #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
    #        adapts this attachment to Message content in appropriate format for Model.


    #  TRY THIS APPROACH WITH DIFFERENT MODELS!
    dial_client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        api_key=API_KEY,
        deployment_name="gemini-2.0-flash-lite",
    )
    dial_client.get_completion(messages=[prompt])


    #  Optional: Try upload 2+ pictures for analysis


start()
