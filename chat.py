from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from typing import List, Annotated
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()


llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai"
)
#declare state
class State(TypedDict):
    messages: Annotated[List, add_messages]

#declare nodes function
def ChatBotNode(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def SampleBotNde(state: State):
    print("Entered sample bot ", state)
    return {"messages": ["Hello, how can I help you?"]}

graph_builder = StateGraph(State)

#add nodes
graph_builder.add_node("ChatBotNode", ChatBotNode)
graph_builder.add_node("SampleBotNde", SampleBotNde)

#add edges

graph_builder.add_edge(START, "ChatBotNode")
graph_builder.add_edge("ChatBotNode","SampleBotNde")
graph_builder.add_edge("SampleBotNde", END)

#declare graph
graph = graph_builder.compile()

updatedState = graph.invoke(State(messages=["Hello, I am a chatbot. How can I assist you?"]))
print("\n\nUpdated State: ", updatedState)

