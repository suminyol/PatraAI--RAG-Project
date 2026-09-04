from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
data=PyPDFLoader("document loaders/GRU.pdf")
docs=data.load()
text = "\n".join(doc.page_content for doc in docs)
temp=ChatPromptTemplate.from_messages([
    ("system","you are an Ai that summarizes the text"),("human","{data}")
])
model=GoogleGenerativeAI(model="gemini-3.5-flash-lite",temperature=0.8)
prompt=temp.format_messages(data=text)
result = model.invoke(prompt)
print(result)