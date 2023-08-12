import langchain
from langchain import PromptTemplate, LLMChain
from langchain.llms import TextGen
from langchain.memory import ConversationSummaryBufferMemory, VectorStoreRetrieverMemory, CombinedMemory

from langchain.vectorstores import Chroma
from langchain.schema import messages_from_dict, messages_to_dict
import json
import os
from pathlib import Path

from langchain.embeddings import GPT4AllEmbeddings

def init_embeddings():
    # Initialize GPT4AllEmbeddings for language model embeddings
    gpt4all_embd = GPT4AllEmbeddings()

    # Create a Chroma vector store with the GPT4All embeddings  and set the directory of the database to db
    vectorstore = Chroma(persist_directory="db", embedding_function=gpt4all_embd)

    # Persist the vector store to disk for future usage
    vectorstore.persist()

    retriever = vectorstore.as_retriever(search_kwargs=dict(k=1))
    memory = VectorStoreRetrieverMemory(retriever=retriever, memory_key="chromadb", input_key="human_input", exclude_input_keys = ["chat_history"])
    return memory
     

def init_llm(model_url, debug):
    langchain.debug = debug

    template = """You are a chatbot having a conversation with a human.

    ### memory database: 
    {chromadb}

    ### Current Conversation:

    {chat_history}
    ### Human: 
    {human_input}
    ### RESPONSE:
    """

    # Create a PromptTemplate using the defined template
    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input", "chromadb"], template=template
    )
    llm = TextGen(model_url=model_url)
    
    #Memory
    short_term_memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=50, memory_key="chat_history", input_key="human_input")


    #Load the short term memory from files
    if os.path.exists("shortmem/moving_summary_buffer.dat"):
        f = open("shortmem/moving_summary_buffer.dat", "r")
        short_term_memory.moving_summary_buffer=str(f.read())
        f.close()

    if os.path.exists("shortmem/messages.json"):
        with Path("shortmem/messages.json").open("r") as f:
            loaded_messages = json.load(f)
        short_term_memory.chat_memory.messages = messages_from_dict(loaded_messages)
        f.close()


    vector_db = init_embeddings()
    memory = CombinedMemory(memories=[short_term_memory, vector_db])

    

    llm_chain = LLMChain(
        llm=llm, 
        memory=memory,
        prompt=prompt,
        verbose=True,                    
    )


    return llm_chain


def generate_llm(llm_chain, user_input):
    # Run the provided input through the LLMChain to generate a response

    Output = llm_chain.run(human_input=user_input)

    #Save the short term memory to files

    if not os.path.exists("shortmem"):
        os.makedirs("shortmem")

    f = open("shortmem/moving_summary_buffer.dat", "w")
    f.write(llm_chain.memory.memories[0].moving_summary_buffer)
    f.close()

    with Path("shortmem/messages.json").open("w") as f:
        json.dump(messages_to_dict(llm_chain.memory.memories[0].chat_memory.messages), f, indent=4)

    return Output