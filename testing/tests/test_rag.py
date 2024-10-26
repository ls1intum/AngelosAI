import os
import pytest
import requests
import numpy as np
import pandas as pd
import logging
from dotenv import load_dotenv
from datetime import datetime
from typing import List

from testing.models.azure_testing_model import AzureTestingModel
from testing.tests.test_data import qa_objects
from testing.evaluation.llm_evaluation import LlmEvaluation
from testing.evaluation.embedding_evaluation import EmbeddingEvaluation
from testing.evaluation.deep_eval_evaluation import DeepEvalEvaluation
from testing.evaluation.relevant_links_evaluation import RelevantLinkEvaluation
from testing.test_data_models.qa_data import QAData

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "../testing.env"))

# Fetch ANGELOS from the .env file
TEST_URL = os.getenv("TEST_URL")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION")

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize all evaluation classes
testing_model = AzureTestingModel(api_key=AZURE_OPENAI_API_KEY, api_version=AZURE_OPENAI_VERSION, azure_endpoint=AZURE_OPENAI_ENDPOINT, model=AZURE_OPENAI_DEPLOYMENT, embed_model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT)
llm_eval = LlmEvaluation(model=testing_model)
embedding_eval = EmbeddingEvaluation(model=testing_model)
deep_eval = DeepEvalEvaluation(model_name=AZURE_OPENAI_DEPLOYMENT)
link_eval = RelevantLinkEvaluation()

# Create a results directory if it doesn't exist
results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(results_dir, exist_ok=True)

# Initialize CSV columns
CSV_COLUMNS = [
    'Label', 'Question', 'Answer', 'Ground Truth', 'Used Tokens', 'Cosine Similarity', 'Euclidean Distance',
    'Custom LLM Classification', 'Custom LLM Fact Evaluation',
    'Contextual Precision (General)', 'Contextual Precision Reason (General)',
    'Contextual Precision (Specific)', 'Contextual Precision Reason (Specific)',
    'Contextual Recall', 'Contextual Recall Reason',
    'Contextual Relevancy', 'Contextual Relevancy Reason',
    'Answer Relevancy', 'Answer Relevancy Reason',
    'Faithfulness', 'Faithfulness Reason',
    'Hallucination', 'Hallucination Reason',
    'Link Accuracy'
]

# Prepare the DataFrame to collect results across tests
results_df = pd.DataFrame(columns=CSV_COLUMNS)

# Generate a unique CSV filename based on the timestamp
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = os.path.join(results_dir, f"rag_evaluation_results_{current_time}.csv")
summary_csv_filename = os.path.join(results_dir, f"rag_evaluation_summary_{current_time}.csv")


@pytest.fixture(scope="session", autouse=True)
def gather_results():
    # Initialize a global DataFrame to collect results
    global results_df
    yield  # This will allow all tests to run first
    # After all tests are run, calculate and save the summary
    if not results_df.empty:
        create_summary_csv(results_df, summary_csv_filename)


def create_summary_csv(results_df: pd.DataFrame, summary_csv_filename: str):
    # Filter numeric columns that can be averaged
    numeric_columns = [
        'Used Tokens', 'Cosine Similarity', 'Euclidean Distance',
        'Contextual Precision (General)', 'Contextual Precision (Specific)',
        'Contextual Recall', 'Contextual Relevancy',
        'Answer Relevancy', 'Faithfulness', 'Hallucination', 'Link Accuracy'
    ]
    # Calculate averages for each numeric column
    summary_data = {column: results_df[column].mean() for column in numeric_columns if column in results_df}
    # Save the summary to CSV
    summary_df = pd.DataFrame([summary_data])
    summary_df.to_csv(summary_csv_filename, index=False)
    logging.info(f"Summary CSV saved to {summary_csv_filename}")
    

