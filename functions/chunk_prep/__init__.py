import logging
import azure.functions as func
import os
import sys
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions, BlobServiceClient
import urllib.request
import glob
import io
import argparse
import json
from enum import Enum
import tiktoken
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
#import openai
import nltk
from nltk.corpus import words
import fitz


XY_ROUNDING_FACTOR = 1
CHUNK_TARGET_SIZE = 500
REAL_WORDS_TARGET = 0.25
TARGET_PAGES = "ALL"          # ALL or Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like pages="1-3, 5-6". Separate each page number or range with a comma.
SECTIONS_PER_CHUNK = 3

def main(myblob: func.InputStream):





    # def extract_outlines(pdf_path):
    #     doc = fitz.open(pdf_path)
    #     outlines = doc.get_toc()
    #     return outlines


    # def separate_sections(pdf_path, outlines):
    #     doc = fitz.open(pdf_path)
    #     structured_sections = {}

    #     for idx, outline in enumerate(outlines[:-1]):
    #         title, level, page = outline
    #         next_title, _, next_page = outlines[idx + 1]
    #         text = ""

    #         for pg in range(page - 1, next_page - 1):
    #             page_text = doc.load_page(pg).get_text("text")
    #             text += page_text

    #         structured_sections[title] = text

    #     return structured_sections

    # pdf_path = os.path.join(os.getcwd(), 'chunk_prep/NationalDefence-DefenceStrategicReview.pdf')

    # outlines = extract_outlines(pdf_path)
    # structured_sections = separate_sections(pdf_path, outlines)

    # for title, text in structured_sections.items():
    #     print(title)
    #     print(text)











    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    from azure.core.exceptions import HttpResponseError
    try:
        analyze_layout(myblob)
    except HttpResponseError as error:
        print("For more information about troubleshooting errors, see the following guide: "
              "https://aka.ms/azsdk/python/formrecognizer/troubleshooting")
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise

    logging.info("Done")


def is_pdf(file_name):
    # Get the file extension using os.path.splitext
    file_ext = os.path.splitext(file_name)[1]
    # Return True if the extension is .pdf, False otherwise
    return file_ext == ".pdf"


def sort_key(element):
    return (element["page"])
    # to do, more complex sorting logic to cope with indented bulleted lists
    return (element["page"], element["role_priority"], element["bounding_region"][0]["x"], element["bounding_region"][0]["y"])


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    # Returns the number of tokens in a text string
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


class paragraph_roles(Enum):
    pageHeader      = 1
    title           = 2
    sectionHeading  = 3
    other           = 3
    footnote        = 5
    pageFooter      = 6
    pageNumber      = 7


def role_prioroty(role):
    priority = 0
    match role:
        case "title":
            priority = paragraph_roles.title.value
        case "sectionHeading":
            priority = paragraph_roles.sectionHeading.value
        case "footnote":
            priority = paragraph_roles.footnote.value
        case "pageHeader" :
            priority = paragraph_roles.pageHeader.value            
        case "pageFooter" :
            priority = paragraph_roles.pageFooter.value
        case "pageNumber" :
            priority = paragraph_roles.pageNumber.value     
        case other:     # content
            priority = paragraph_roles.other.value         
    return (priority)


# Load a pre-trained tokenizer
tokenizer = nltk.tokenize.word_tokenize

# Load a set of known English words
word_set = set(nltk.corpus.words.words())


# Define a function to check whether a token is a real English word
def is_real_word(token):
    return token.lower() in word_set

# Define a function to check whether a string contains real English words
def contains_real_words(string):
    tokens = tokenizer(string)
    real_word_count = sum(1 for token in tokens if is_real_word(token))
    return (real_word_count / len(tokens) > REAL_WORDS_TARGET) and (len(tokens) >= 1)  # Require at least 50% of tokens to be real words and at least one word


def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in polygon])



