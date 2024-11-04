import os
import getpass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from util import (
    get_retriever,
    format_docs,
    format_docs_web,
    get_web_retriever
)

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or getpass.getpass('Enter OPENAI API Key: ')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY') or getpass.getpass('Enter Pinecone API Key: ')
DEFAULT_QUERY = "為什麼只有台灣還有圖利罪？"
TEMPLATE = """你是一個事實查核機器人，以下提供來自 「台灣事實查核中心」的查核結果。請根據這些查核結果回答問題，或查核問題本身的真偽。如果相關資料可以回答問題或提供佐證，請用這些資料解答並科普，提供更多相關資訊給閱聽者，並附上連結（有相關的連結再附上就好！）。如果資料無法回答問題或判斷真偽，回傳 `doSearch: True`。如果最終無法回答，請回應「目前尚無機構對此案例做事實查核」。
請以 JSON 格式回答，其中包含 `response（對應回答）`: str 、`url`: List[str]、`doSearch`: True/False，以及 `confidence_score`: [0, 1]。
相關查核資訊：
{context}

待查核言論或提問: {question}
<Warning>請務必用繁體中文以及台灣用語思考並回答問題！！！！！
"""

TEMPLATE_FOR_WEBSEARCH = """
你是一個事實查核機器人，由於目前尚無機構對此案例做事實查核，我們從網路上收集以下相關資料。然而，這些資料的真實性「沒有」被證實。因此你只能資訊分享，告訴詢問者一些相關的報導、文章是如何闡述或說明這件事情。請務必告訴使用者斟酌參考，不能完全相信這些報導或文章。當然，你不能提供任何非客觀的意見和不存在的資訊。
相關網路資料：
{documents}

待查核言論或提問: {question}

<Warning>請務必用繁體中文以及台灣用語思考並回答問題！！！！！
"""

def checker(query):
    result = ""
    project = "factcheck"
    model = "intfloat/multilingual-e5-small"
    namespace = 'tfc-taiwan'
    if not query:
        query = DEFAULT_QUERY
    
    retriever = get_retriever(
        api_key=PINECONE_API_KEY,
        project_name=project,
        model_name=model,
        namespace=namespace,
        k=3,
    )

    llm_json = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY, model_kwargs={"response_format": {"type": "json_object"}},)
    llm_str = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)

    
    custom_rag_prompt = PromptTemplate.from_template(TEMPLATE)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | custom_rag_prompt
        | llm_json
        | JsonOutputParser()
    )

    response = rag_chain.invoke(query)

    if not response['doSearch']:
        result += response['response']
        result += "\n相關連結:\n"
        if isinstance(response['url'], list):
            result += "\n".join(response['url'])
        if isinstance(response['url'], str):
            result += response['url']
    else:
        result += 'No related information found in Pinecone. Do Web searching...'
        web_retriever = get_web_retriever()
        custom_rag_prompt_for_web_search = PromptTemplate.from_template(TEMPLATE_FOR_WEBSEARCH)
        reg_chain_for_web_search =(
            {"documents": web_retriever | format_docs_web, "question": RunnablePassthrough()}
            | custom_rag_prompt_for_web_search
            | llm_str
            | StrOutputParser()
        )
        response_for_websearch = reg_chain_for_web_search.invoke(query)
        result += response_for_websearch
    
    print(result)
    return result



if __name__ == "__main__":
    query = input(">>>")
    checker(query)