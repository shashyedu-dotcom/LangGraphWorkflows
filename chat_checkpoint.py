from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient
from typing import List, Annotated, Optional
from openai import OpenAI
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()


llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai"
)

client = OpenAI()


#declare state
class State(TypedDict):
    messages: Annotated[List, add_messages]

#declare nodes function
def ChatBotNode(state: State):
    response = llm.invoke(state.get("messages", []))
    return {"messages": [response]}

graph_builder = StateGraph(State)

#add nodes
graph_builder.add_node("ChatBotNode", ChatBotNode)

#add edges

graph_builder.add_edge(START, "ChatBotNode")
graph_builder.add_edge("ChatBotNode", END)

graph = graph_builder.compile()
#declare and compile graph with mongodb storage

def compile_graph_with_checkpointer(checkpoint):
    graph = graph_builder.compile(checkpointer=checkpoint)
    return graph

#create client with localhost url, set config with thread id
DB_URL = "mongodb://admin:admin@localhost:27017"

# mongo_client = MongoClient(DB_URL)

# checkpointer = MongoDBSaver(mongo_client,db_name="langraph_db",collection_name="checkpoints")

with MongoDBSaver.from_conn_string(DB_URL) as saver:
    graph_with_checkpointer = compile_graph_with_checkpointer(saver)

    config = {
        "configurable": {
            "thread_id": "chat_thread_1"
        }
    }

    updatedState = graph_with_checkpointer.invoke(State(messages=[{"role": "user", "content": "what is my name?"}]),config=config )
    print("\n\nUpdated State: ", updatedState)

