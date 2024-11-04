import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from transformers import AutoConfig
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.tools import TavilySearchResults
load_dotenv()
BASE_URL = "https://tfc-taiwan.org.tw/articles"


def load_tfc_data(path):
    with open(path, 'r') as f:
        print(f'Load data from {path}')
        return json.load(f)

def load_existing_data():
    if os.path.exists(".src/tfc_data.json"):
        with open(".src/tfc_data.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_model_embedding_dimension(model_name: str) -> int:
    # Load the configuration of the model
    config = AutoConfig.from_pretrained(model_name)
    
    if hasattr(config, 'hidden_size'):
        return config.hidden_size
    elif hasattr(config, 'dim'):
        return config.dim
    elif hasattr(config, 'd_model'):
        return config.d_model
    else:
        raise ValueError(f"Unable to determine embedding dimension for model: {model_name}")

def init_pinecone(api_key, project_name='factcheck', model_name='intfloat/multilingual-e5-small'):
    index_name = f"{project_name}-{model_name.split('/')[-1]}"
    pc = Pinecone(api_key=api_key)
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=get_model_embedding_dimension(model_name),
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1',
            )
        )
    
    return pc.Index(index_name)

def get_web_retriever():
    return TavilySearchResults(
        max_results=3,
        include_answer=True,
        include_raw_content=True,
        include_images=True,
        # search_depth="advanced",
        # include_domains = []
        # exclude_domains = []
    )


def get_retriever(api_key, project_name, model_name, namespace, k):
    index_name = f"{project_name}-{model_name.split('/')[-1]}"
    pc = Pinecone(api_key=api_key)
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    
    assert index_name in existing_indexes, f"{index_name} not found in Pinecone"

    # print(f"Vectors in index {index_name}: {pc.Index(index_name).describe_index_stats()}")

    # Initialize the vector store and embedding model
    vector_store = PineconeVectorStore(index=pc.Index(index_name), embedding=HuggingFaceEmbeddings(model_name=model_name))

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k, "namespace": namespace})

    # retrieved_docs = retriever.invoke(query)
    # print(retrieved_docs)
    return retriever

def format_docs(docs):
    docs.sort(key=lambda doc: doc.metadata['id'], reverse=False)
    # combined_content = "\n\n".join(doc.page_content for doc in docs)
    # urls = list({doc.metadata['url'] for doc in docs})

    # return f"{combined_content}\n相關連結：\n{urls}"
    combined_content = ""
    for doc in docs:
        doc_id = doc.metadata['id'].split('-')[0]
        combined_content += f"{doc.page_content}\n"
        combined_content += f"Source: {BASE_URL}/{doc_id}\n"
    return combined_content

def format_docs_web(docs):
    return "\n\n".join(doc['content'] for doc in docs)

# G