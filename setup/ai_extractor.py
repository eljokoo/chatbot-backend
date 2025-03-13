import os

from dotenv import load_dotenv
from langchain.chains import create_extraction_chain
from langchain_deepseek import ChatDeepSeek
from langchain_dartmouth.llms import ChatDartmouthCloud

load_dotenv()

# llm = ChatDeepSeek(model="deepseek-chat",
#                    api_key=os.getenv('DEEPSEEK-API-KEY'))

llm = ChatDartmouthCloud(dartmouth_chat_api_key=os.getenv('DARTMOUTH_CHAT_API_KEY'), model_name="openai.gpt-4o-mini-2024-07-18")

def extract(content: str, **kwargs):
    """
    The `extract` function takes in a string `content` and additional keyword arguments, and returns the
    extracted data based on the provided schema.
    """

    # This part just formats the output from a Pydantic class
    if 'schema_pydantic' in kwargs:
        response = create_extraction_chain(
            pydantic_schema=kwargs["schema_pydantic"], llm=llm).invoke(content)
        response_as_dict = [item.dict() for item in response]

        return response_as_dict
    else:
        return llm.with_structured_output(kwargs["schema"]).invoke(content)
