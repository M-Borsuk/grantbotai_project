from typing import Dict, List

import numpy as np
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from app.db import mongo
from app.logger import logger


class OpenRouterLLM:

    MAX_TOKENS = 350

    def __init__(self, key: str, base_url: str, model: str):
        self.client = openai.OpenAI(api_key=key, base_url=base_url)
        self.model = model

    def __fetch_candidates__(self, company_id: str) -> List[Dict]:
        """
        Fetch all documents for a given company_id from the database.

        Args:
            company_id (str): The ID of the company.
        Returns:
            List[Dict]: A list of document records.
        """
        docs = list(mongo.documents.find({"company_id": company_id}))
        logger.info(f"Fetched {len(docs)} documents for company_id={company_id}")
        return docs

    def __retrieve_top_k__(self, input_text: str, candidates: List[Dict], k: int = 3) -> List[Dict]:
        """
        Return top-k docs most similar to input_text.

        Args:
            input_text (str): The input text to compare against.
            candidates (List[Dict]): List of candidate documents with 'text' field.
            k (int): Number of top documents to retrieve.
        Returns:
            List[Dict]: Top-k most similar document records.
        """
        texts = [c["text"] for c in candidates]
        if not texts:
            return []
        corpus = [input_text] + texts
        vect = TfidfVectorizer().fit(corpus)
        vectors = vect.transform(corpus)
        sims = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
        top_idx = np.argsort(sims)[::-1][:k]
        return [candidates[i] for i in top_idx]

    def __format_contexts_for_llm__(self, contexts: List[Dict]) -> str:
        """
        Format context documents for LLM input, marking section types.

        Args:
            contexts (List[Dict]): List of context documents with 'section_type' and 'text'.
        Returns:
            str: Formatted context string for LLM.
        """
        blocks = []
        for c in contexts:
            section = c.get("section_type", "unknown")
            text = c.get("text", "")
            blocks.append(f"[{section.upper()}]\n{text}")
        return "\n\n".join(blocks)

    @staticmethod
    def __system_prompt_for_section__(section_type: str) -> str:
        """
        Create a system prompt tailored for generating a specific section type.

        Args:
            section_type (str): The type of section to generate.
        Returns:
            str: The system prompt string.
        """
        return (
            f"You are an expert at writing grant application document sections. "
            f"The user will ask you to generate the [{section_type.upper()}] section. "
            f"Use the provided context snippets (labeled with their original section types) to generate a coherent, comprehensive [{section_type.upper()}] section. "
            "Be concise and make sure to use factual information from the context whenever possible."
        )

    def generate_section(
        self, input_text: str, company_id: str, section_type: str, k: int = 3
    ) -> dict:
        """
        Generate a specific section of a grant application using LLM and context retrieval.

        Args:
            input_text (str): The user's input text.
            company_id (str): The ID of the company.
            section_type (str): The type of section to generate.
            k (int): Number of context documents to retrieve.
        Returns:
            dict: A dictionary with 'generated_text' and 'sources'.
        """
        candidates = self.__fetch_candidates__(company_id)
        top_contexts = self.__retrieve_top_k__(input_text, candidates, k=k)
        context_block = self.__format_contexts_for_llm__(top_contexts)
        system_prompt = self.__system_prompt_for_section__(section_type)
        user_prompt = f"User input: {input_text}\n\nContext snippets:\n{context_block}"
        logger.info(
            f"Generating section with system prompt: {system_prompt} and user prompt: {user_prompt}"
        )
        generated_text = self.query_openrouter(
            user_prompt, max_tokens=self.MAX_TOKENS, system_prompt=system_prompt
        )
        sources = [c["id"] for c in top_contexts]
        return {
            "generated_text": generated_text,
            "sources": sources,
        }

    def query_openrouter(self, user_prompt: str, max_tokens: int, system_prompt: str) -> str:
        """
        Generate text using the OpenRouter API with a system and user prompt.

        Args:
            user_prompt (str): The user's input prompt.
            max_tokens (int): Maximum number of tokens to generate.
            system_prompt (str): The system-level prompt to guide generation.

        Returns:
            str: The generated text from the model.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

openrouter_llm = OpenRouterLLM(
    key=settings.openrouter_key,
    base_url=settings.openrouter_api_base,
    model=settings.openrouter_model,
)
