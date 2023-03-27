from typing import List, Dict, Any
from langchain.docstore.document import Document
from langchain.chains.question_answering import load_qa_chain
from approaches.prompts import REFINE_QUESTION_PROMPT, REFINE_PROMPT, STUFF_PROMPT
from langchain.llms import AzureOpenAI

# @st.cache_data
def get_answer(docs: List[Document], 
               query: str, 
               language: str, 
               chain_type: str,
               deployment_name: str,
               openai_key: str,
               temperature: float, 
               max_tokens: int
              ) -> Dict[str, Any]:
    
    """Gets an answer to a question from a list of Documents."""

    # Get the answer
    
    llm = AzureOpenAI(deployment_name=deployment_name, model_name=deployment_name, 
                      temperature=temperature, max_tokens=max_tokens, openai_api_key=openai_key)
    
    if chain_type=="refine":
        chain = load_qa_chain(llm, chain_type=chain_type, question_prompt=REFINE_QUESTION_PROMPT, refine_prompt=REFINE_PROMPT)    
    if chain_type=="stuff":
        chain = load_qa_chain(llm, chain_type=chain_type, prompt=STUFF_PROMPT)
    
    answer = chain( {"input_documents": docs, "question": query, "language": language}, return_only_outputs=True)
    
    return answer