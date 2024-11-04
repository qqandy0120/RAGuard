import os
import getpass
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()
check = input("Are you sure you want to DELETE all data? Press y to delete")
if check is not 'y':
    pass
else:
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY') or getpass.getpass('Enter Pinecone API Key: ')
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("factcheck-multilingual-e5-small")
    index.delete(delete_all=True, namespace='tfc-taiwan')
    print("Deleted")
