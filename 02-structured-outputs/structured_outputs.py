from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


load_dotenv()


class Country(BaseModel):
    """Information about a country."""

    name: str = Field(description="Name of the country")
    language: str = Field(description="Primary language of the country")
    capital: str = Field(description="Capital city of the country")


llm = ChatOpenAI(model="gpt-6-astra")

structured_llm = llm.with_structured_output(Country)

country = structured_llm.invoke("Tell me about France")

print(country)
print(country.name)
print(country.language)
print(country.capital)