# Python program to convert
# text file to pdf file
from bs4 import BeautifulSoup
import psycopg2
import os
import openai
import wandb
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import ElasticVectorSearch, Pinecone, Weaviate, FAISS
from PyPDF2 import PdfReader
from fpdf import FPDF
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from django.conf import settings

load_dotenv()

def parse_html():
    global tag_interests, interests
    # Opening the html file
    file_path = os.path.join(settings.BASE_DIR, 'upload/ads_interests.html')
    HTMLFile = open(file_path, "r")

    # Reading the file
    index = HTMLFile.read()

    # Creating a BeautifulSoup object and specifying the parser
    soup = BeautifulSoup(index, 'html.parser')

    tag_interests = soup.find_all('td')
    interests = []

    # Using the prettify method to modify the code
    for tag in tag_interests:
        interest = tag.find_next('div').text
        if len(interest) == 0:
            continue
        interests.append(interest)
        # div_tag = user.find_next('div')
    # print(interests)

def create_ads_pdf():
    global tag_interests, interests
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf
    intro_string = 'This file will tell information about the ads interest for Jainam (instagram username: @jainamxgala).\n'
    # pdf.add_font('ArialUnicode', '/Users/jgala/Documents/Arial_Unicode.ttf', uni=True)
    pdf.set_font("Arial", '', size = 12)
    pdf.cell(200, 10, txt = intro_string, ln = 1, align = 'L')

    for interest in interests:
        pdf.cell(200, 10, txt = "I am interested in " + interest + ".\n", ln = 1, align = 'L')

    # save the pdf with name .pdf
    saved_file_path = os.path.join(settings.BASE_DIR, 'upload/created_ads_interested.pdf')
    pdf.output(saved_file_path)

def prepare_search_engine():
    saved_file_path = os.path.join(settings.BASE_DIR, 'upload/created_ads_interested.pdf')
    reader = PdfReader(saved_file_path)
    raw_text = ''
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_text = raw_text + text

    text_splitter = CharacterTextSplitter(        
    separator = "\n",
    chunk_size = 1000,
    chunk_overlap  = 200,
    length_function = len,
    )
    texts = text_splitter.split_text(raw_text)

    # Download embeddings from OpenAI
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)
    return docsearch
    
def run_search_engine(docsearch, query):
    docs = docsearch.similarity_search(query)
    chain = load_qa_chain(OpenAI(max_tokens=1000), chain_type="stuff")
    result = chain.run(input_documents=docs, question=query)
    print(result)
    return result

global tag_interests, interests
# parse_html()
# create_ads_pdf()
# docsearch = prepare_search_engine()
# run_search_engine(docsearch, "Categorize Jainam's interest in 5 different categories and give a list.")
# run_search_engine(docsearch, "Which celebrities are in Jainam's interests?")
# run_search_engine(docsearch, "What kind of music does Jainam listen to?")
# run_search_engine(docsearch, "Which is Jainam's favorite sport?")