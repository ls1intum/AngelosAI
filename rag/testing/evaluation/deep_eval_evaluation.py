import asyncio
import httpx
import random

from dotenv import load_dotenv
from deepeval.metrics import ContextualPrecisionMetric, ContextualRecallMetric, ContextualRelevancyMetric, AnswerRelevancyMetric, HallucinationMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from deepeval.metrics.ragas import RagasMetric
from testing.test_data_models.qa_data import QAData

class DeepEvalEvaluation:
    def __init__(self, model_name: str, threshold: float = 0.7, max_retries: int = 3, timeout: int = 60):
        """
        Initialize DeepEvalEvaluation class.
        """
        self.model = model_name
        self.threshold = threshold
        self.max_retries = max_retries
        self.timeout = timeout
        
    async def _retry_async_call(self, func, *args, **kwargs):
        """Retries an async function with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout)
            except (asyncio.TimeoutError, httpx.HTTPStatusError, httpx.TimeoutException) as e:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}. Retrying in {wait_time:.2f}s.")
                await asyncio.sleep(wait_time)
        raise Exception(f"Failed after {self.max_retries} retries.")

    async def evaluate_contextual_precision(self, qa_data: QAData, actual_output: str, retrieval_context: list):
        """
        Evaluates Contextual Precision for the RAG retriever.

        The contextual precision metric measures your RAG pipeline's retriever 
        by evaluating whether nodes in your retrieval_context that are relevant 
        to the given input are ranked higher than irrelevant ones. 

        Args:
            qa_data (QAData): Contains the input question and expected output.
            actual_output (str): The generated answer from the LLM.
            retrieval_context (list): The retrieved context for the given input.

        Returns:
            score (float): The contextual precision score.
            reason (str): Explanation of the score from the LLM (self-explaining metric).
        """
        loop = asyncio.get_event_loop()
        
        def measure_sync():
            metric = ContextualPrecisionMetric(
                threshold=self.threshold,
                model=self.model,
                include_reason=True
            )

            test_case = LLMTestCase(
                input=qa_data.question,
                actual_output=actual_output,
                expected_output=qa_data.answer,
                retrieval_context=retrieval_context
            )
            metric.measure(test_case)
            return metric.score, metric.reason

        return await self._retry_async_call(loop.run_in_executor, None, measure_sync)

    async def evaluate_contextual_recall(self, qa_data: QAData, actual_output: str, retrieval_context: list):
        """
        Evaluates Contextual Recall for the RAG retriever.

        The contextual recall metric measures the quality of your RAG pipeline's retriever 
        by evaluating the extent to which the retrieval_context aligns with the expected_output. 

        Args:
            qa_data (QAData): Contains the input question and expected output.
            actual_output (str): The generated answer from the LLM.
            retrieval_context (list): The retrieved context for the given input.

        Returns:
            score (float): The contextual recall score.
            reason (str): Explanation of the score from the LLM (self-explaining metric).
        """
        loop = asyncio.get_event_loop()
        
        def measure_sync():
            metric = ContextualRecallMetric(
                threshold=self.threshold,
                model=self.model,
                include_reason=True
            )

            test_case = LLMTestCase(
                input=qa_data.question,
                actual_output=actual_output,
                expected_output=qa_data.answer,
                retrieval_context=retrieval_context
            )
            
            metric.measure(test_case)
            return metric.score, metric.reason

        return await self._retry_async_call(loop.run_in_executor, None, measure_sync)

    async def evaluate_contextual_relevancy(self, qa_data: QAData, actual_output: str, retrieval_context: list):
        """
        Evaluates Contextual Relevancy for the RAG retriever.

        The contextual relevancy metric measures the quality of your RAG pipeline's retriever 
        by evaluating the overall relevance of the information presented in your retrieval_context 
        for a given input. 

        Args:
            qa_data (QAData): Contains the input question and expected output.
            actual_output (str): The generated answer from the LLM.
            retrieval_context (list): The retrieved context for the given input.

        Returns:
            score (float): The contextual relevancy score.
            reason (str): Explanation of the score from the LLM (self-explaining metric).
        """
        loop = asyncio.get_event_loop()
        
        def measure_sync():
            metric = ContextualRelevancyMetric(
                threshold=self.threshold,
                model=self.model,
                include_reason=True
            )

            test_case = LLMTestCase(
                input=qa_data.question,
                actual_output=actual_output,
                retrieval_context=retrieval_context
            )
            metric.measure(test_case)
            return metric.score, metric.reason

        return await self._retry_async_call(loop.run_in_executor, None, measure_sync)
    
    async def answer_relevancy(self, input_text, actual_output):
        """
        Measures the relevancy of the generated output to the given input.
        
        :param input_text: The question or input given to the LLM.
        :param actual_output: The answer generated by the LLM.
        :return: Score of how relevant the output is, and the reason provided by the model.
        """
        loop = asyncio.get_event_loop()
        
        def measure_sync():
            metric = AnswerRelevancyMetric(
                threshold=0.7,
                model=self.model,
                include_reason=True
            )
            test_case = LLMTestCase(
                input=input_text,
                actual_output=actual_output
            )
            metric.measure(test_case)
            return metric.score, metric.reason

        return await self._retry_async_call(loop.run_in_executor, None, measure_sync)

    async def faithfulness(self, input_text, actual_output, retrieval_context):
        """
        Measures how factually aligned the generated output is with the provided retrieval context.
        
        :param input_text: The question or input given to the LLM.
        :param actual_output: The answer generated by the LLM.
        :param retrieval_context: The retrieved context from the RAG model.
        :return: Score of how faithful the output is to the context, and the reason provided by the model.
        """
        loop = asyncio.get_event_loop()
        
        def measure_sync():
            metric = FaithfulnessMetric(
                threshold=0.7,
                model=self.model,
                include_reason=True
            )
            test_case = LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                retrieval_context=retrieval_context
            )
            metric.measure(test_case)
            return metric.score, metric.reason
        
        return await self._retry_async_call(loop.run_in_executor, None, measure_sync)

    async def hallucination(self, input_text, actual_output, context):
        """
        Determines whether the LLM output contains hallucinations (factually incorrect information) 
        by comparing the output with the provided context.
        
        :param input_text: The question or input given to the LLM.
        :param actual_output: The answer generated by the LLM.
        :param context: The context passed to the LLM.
        :return: Score indicating hallucination and the reason provided by the model.
        """
        loop = asyncio.get_event_loop()
        
        def measure_sync():
            metric = HallucinationMetric(threshold=0.5)
            test_case = LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                context=context
            )

            # Measure the metric score and reason
            metric.measure(test_case)
            return metric.score, metric.reason
        
        return await self._retry_async_call(loop.run_in_executor, None, measure_sync)
    
    def evaluate_ragas(self, qa_data: QAData, actual_output: str, retrieval_context: list):
        """
        Evaluates RAGAS metric for the RAG retriever and generator.

        The RAGAS metric measures the overall quality of the RAG pipeline by
        evaluating how well the generated answer aligns with both the retrieval context 
        and the expected output.

        Args:
            qa_data (QAData): Contains the input question and expected output.
            actual_output (str): The generated answer from the LLM.
            retrieval_context (list): The retrieved context for the given input.

        Returns:
            score (float): The RAGAS score.
            reason (str): Explanation of the score from the LLM (self-explaining metric).
        """
        metric = RagasMetric(
            threshold=self.threshold,
            model=self.model
        )

        test_case = LLMTestCase(
            input=qa_data.question,
            actual_output=actual_output,
            expected_output=qa_data.answer,
            retrieval_context=retrieval_context
        )

        metric.measure(test_case)
        return metric.score