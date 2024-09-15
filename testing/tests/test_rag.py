import os
import pytest
import requests
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from testing.tests.test_data import qa_objects
from testing.evaluation.llm_evaluation import LlmEvaluation
from testing.evaluation.embedding_evaluation import EmbeddingEvaluation
from testing.evaluation.deep_eval_evaluation import DeepEvalEvaluation
from testing.evaluation.relevant_links_evaluation import RelevantLinkEvaluation
import logging

# Load environment variables
load_dotenv()

# Fetch EUNOMNIA_URL from the .env file
TEST_URL = os.getenv("TEST_URL")

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize all evaluation classes
llm_eval = LlmEvaluation()
embedding_eval = EmbeddingEvaluation()
deep_eval = DeepEvalEvaluation()
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

# Prepare the DataFrame to collect results
results_df = pd.DataFrame(columns=CSV_COLUMNS)

# Generate a unique CSV filename based on the timestamp
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = os.path.join(results_dir, f"rag_evaluation_results_{current_time}.csv")

@pytest.mark.parametrize("qaData", qa_objects)
def test_rag_api(qaData):
    global results_df

    response = requests.post(
        TEST_URL,
        json={"message": qaData.question, "study_program": qaData.classification}
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

    # Display interim results with numpy for quick evaluation
    print(np.array(results_df))

    # Save the CSV after every test case
    results_df.to_csv(csv_filename, index=False)