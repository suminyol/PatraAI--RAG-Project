from langchain_community.vectorstores import Chroma
from langchain_mistralai import ChatMistralAI
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()
from langchain_core.documents import Document
from langchain_classic.retrievers.multi_query import MultiQueryRetriever

docs = [
    Document(page_content="Gradient descent is an optimization algorithm used in machine learning."),
    Document(page_content="Gradient descent minimizes the loss function."),
    Document(page_content="Gradient descent is an optimization that minimizes the loss function."),
    Document(page_content="Neural networks use gradient descent for training."),
    Document(page_content="Support Vector Machines are supervised learning algorithms.")
]

embeddings = HuggingFaceEmbeddings()

vectorstore=Chroma.from_documents(docs,embeddings)

retriever=vectorstore.as_retriever()

llm=ChatMistralAI(model="voxtral-small-2507")

multiquery_retriever=MultiQueryRetriever.from_llm(retriever=retriever,llm=llm)

query="What is gradient descent?"

docs=multiquery_retriever.invoke(query)

for i in docs:
    print(i.page_content)