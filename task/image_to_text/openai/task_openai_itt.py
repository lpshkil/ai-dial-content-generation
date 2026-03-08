import base64
from pathlib import Path

from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.model_client import DialModelClient
from task._models.role import Role
from task.image_to_text.openai.message import (
    ContentedMessage,
    TxtContent,
    ImgContent,
    ImgUrl,
)


def start() -> None:
    project_root = Path(__file__).parent.parent.parent.parent
    image_path = project_root / "dialx-banner.png"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    # TODO:
    #  1. Create DialModelClient
    dial_client = DialModelClient(
        deployment_name="gpt-4o",
        api_key=API_KEY,
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
    )
    
    #--------------------------------------------------------------------------
    #  2. Call client to analise image:
    #    - try with base64 encoded format
    #--------------------------------------------------------------------------

    messages = []

    contented_message_base64 = ContentedMessage(
        role=Role.USER,
        content=[
            TxtContent("What is in this image?"),
            ImgContent(image_url=ImgUrl(f"data:image/png;base64,{base64_image}"))
        ]
    )

    messages.append(contented_message_base64)

    
    response_message = dial_client.get_completion(messages=messages)
    
    #--------------------------------------------------------------------------
    #  2. Call client to analise image:
    # - try with URL: https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg
    #--------------------------------------------------------------------------

    messages = []

    contented_message_url = ContentedMessage(
        role=Role.USER,
        content=[
            TxtContent("What is in this image?"),
            ImgContent(image_url=ImgUrl("https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg"))
        ]
    )

    messages.append(contented_message_url)
    response_message = dial_client.get_completion(messages=messages)

    #    
    #  ----------------------------------------------------------------------------------------------------------------
    #  Note: This approach embeds the image directly in the message as base64 data URL! Here we follow the OpenAI
    #        Specification but since requests are going to the DIAL Core, we can use different models and DIAL Core
    #        will adapt them to format Gemini or Anthropic is using. In case if we go directly to
    #        the https://api.anthropic.com/v1/complete we need to follow Anthropic request Specification (the same for gemini)



start()
