# flake8: noqa
from langchain.prompts import PromptTemplate

## Use a shorter template to reduce the number of tokens in the prompt

stuff_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
{context}
Question: {question}
Answer in {language}:"""

STUFF_PROMPT = PromptTemplate(
    input_variables=["context", "question", "language"],
    template=stuff_template
)

refine_template = (
    "The original question is as follows: {question}\n"
    "We have provided an existing answer: {existing_answer}\n"
    "We have the opportunity to refine the existing answer"
    "(only if needed) with some more context below.\n"
    "Sources:\n"
    "{context_str}\n"
    "------------\n"
    "Given the new context, refine the existing answer to better"
    "answer the question (in {language}) and, if available in the context, mention some examples."
    "If the context isn't useful, return the original answer."
    "The source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brakets to reference the source, e.g. [info1.txt]. Don't combine sources, list each source separately, e.g. [info1.txt][info2.pdf]."
)

REFINE_PROMPT =  PromptTemplate(
    input_variables=["question", "existing_answer", "context_str", "language"],
    template=refine_template,
)

follow_up_questions_prompt_content = (
    "Generate three very brief follow-up questions that the user would likely ask next about their military intelligence data."
    "Use double angle brackets to reference the questions, e.g. <<Are there exclusions for prescriptions?>>."
    "Try not to repeat questions that have already been asked."
    "Only generate questions and do not generate any text before or after the questions, such as 'Next Questions'"""
)

refine_question_template = (
    "Context information is below. \n"
    "Sources:\n"
    "{context_str}"
    "\n---------------------\n"
    "Given the context information and no prior knowledge, "
    "answer the question (in {language}): {question}\n"
    "The source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brakets to reference the source, e.g. [info1.txt]. Don't combine sources, list each source separately, e.g. [info1.txt][info2.pdf]."
)
REFINE_QUESTION_PROMPT = PromptTemplate(
    input_variables=["context_str", "question", "language"], 
    template=refine_question_template,
)