# *********************************************
# Example code to call a summary from openai
# *********************************************
# def split_text(text):
#     max_chunk_size = 2048
#     chunks = []
#     current_chunk = ""
#     for sentence in text.split("."):
#         if len(current_chunk) + len(sentence) < max_chunk_size:
#             current_chunk += sentence + "."
#         else:
#             chunks.append(current_chunk.strip())
#             current_chunk = sentence + "."
#     if current_chunk:
#         chunks.append(current_chunk.strip())
#     return chunks

# def generate_summary(text):
#     openai.api_key = os.environ["AZURE_BLOB_STORAGE_ACCOUNT"]

#     #Note: The openai-python library support for Azure OpenAI is in preview.
#     openai.api_type = "azure"
#     openai.api_base = "https://infoasst-spike-aoai.openai.azure.com/"
#     openai.api_version = "2022-12-01"
#     openai.api_key = os.environ["AZURE_OPENAI_SERVICE_KEY"]

#     input_chunks = split_text(text)
#     output_chunks = []
#     for chunk in input_chunks:

#         response = openai.Completion.create(
#             engine="text-davinci-003",
#             prompt=f"Provide a summary of the text below that captures its main idea: \n {chunk}",
#             temperature=0.3,
#             max_tokens=250,
#             top_p=0.5,
#             frequency_penalty=0,
#             presence_penalty=0,
#             best_of=1,
#             stop=None)

#         summary = response.choices[0].text.strip()
#         output_chunks.append(summary)

#     return " ".join(output_chunks)



def token_count(input_text):
    # calc token count
    encoding = "cl100k_base"    # For gpt-4, gpt-3.5-turbo, text-embedding-ada-002, you need to use cl100k_base
    token_count = num_tokens_from_string(input_text, encoding)
    return token_count    


