import asyncio
from datetime import datetime
import os

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


class Size:
    """
    The size of the generated image.
    """

    square: str = "1024x1024"
    height_rectangle: str = "1024x1792"
    width_rectangle: str = "1792x1024"


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """

    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """

    standard: str = "standard"
    hd: str = "hd"


async def _save_images(attachments: list[Attachment]):
    # TODO:
    #  1. Create DIAL bucket client
    dial_bucket_client = DialBucketClient(api_key=API_KEY, base_url=DIAL_URL)
    #  2. Iterate through Images from attachments, download them and then save here
    async with dial_bucket_client:
        for attachment in attachments:
            if attachment.get("type", None) == "image/png":
                img_bytes = await dial_bucket_client.get_file(attachment.get("url"))

                img_file_name = os.path.basename(attachment.get("url"))

                with open(img_file_name, mode="wb") as f:
                    f.write(img_bytes)
                    print(f"Image has been saved: {img_file_name}")

    #  3. Print confirmation that image has been saved locally


def start() -> None:
    # TODO:
    #  1. Create DialModelClient
    dial_model_client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name="dall-e-3",
        api_key=API_KEY,
    )

    # --------------------------------------------------------------------------------
    #  2. Generate image for "Sunny day on Bali"
    # --------------------------------------------------------------------------------

    prompt = Message(
        role=Role.USER,
        content="Generate image for 'Sunny day on Bali'",
    )

    message = dial_model_client.get_completion(messages=[prompt])
    message_dict = message.to_dict()

    #  3. Get attachments from response and save generated message (use method `_save_images`)
    asyncio.run(_save_images(message_dict.get("custom_content").get("attachments")))

    # --------------------------------------------------------------------------------
    #  4. Try to configure the picture for output via `custom_fields` parameter.
    #    - Documentation: See `custom_fields`. https://dialx.ai/dial_api#operation/sendChatCompletionRequest
    # --------------------------------------------------------------------------------

    message = dial_model_client.get_completion(
        messages=[prompt],
        custom_fields={
            "style": Style.vivid,
        },
    )
    message_dict = message.to_dict()
    asyncio.run(_save_images(message_dict.get("custom_content").get("attachments")))

    # --------------------------------------------------------------------------------
    #  5. Test it with the 'imagegeneration@005' (Google image generation model)
    # --------------------------------------------------------------------------------

    dial_model_client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name="gpt-image-1.5-2025-12-16",
        api_key=API_KEY,
    )
    message = dial_model_client.get_completion(messages=[prompt])
    message_dict = message.to_dict()
    asyncio.run(_save_images(message_dict.get("custom_content").get("attachments")))


start()
