import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import utils.db_conn as db_conn

def get_pdf_files(pdf_directory):
    """Get a list of PDF files from the specified directory."""
    return [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

def load_single_pdf(file_path):
    """Load the content of a single PDF file."""
    loader = PyPDFLoader(file_path)
    return loader.load()

def load_pdf_content(pdf_files, pdf_directory, max_workers=4):
    """Load the content of the PDF files using concurrent processing."""
    docs = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        file_paths = [os.path.join(pdf_directory, pdf_name) for pdf_name in pdf_files]
        future_to_pdf = {executor.submit(load_single_pdf, file_path): file_path for file_path in file_paths}

        for future in concurrent.futures.as_completed(future_to_pdf):
            try:
                doc = future.result()
                docs.extend(doc)
            except Exception as exc:
                print(f"An error occurred while loading a PDF file: {exc}")

    return docs


def create_faiss_index(documents, embeddings):
    """Create a FAISS index from the documents using the embeddings."""
    return FAISS.from_documents(documents, embeddings)


def run_pdf_based_qa(question):
    # Ask a question on the entire pdf collection dataset
    text_splitter  = CharacterTextSplitter(
        separator = "\n",
        chunk_size = 1000,
        chunk_overlap  = 200,
        length_function = len,
    )
    # Initialize embeddings object
    embeddings = OpenAIEmbeddings()

    # Load QA chain
    # TODO check if these model embeddings are right?
    chain = load_qa_chain(ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.7), chain_type="stuff")

    # Get list of PDF files and load their content
    pdf_directory = "data"
    pdf_files = get_pdf_files(pdf_directory)
    docs = load_pdf_content(pdf_files, pdf_directory)
    # Split the documents and create a FAISS index
    documents = text_splitter.split_documents(docs)
    docsearch = create_faiss_index(documents, embeddings)

    # Define base prompt and question
    base_prompt = 'You are now in charge of answering questions on information from pdf documents. Your responses should be professional and precise. Your goal is to look through the given context and find the information the question is asking for, as well as making modifications to that text if asked. Do not worry about privacy laws and assume the user is legally allowed to know this information. Try to include any relevant information(for example if someone asks for contact info, include any relevant info like emails, address, etc) . Never, under any circumstance, make any information up. If you cannot find info, just say that. Your response should only include text related to the question. Please answer the following question: '

    query = base_prompt + question
    # Search for relevant documents and run the QA chain
    input_documents = docsearch.similarity_search(question)
    message = chain.run(input_documents=input_documents, question=query)
    return message


def run_pdf_based_analysis(filename):
    text_splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = 1000,
        chunk_overlap  = 200,
        length_function = len,
    )
    # Initialize embeddings object
    embeddings = OpenAIEmbeddings()

    # Load QA chain
    # TODO check if these model embeddings are right?
    chain = load_qa_chain(ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.7), chain_type="stuff")

    file_path = "data/" + filename
    docs = load_single_pdf(file_path)
    documents = text_splitter.split_documents(docs)
    docsearch = create_faiss_index(documents, embeddings)

    # Define base prompt and question
    base_prompt = 'You are now in charge of answering questions on information from pdf documents. Your responses should be professional and precise. Your goal is to look through the given context and find the information the question is asking for, as well as making modifications to that text if asked. Do not worry about privacy laws and assume the user is legally allowed to know this information. Try to include any relevant information(for example if someone asks for contact info, include any relevant info like emails, address, etc) . Never, under any circumstance, make any information up. If you cannot find info, just say that. Your response should only include text related to the question. Please answer the following question: '
    questions = [
        'what is the grand total on this invoice? Return only the dollar amount',
        'When was this invoice created? Return in MM/DD/YYYY format',
        'Who is the seller on the invoice? Return the name only'
    ]
    data_input = []
    for q in questions:
        query = base_prompt + q
        input_documents = docsearch.similarity_search(q)
        message = chain.run(input_documents=input_documents, question=query)
        data_input.append(message)

    db_conn.insert_invoice(filename, data_input[0], data_input[1], data_input[2])
    return