def analyze_layout(myblob: func.InputStream):

    if is_pdf(myblob.name):

        logging.info("processing pdf " + myblob.name)

        azure_blob_storage_account = os.environ["AZURE_BLOB_STORAGE_ACCOUNT"]
        azure_blob_drop_storage_container = os.environ["AZURE_BLOB_DROP_STORAGE_CONTAINER"]
        azure_blob_content_storage_container = os.environ["AZURE_BLOB_CONTENT_STORAGE_CONTAINER"]
        azure_blob_storage_key = os.environ["AZURE_BLOB_STORAGE_KEY"]
        base_filename = os.path.basename(myblob.name)

        # Get path and file name minus the root container
        separator = "/"
        File_path_and_name_no_container = separator.join(
            myblob.name.split(separator)[1:])

        # Get the folders to use when creating the new files
        folder_set = File_path_and_name_no_container.removesuffix(
            f'/{base_filename}')

        # Gen SAS token
        sas_token = generate_blob_sas(
            account_name=azure_blob_storage_account,
            container_name=azure_blob_drop_storage_container,
            blob_name=File_path_and_name_no_container,
            account_key=azure_blob_storage_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_path = f'https://{azure_blob_storage_account}.blob.core.windows.net/{myblob.name}?{sas_token}'
        source_blob_path = source_blob_path.replace(" ", "%20")

    # [START extract_layout]
    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
 
    if TARGET_PAGES == "ALL":
        poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-layout", document_url=source_blob_path
        )
    else :
        poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-layout", document_url=source_blob_path, pages=TARGET_PAGES
        )        
    result = poller.result()

    # write out raw results
    # blob_service_client = BlobServiceClient(
    #     f'https://{azure_blob_storage_account}.blob.core.windows.net/', azure_blob_storage_key)
    # output_filename = os.path.splitext(os.path.basename(base_filename))[0] + "-telemtry" + ".json"
    # block_blob_client = blob_service_client.get_blob_client(
    #     container=azure_blob_content_storage_container, blob=f'{folder_set}/{output_filename}')
    # block_blob_client.upload_blob(json.dumps(result), overwrite=True)


    for idx, style in enumerate(result.styles):
        print(
            "Document contains {} content".format(
                "handwritten" if style.is_handwritten else "no handwritten"
            )
        )

    for page in result.pages:
        print("----Analyzing layout from page #{}----".format(page.page_number))
        print(
            "Page has width: {} and height: {}, measured with unit: {}".format(
                page.width, page.height, page.unit
            )
        )

        for line_idx, line in enumerate(page.lines):
            words = line.get_words()
            print(
                "...Line # {} has word count {} and text '{}' within bounding polygon '{}'".format(
                    line_idx,
                    len(words),
                    line.content,
                    format_polygon(line.polygon),
                )
            )

            for word in words:
                print(
                    "......Word '{}' has a confidence of {}".format(
                        word.content, word.confidence
                    )
                )

        for selection_mark in page.selection_marks:
            print(
                "...Selection mark is '{}' within bounding polygon '{}' and has a confidence of {}".format(
                    selection_mark.state,
                    format_polygon(selection_mark.polygon),
                    selection_mark.confidence,
                )
            )

    for table_idx, table in enumerate(result.tables):
        print(
            "Table # {} has {} rows and {} columns".format(
                table_idx, table.row_count, table.column_count
            )
        )
        for region in table.bounding_regions:
            print(
                "Table # {} location on page: {} is {}".format(
                    table_idx,
                    region.page_number,
                    format_polygon(region.polygon),
                )
            )
        for cell in table.cells:
            print(
                "...Cell[{}][{}] has content '{}'".format(
                    cell.row_index,
                    cell.column_index,
                    cell.content,
                )
            )
            for region in cell.bounding_regions:
                print(
                    "...content on page {} is within bounding polygon '{}'".format(
                        region.page_number,
                        format_polygon(region.polygon),
                    )
                )

    # build the json structure
    pargraph_elements = []
    title = ""
    section_heading = ""
    for paragraph in result.paragraphs: 
        # only porcess content, titles and sectionHeading 
        if paragraph.role == "title" or paragraph.role == "sectionHeading" or paragraph.role == None:
            polygon_elements = []
            # store the most recent title and subheading as context data
            if paragraph.role == "title":
                title = paragraph.content   
            if paragraph.role == "sectionHeading":
                section_heading = paragraph.content         
            for point in paragraph.bounding_regions[0].polygon:
                polygon_elements.append({
                    "x": round(point.x, XY_ROUNDING_FACTOR),
                    "y": round(point.y, XY_ROUNDING_FACTOR)
                })
            pargraph_elements.append({
                "page": paragraph.bounding_regions[0].page_number,
                "role_priority": role_prioroty(paragraph.role),
                "role": paragraph.role,
                "bounding_region": polygon_elements,   
                "content": paragraph.content,  
                "title": title,
                "section_heading": section_heading
            })           

    # sort
    pargraph_elements.sort(key=sort_key)

    # *********************************************************************
    # # Build summaries by section
    # blob_service_client = BlobServiceClient(
    # f'https://{azure_blob_storage_account}.blob.core.windows.net/', azure_blob_storage_key)
    # section_number = 0
    # section_text = ""
    # section_heading = ""
    # for paragraph_element in pargraph_elements:  
    #     # only process for section headings, titles or content
    #     if paragraph_element["role"] == "sectionHeading" or paragraph_element["role"]  == "title" or paragraph_element["role"]  == None:
    #         # 
    #         if paragraph_element["role"]  == None:  # paragraph
    #             section_text = section_text + " " +paragraph_element["content"] 
    #         else: # section or title
    #             # write out the section or title page summary, but not for the first title/subheading it hits
    #             if section_number > 0:
    #                 section_element['section_text'] = section_text
    #                 section_element['section_summary'] = generate_summary(section_text)

    #             # reset values for next section
    #             section_element = paragraph_element
    #             section_heading = paragraph_element["content"]
    #             section_text = ""
    #             section_number += 1

    # # Process the last section
    # section_heading = paragraph_element["content"]
    # *********************************************************************
            

    # # extract the content by paragraph with title, sectionHeading & pageHeader and write as a chunk
    # blob_service_client = BlobServiceClient(
    # f'https://{azure_blob_storage_account}.blob.core.windows.net/', azure_blob_storage_key)
    # i = 0
    # chunk_text = ""
    # chunk_size = 0
    # for paragraph_element in pargraph_elements:     
    #     # only write content as chunks - not titles , footers etc.
        
    #     if paragraph_element["role"] == None:
    #         paragraph_size = token_count(paragraph_element["content"])
    #         if chunk_size + paragraph_size <= CHUNK_TARGET_SIZE:
    #             chunk_size = chunk_size + paragraph_size
    #             chunk_text = chunk_text + "\n" + paragraph_element["content"]
    #         else:
    #             chunk_output = paragraph_element["title"] + "\n" + \
    #                 paragraph_element["section_heading"] + "\n\n" + \
    #                 chunk_text        
    #             output_filename = os.path.splitext(os.path.basename(base_filename))[0] + f"-{i}" + ".txt"
    #             block_blob_client = blob_service_client.get_blob_client(
    #                 container=azure_blob_content_storage_container, blob=f'{folder_set}/{output_filename}')
    #             block_blob_client.upload_blob(chunk_output.encode('utf-8'), overwrite=True)
    #             i += 1
    #             chunk_text = ""
    #             chunk_size = 0



    # extract the content by paragraph with title, sectionHeading & pageHeader and write as a chunk
    blob_service_client = BlobServiceClient(
    f'https://{azure_blob_storage_account}.blob.core.windows.net/', azure_blob_storage_key)
    file_number = 0
    chunk_text = ""
    chunk_size = 0
    paragraph_size = 0
    section_name = ""
    title_name = ""
    target_size_reached = False
    chunk_output = []
    
    # group paragraphs into sections
    i = 1
    for paragraph_element in pargraph_elements:   
        
        if paragraph_element["role"] == None and contains_real_words(paragraph_element["content"]) == True:
            title_name = paragraph_element["title"]
            section_name = paragraph_element["section_heading"]
            # build chunck from paragraphs until target size is reached  
            paragraph_size = token_count(paragraph_element["content"])
            if chunk_size + paragraph_size <= CHUNK_TARGET_SIZE:
                chunk_size = chunk_size + paragraph_size
                chunk_text = chunk_text + "\n" + paragraph_element["content"]
            else:
                # if target chunk size is hit then write out file
                target_size_reached = True 

        # output section, or part of section if max chuck size is reached, OR if this is a new section, OR if this is the last paragraph in the document, write to the chunk array
        if (paragraph_element["role"] != None or target_size_reached == True or (i == len(pargraph_elements))) and chunk_text != ""  :
            # if its a new section then build the text block
            chunk_text = title_name + " - " + section_name + "\n" + \
                chunk_text + "\n\n\n"   
            chunk_output.append(chunk_text)

            # if we wrote the file because we hit the token target, then start with the last paragraph processed
            if target_size_reached == True:
                chunk_text = paragraph_element["content"]
                chunk_size = paragraph_size   
                target_size_reached = False 
            else:
                chunk_text = ""
                chunk_size = 0   

        i += 1



    # iterate over the chunked output and output in the format of sections to text files ... i-1, i, and i+1
    i = 0
    file_text = ""
    write_file = False
    while i <= len(chunk_output)-1:

        if i == len(chunk_output)-1:
            file_text = chunk_output[i-1] + "\n" \
                + chunk_output[i]
            write_file = True

        elif i >= 1:
            file_text = chunk_output[i-1] + "\n" \
                + chunk_output[i] + "\n" \
                + chunk_output[i+1]    
            write_file = True
        
        if write_file == True:
            output_filename = os.path.splitext(os.path.basename(base_filename))[0] + f"-{file_number}" + ".txt"
            block_blob_client = blob_service_client.get_blob_client(
                container=azure_blob_content_storage_container, blob=f'{folder_set}/{output_filename}')
            block_blob_client.upload_blob(file_text.encode('utf-8'), overwrite=True)
            file_number += 1   

        i += 1

    print("done")


        








