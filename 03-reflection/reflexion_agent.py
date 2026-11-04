from typing import TypedDict

from dotenv import load_dotenv
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


load_dotenv()


# 1. Structured response

class Reflection(BaseModel):
    missing: str
    unnecessary: str


class Answer(BaseModel):
    answer: str
    reflection: Reflection
    search_queries: list[str]
    references: list[str] = Field(
        description="Sources used, or an empty list"
    )


# 2. Graph state

class State(TypedDict, total=False):
    question: str
    response: Answer
    search_results: list
    iteration: int


# 3. Model and search tool

llm = ChatOpenAI(model="gpt-6-astra")
structured_llm = llm.with_structured_output(Answer)

search_tool = TavilySearchResults(max_results=3)


# 4. Create the initial answer
def draft(state: State):
    response = structured_llm.invoke(
        f"""
        Answer this question:

        {state["question"]}

        Also:
        - Critique what is missing.
        - Identify unnecessary information.
        - Generate 1-3 search queries.
        - Return an empty references list.
        """
    )

    return {
        "response": response,
        "iteration": 0,
    }


# 5. Execute the searches

def research(state: State):
    results = []

    for query in state["response"].search_queries:
        results.extend(search_tool.invoke(query))

    return {"search_results": results}


# 6. Revise using the search results

def revise(state: State):
    previous = state["response"]

    response = structured_llm.invoke(
        f"""
        Question:
        {state["question"]}

        Previous answer:
        {previous.answer}

        What was missing:
        {previous.reflection.missing}

        Unnecessary information:
        {previous.reflection.unnecessary}

        Search results:
        {state["search_results"]}

        Revise the answer using the search results.
        Include source URLs in references.
        Critique the new answer and generate new search queries.
        """
    )

    return {
        "response": response,
        "iteration": state["iteration"] + 1,
    }


# 7. Decide whether to repeat

def should_continue(state: State):
    if state["iteration"] >= 2:
        return END

    return "research"


# 8. Build the graph

graph = StateGraph(State)

graph.add_node("draft", draft)
graph.add_node("research", research)
graph.add_node("revise", revise)

graph.add_edge(START, "draft")
graph.add_edge("draft", "research")
graph.add_edge("research", "revise")
graph.add_conditional_edges("revise", should_continue)

app = graph.compile()


# 9. Run the agent

result = app.invoke(
    {
        "question": "How can small businesses use AI to grow?"
    }
)

print(result["response"].answer)

print("\nReferences:")
for reference in result["response"].references:
    print(reference)