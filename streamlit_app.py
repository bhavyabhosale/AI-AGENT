import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup


load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def scrape_website(url):
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to retrieve the website")
        return ""
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text(separator="\n")
    return text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details. 
    If the answer is not in the provided context, just say, 'answer is not available in the context,' 
    don't provide the wrong answer.

    Context:\n {context}?\n
    Question:\n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain


def handle_user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    
    st.session_state.chat_history.append({"question": user_question, "answer": response["output_text"]})

def main():
    st.set_page_config("AI-AGENT")
    st.header("AI-AGENT")

    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_question = st.text_input("Ask a Question from the PDF Files or Website")
    if st.button("Submit Question"):
        if user_question:
            handle_user_input(user_question)
            st.experimental_rerun()

    
    for chat in st.session_state.chat_history:
        st.write(f"*You:* {chat['question']}")
        st.write(f"*Agent:* {chat['answer']}")
        st.write("---")  

    
    
   

    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
        website_url = st.text_input("Website URL")

        if st.button("Submit & Process PDFs"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done")

        if st.button("Process Website"):
            if website_url:
                with st.spinner("Processing Website..."):
                    website_text = scrape_website(website_url)
                    if website_text:
                        text_chunks = get_text_chunks(website_text)
                        get_vector_store(text_chunks)
                        st.success("Website processing done")
            else:
                st.error("Please enter a valid website URL")
                
    st.sidebar.markdown("""
    <a href="https://t.me/aibox123bot" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Bot" style="width:30px;height:30px;">
        Chat with our Telegram Bot
    </a>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