@pytest.mark.parametrize("qaData", qa_objects)
def test_rag_api(qaData: QAData):
    global results_df

    response = requests.post(
        TEST_URL,
        json={"message": qaData.question, "study_program": qaData.classification, "language": qaData.language}
    )

    # If there's an issue with the server response, fail gracefully
    if response.status_code != 200:
        pytest.fail(f"RAG API returned error: {response.status_code}")
    
    # Parse the response
    rag_response = response.json()
    answer = rag_response['answer']
    general_context = rag_response['general_context']
    specific_context = rag_response['specific_context']
    used_tokens = rag_response['used_tokens']

    # Step 2: Run LLM Fact Classification
    llm_classification = llm_eval.ask_llm_to_classify(qaData, answer)
    logging.info(f"LLM Classification: {llm_classification}")
    
    fact_evaluation = llm_eval.evaluate_facts(qaData, answer)
    logging.info(f"LLM Fact Evaluation: {fact_evaluation}")

    # Step 3: Run Embedding Evaluation for similarity metrics
    embedding_results = embedding_eval.evaluate_similarity(qaData.answer, answer)
    logging.info(f"Cosine Similarity: {embedding_results['cosine_similarity']}")
    logging.info(f"Euclidean Distance: {embedding_results['euclidean_distance']}")

    # Step 4: Run DeepEval Evaluation for various metrics
    contextual_precision, contextual_precision_reason = deep_eval.evaluate_contextual_precision(qaData, answer, general_context)
    logging.info(f"Contextual Precision (General): {contextual_precision}")
    logging.info(f"Contextual Precision Reason (General): {contextual_precision_reason}")
    
    contextual_precision_specific, contextual_precision_specific_reason = deep_eval.evaluate_contextual_precision(qaData, answer, specific_context)
    logging.info(f"Contextual Precision (Specific): {contextual_precision_specific}")
    logging.info(f"Contextual Precision Reason (Specific): {contextual_precision_specific_reason}")

    contextual_recall, contextual_recall_reason = deep_eval.evaluate_contextual_recall(qaData, answer, general_context + specific_context)
    logging.info(f"Contextual Recall: {contextual_recall}")
    logging.info(f"Contextual Recall Reason: {contextual_recall_reason}")

    contextual_relevancy, contextual_relevancy_reason = deep_eval.evaluate_contextual_relevancy(qaData, answer, general_context + specific_context)
    logging.info(f"Contextual Relevancy: {contextual_relevancy}")
    logging.info(f"Contextual Relevancy Reason: {contextual_relevancy_reason}")

    answer_relevancy, answer_relevancy_reason = deep_eval.answer_relevancy(qaData.question, answer)
    logging.info(f"Answer Relevancy: {answer_relevancy}")
    logging.info(f"Answer Relevancy Reason: {answer_relevancy_reason}")

    faithfulness, faithfulness_reason = deep_eval.faithfulness(qaData.question, answer, general_context + specific_context)
    logging.info(f"Faithfulness: {faithfulness}")
    logging.info(f"Faithfulness Reason: {faithfulness_reason}")

    hallucination, hallucination_reason = deep_eval.hallucination(qaData.question, answer, general_context + specific_context)
    logging.info(f"Hallucination: {hallucination}")
    logging.info(f"Hallucination Reason: {hallucination_reason}")

    # Step 5: Relevant Link Accuracy
    link_accuracy = link_eval.evaluate_relevant_links(qaData.expected_sources, answer)
    logging.info(f"Link Accuracy: {link_accuracy}")

    # Step 6: Store results in DataFrame
    result_row = {
        'Label': qaData.label,
        'Question': qaData.question,
        'Answer': answer,
        'Ground Truth': qaData.answer,
        'Used Tokens': used_tokens,
        'Cosine Similarity': embedding_results['cosine_similarity'],
        'Euclidean Distance': embedding_results['euclidean_distance'],
        'Custom LLM Classification': llm_classification,
        'Custom LLM Fact Evaluation': fact_evaluation,
        'Contextual Precision (General)': contextual_precision,
        'Contextual Precision Reason (General)': contextual_precision_reason,
        'Contextual Precision (Specific)': contextual_precision_specific,
        'Contextual Precision Reason (Specific)': contextual_precision_specific_reason,
        'Contextual Recall': contextual_recall,
        'Contextual Recall Reason': contextual_recall_reason,
        'Contextual Relevancy': contextual_relevancy,
        'Contextual Relevancy Reason': contextual_relevancy_reason,
        'Answer Relevancy': answer_relevancy,
        'Answer Relevancy Reason': answer_relevancy_reason,
        'Faithfulness': faithfulness,
        'Faithfulness Reason': faithfulness_reason,
        'Hallucination': hallucination,
        'Hallucination Reason': hallucination_reason,
        'Link Accuracy': link_accuracy
    }

    # Append to DataFrame
    results_df = pd.concat([results_df, pd.DataFrame([result_row])], ignore_index=True)

    # Save the CSV after every test case
    results_df.to_csv(csv_filename, index=False)