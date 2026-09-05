from langchain_community.vectorstores import Chroma
from langchain_mistralai import MistralAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
from langchain_core.documents import Document

docs = [
    Document(page_content="Gradient descent is an optimization algorithm used in machine learning."),
    Document(page_content="Gradient descent minimizes the loss function."),
    Document(page_content="Gradient descent is an optimization that minimizes the loss function."),
    Document(page_content="Neural networks use gradient descent for training."),
    Document(page_content="Support Vector Machines are supervised learning algorithms.")
]

embeddings=MistralAIEmbeddings()

vectorstore=Chroma.from_documents(docs,embeddings)

similarity_retrievers=vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k":3}
)
print("---------------Similarity Search--------------")

similarity_docs=similarity_retrievers.invoke("What is gradient descent ? ")

for i in similarity_docs:
    print(i.page_content)


mmr_retriever=vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k":3}
)
print("----------------MMR Retriever--------------")
mmr_docs=mmr_retriever.invoke("What is gradient descent ? ")

for i in mmr_docs:
    print(i.page_content)