# -*- coding: utf-8 -*-
import os
from pathlib import Path
import argparse
import getpass
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from util import(
    load_tfc_data, 
    init_pinecone,
)
load_dotenv()
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY') or getpass.getpass('Enter Pinecone API Key: ')
BASE_URL = "https://tfc-taiwan.org.tw/"

    



def chunk2Doc(page, chunk, chunk_id):
    return Document(
        page_content=chunk,
        metadata={
            "id": f"{page['page_id']}-{chunk_id+1}",
            "title": page['title'],
            "url": f'{BASE_URL}/articles/{page["page_id"]}',
        }
    )


def upsert(args):
    tfc_data = load_tfc_data(args.input_file)
    index = init_pinecone(
        api_key=PINECONE_API_KEY,
        project_name=args.project_name, 
        model_name=args.embd_model,
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        length_function=len,
    )
    # embeddings = VoyageAIEmbeddings(model=args.embd_model)
    embeddings = HuggingFaceEmbeddings(model_name=args.embd_model)
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    
    documents = []
    uuids = []
    for page in tfc_data:
        chunks = text_splitter.split_text(page['content'])
        for chunk_id, chunk in enumerate(chunks):
            documents.append(chunk2Doc(page, chunk, chunk_id))
            uuids.append(f"{page['page_id']}-{chunk_id+1}")
    
    vector_store.add_documents(documents=documents, ids=uuids, namespace='tfc-taiwan')
    print(f"Added {len(documents)} chunks into Pinecone")
    

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_file',
        type=Path,
    )
    parser.add_argument(
        '--project_name',
        type=str,
        default='factcheck',
    )
    parser.add_argument(
        '--embd_model',
        type=str,
        default='intfloat/multilingual-e5-small'
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = arg_parse()
    upsert(args)