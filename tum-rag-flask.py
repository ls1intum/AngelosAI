import os
import openai
import tiktoken
import re
import numpy as np
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from bs4 import BeautifulSoup
import urllib3

# Suppress only the unverified HTTPS request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not found. Please set it in the .env file.")

openai.api_key = openai_api_key

# Function to calculate cosine similarity
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

#### INDEXING ####

# Load all PDF documents from the "knowledge" folder
def load_pdfs_from_folder(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            loader = PyPDFLoader(file_path)
            loaded_docs = loader.load()
            documents.extend(loaded_docs)  # Extend with the loaded pages
            print(f"Loaded {len(loaded_docs)} pages from {filename}")
    return documents


def load_links_from_file(file_path):
    def extract_course_name(content):
        # Extract the course name between "Name" and "Organisation"
        match = re.search(r"Name\s*(.*?)\s*Organisation", content)
        if match:
            return match.group(1).strip()
        return None

    def insert_course_name(content, course_name):
        sections = [
            "Voraussetzungen",
            "Arbeitsaufwand",
            "Angestrebte Lernergebnisse",
            "Inhalt",
            "Lehr- und Lernmethode"
        ]
        for section in sections:
            pattern = re.compile(f"({section})", re.IGNORECASE)
            # Substitute section name with section name followed by the course name
            content = pattern.sub(f"\\1 {course_name}", content)
        return content

    documents = []

    with open(file_path, 'r') as file:
        urls = file.readlines()
        for url in urls:
            url = url.strip()
            if url:
                # Fetch the original content with WebBaseLoader
                loader = WebBaseLoader(
                    web_paths=(url,),
                )
                loader.requests_kwargs = {'verify': False}
                loaded_docs = loader.load()

                for doc in loaded_docs:
                    # Clean up the page content
                    cleaned_content = re.sub(r'\s+', ' ', doc.page_content).strip()
                    # Extract course name
                    course_name = extract_course_name(cleaned_content)
                    if course_name:
                        # Insert course name at relevant sections
                        updated_content = insert_course_name(cleaned_content, course_name)
                        #print(updated_content)
                        doc.page_content = updated_content
                        documents.append(doc)

                #print(f"Loaded {len(loaded_docs)} documents from {url}")
                #print("----------")
    
    return documents


# Get the absolute path to the knowledge folder
current_dir = os.path.dirname(os.path.abspath(__file__))
knowledge_folder = os.path.join(current_dir, "knowledge")
print(f"Loading PDF documents from the knowledge folder at: {knowledge_folder}")

docs = load_pdfs_from_folder(knowledge_folder)
pdf_doc_count = len(docs)
print(f"Loaded {pdf_doc_count} PDF documents.")

# Load links from the links.txt file
docs2 = []
links_file_path = os.path.join(knowledge_folder, "links.txt")
if os.path.exists(links_file_path):
    link_docs = load_links_from_file(links_file_path)
    docs2 = link_docs
    link_doc_count = len(link_docs)
    print(f"Loaded {link_doc_count} documents from links.")
else:
    link_doc_count = 0
    print(f"No links file found at {links_file_path}")

total_docs_count = len(docs) + len(docs2)
print(f"Total loaded documents: {total_docs_count}")
print(f"Orga documents: {len(docs)}")
print(f"Detail documents: {len(docs2)}")

# Split Documents
print("Splitting documents...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
text_splitter2 = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
splits2 = text_splitter2.split_documents(docs2)
print(f"Documents split into {len(splits)} chunks.")
print(f"Detail Documents split into {len(splits2)} chunks.")

# Embed and Index Documents
print("Embedding and indexing documents...")
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(openai_api_key=openai_api_key), collection_name="organisation")
vectorstore2 = Chroma.from_documents(documents=splits2, embedding=OpenAIEmbeddings(openai_api_key=openai_api_key), collection_name="details")
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
retriever2 = vectorstore2.as_retriever(search_kwargs={"k": 3})
print(f"Number of documents in vector store: {len(vectorstore.get()['documents'])}")
print(f"Number of documents in second vector store: {len(vectorstore2.get()['documents'])}")
print("Documents embedded and indexed.")

#### RETRIEVAL and GENERATION ####

# Example Prompt Template
template_str = """Du bist Assistent und beantwortest Fragen von Informatik Studierenden der Technischen Universität München zu ihrem Bachelorstudium. 
Der Studienplan des Studiengangs beinhaltet Wahl- und Pflichtmodule. Spätestens zu Beginn des dritten Fachsemesters entscheiden sich Studierende für ein Anwendungsfach, Von den 21 Credits für ein Anwendungsfach müssen mindestens 6 Credits auf Pflichtmodule entfallen.
Du beantwortest Fragen in Deutsch auf Deutsch. Wenn die Frage nicht in dieses Setting passt und auch nicht im Entferntesten etwas mit dem Studium zu tun hat, antworte einfach: „Tut mir leid, das kann ich nicht beantworten. Ich bin hier, um Bachelorstudierenden der Informatik bei Fragen zu ihrem Studium an der TUM zu helfen.“
Andernfalls, also wenn doch, beantworte die Frage nur basierend auf dem folgenden Kontext:
Kontext: {context1}
{context2}

Frage: {question}
"""

# Set up Prompt
prompt = PromptTemplate(template=template_str)

# Set up LLM
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key)

# Function to format documents and limit context length to top k chunks based on similarity
def format_docs(query, docs, k=5):
    print(f"DOC LENGTH BEFORE FORMATTING: {len(docs)}")
    #embd = OpenAIEmbeddings(openai_api_key=openai_api_key)
    #query_embedding = embd.embed_query(query)
    
    #doc_embeddings = [embd.embed_query(doc.page_content) for doc in docs]
    #similarities = [cosine_similarity(query_embedding, doc_emb) for doc_emb in doc_embeddings]
    
    # Combine docs with their similarities
    #docs_with_similarities = list(zip(docs, similarities))
    
    # Sort documents by similarity in descending order
    #sorted_docs = sorted(docs_with_similarities, key=lambda x: x[1], reverse=True)
    
    # Select top k documents
    #top_docs = [doc for doc, _ in sorted_docs[:k]]
    
    return "\n\n".join(doc.page_content for doc in docs)

# Set up RAG Chain
print("Setting up RAG chain...")
rag_chain = (
    {"context1": RunnablePassthrough(),
     "context2": RunnablePassthrough(),
     "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
print("RAG chain set up.")

# Function to handle user questions
def handle_question(question):
    relevant_docs = retriever.get_relevant_documents(question)
    relevant_detail_docs = retriever2.get_relevant_documents(question)
    context = format_docs(question, relevant_docs, 5)
    print(f"ORGA CONTEXT: {context}")
    print("--")
    context2 = format_docs(question, relevant_detail_docs, 3)
    print(f"DETAIL CONTEXT: {context2}")


    #total_context = context + context2
    #print(f"Context for question: {context + context2}")
    prompt_text = prompt.format(context1=context, context2=context2, question=question)
    print("-----------------------")
    print("-----------------------")
    print(f"Prompt sent to OpenAI API: {prompt_text}")
    response = llm.invoke(prompt_text)  # Use invoke method
    return response.content  # Extract the content from the response
    #response = rag_chain.invoke({"context1": context, "context2": context2, "question": question})
    #return response['content']

# Flask setup
app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('message', '')
    if not question:
        return jsonify({"error": "No question provided"}), 400
    print(f"Received question: {question}")
    answer = handle_question(question)
    print(f"Generated answer: {answer}")
    return jsonify({"answer": answer})

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000)
