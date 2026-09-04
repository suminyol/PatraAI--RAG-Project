from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
data=PyPDFLoader("document loaders/deeplearning.pdf")
docs=data.load()
# text = "\n".join(doc.page_content for doc in docs)
splitter=RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks=splitter.split_documents(docs)
template=ChatPromptTemplate.from_messages([
    ("system","you are an Ai that summarizes the text"),("human","{data}")
])
model=GoogleGenerativeAI(model="gemini-3.5-flash-lite",temperature=0.1) 
prompt=template.format_messages(data=docs)
result = model.invoke(prompt)
print(result)