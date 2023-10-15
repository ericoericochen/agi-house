from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain.output_parsers import (
    PydanticOutputParser,
    CommaSeparatedListOutputParser,
)
from pydantic import BaseModel, Field, validator
from urllib.parse import urlparse, urljoin

import uuid


def get_base_url(url: str):
    # Parse the URL
    parsed_url = urlparse(url)

    # Get the base URL (scheme + netloc)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc + "/"

    return base_url


def is_html(url: str):
    response = requests.get(url)
    content_type = response.headers["content-type"]

    return content_type.startswith("text/html")


def get_links(url: str):
    base_url = get_base_url(url)
    response = requests.get(url)

    content_type = response.headers["content-type"]

    if not content_type.startswith("text/html"):
        return []

    results = []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")

    for link in links:
        if type(link) == str:
            continue

        href = link.get("href")
        if href:
            if not is_absolute_url(href):
                href = urljoin(base_url, href)

            if href.startswith(base_url) and href != base_url:
                results.append(href)

    results = [result for result in results if is_html(result)]
    return results


class JSONResponse(BaseModel):
    id: str = Field(default_factory=uuid.uuid4)
    method: str
    url: str
    # params: dict
    headers: dict
    human_readable_description: str
    source: str
    failure_and_suggestions: str

    @validator("url")
    def url_must_be_absolute(cls, v):
        if not is_absolute_url(v):
            raise ValueError("url must be absolute")
        return v

    @validator("method")
    def method_must_be_valid(cls, v):
        if v not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError("method must be valid")
        return v


class URLResponse(BaseModel):
    id: str = Field(default_factory=uuid.uuid4)
    url: str
    human_readable_description: str
    source: str
    failure_and_suggestions: str

    @validator("url")
    def url_must_be_absolute(cls, v):
        if not is_absolute_url(v):
            raise ValueError("url must be absolute")
        return v


class CodeResponse(BaseModel):
    code: str
    human_readable_description: str
    source: str
    failure_and_suggestions: str


JSON_PARSER = PydanticOutputParser(
    pydantic_object=JSONResponse,
)

CODE_PARSER = PydanticOutputParser(
    pydantic_object=CodeResponse,
)


def is_absolute_url(url):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)


API_PROMPT_TEMPLATE = PromptTemplate(
    template="""
        You are a developer who is trying to use an API. You are trying to figure out how to use the API to {question}. \
        From the API documentation, you've learned that you can use the following: {summaries}. \
        Please format as a json endpmoint query, like this: \
        \n \
        'METHOD': <method>, 'URL': <url>, 'PARAMS': <params>, 'HEADERS': <headers> \
        ---
        human readable description, and of where you found the answer, and why you think it's correct. \
        \n \
        If you cannot do this, please populate the 'failure_and_suggestions' struct: first write 'CANNOT DO' \
        
        format exactly as {format_instructions}
        """,
    input_variables=["summaries", "question"],
    partial_variables={"format_instructions": JSON_PARSER.get_format_instructions()},
)

CODE_PROMPT_TEMPLATE = PromptTemplate(
    template="""
        You are a developer who is trying to use an API. You are trying to figure out how to use the API to {question}. \
        From the API documentation, you've learned that you can use the following: {summaries}. \
        Please write a code snippet that uses the API to {question}, keeping in mind correctness and efficiency. \
        \n \
        If you cannot do this, please populate the 'failure_and_suggestions' struct: first write 'CANNOT DO' \
        
        format exactly as {format_instructions}
        """,
    input_variables=["summaries", "question"],
    partial_variables={"format_instructions": CODE_PARSER.get_format_instructions()},
)

LINK_PROMPT_TEMPLATE = PromptTemplate(
    template="Given that we could not solve the prompt {question}, please provide some links to urls from the context {summaries} \
        that you think could help us solve the prompt {format_instructions}",
    input_variables=["summaries", "question"],
    partial_variables={
        "format_instructions": CommaSeparatedListOutputParser().get_format_instructions()
    },
)
