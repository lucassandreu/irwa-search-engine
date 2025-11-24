# myapp/generation/rag.py
import os
from typing import List, Any, Optional

from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env


class RAGGenerator:
    """
    Improved RAG:
      1) Provide richer product metadata to the LLM.
      2) Pre-filter obviously bad candidates (e.g., out of stock) and add a helper score.
      3) Enforce strict output + low temperature for stable, readable answers.
    """

    SYSTEM_PROMPT = (
        "You are a careful, non-hallucinating product recommender. "
        "You must only use the provided retrieved products. "
        "If the retrieved products do not fit, say so explicitly."
    )

    PROMPT_TEMPLATE = """
You are an expert product advisor helping users choose the best option from retrieved e-commerce products.

## Your task:
- Pick the single best product for the user's request.
- Use the provided metadata (price, discount, rating, stock, category, brand) to justify your choice.
- If no product fits the request, output ONLY:
"There are no good products that fit the request based on the retrieved results."

## Selection guidance:
- Prefer products that match query intent.
- Prefer IN-STOCK items.
- Better value = good rating + good discount + reasonable price.
- Use retrieval_score/helper_score as *signals* but not the only criterion.

## Retrieved products (ranked by search engine):
{retrieved_results}

## User request:
{user_query}

## Output format (follow EXACTLY):
- Best Product: <PID> — <Title>
- Why: <2-4 sentences, referencing specific metadata>
- Alternative (optional): <PID> — <Title> (<1 sentence why it could work>)
"""

    def _helper_score(self, res: Any) -> float:
        """
        Simple deterministic value score to guide the LLM.
        Uses only available fields; safe if missing.
        """
        rating = float(getattr(res, "average_rating", 0) or 0)
        discount = float(getattr(res, "discount", 0) or 0)
        price = float(getattr(res, "selling_price", 0) or 0)

        rating_norm = min(max(rating / 5.0, 0.0), 1.0)
        discount_norm = min(max(discount / 80.0, 0.0), 1.0)

        # cheaper is better, cap at 4000
        price_cap = 4000.0
        price_norm = 0.5 if price <= 0 else 1.0 - min(price, price_cap) / price_cap

        return round(0.5 * rating_norm + 0.35 * discount_norm + 0.15 * price_norm, 4)

    def _format_results(self, retrieved_results: List[Any], top_N: int) -> str:
        lines = []
        for i, res in enumerate(retrieved_results[:top_N], start=1):
            pid = getattr(res, "pid", "unknown")
            title = getattr(res, "title", "unknown title")
            price = getattr(res, "selling_price", None)
            discount = getattr(res, "discount", None)
            actual_price = getattr(res, "actual_price", None)
            rating = getattr(res, "average_rating", None)
            stock = getattr(res, "out_of_stock", None)
            brand = getattr(res, "brand", None)
            category = getattr(res, "category", None)
            subcat = getattr(res, "sub_category", None)
            retrieval_score = getattr(res, "ranking", None)

            helper = self._helper_score(res)

            lines.append(
                f"{i}. PID: {pid}\n"
                f"   Title: {title}\n"
                f"   Brand: {brand}\n"
                f"   Category: {category} / {subcat}\n"
                f"   Price: {price} | Actual: {actual_price} | Discount: {discount}%\n"
                f"   Rating: {rating}/5 | In stock: {not bool(stock)}\n"
                f"   retrieval_score: {retrieval_score} | helper_score: {helper}\n"
            )
        return "\n".join(lines)

    def generate_response(
        self,
        user_query: str,
        retrieved_results: List[Any],
        top_N: int = 20
    ) -> str:
        DEFAULT_ANSWER = (
            "RAG is not available. Check your credentials (.env file) or account limits."
        )

        # If nothing retrieved, skip LLM
        if not retrieved_results:
            return "There are no good products that fit the request based on the retrieved results."

        # Improvement #2: pre-filter out-of-stock items if we have enough left
        in_stock = [r for r in retrieved_results if not getattr(r, "out_of_stock", False)]
        if len(in_stock) >= 3:
            retrieved_results = in_stock

        try:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                return DEFAULT_ANSWER

            client = Groq(api_key=api_key)
            model_name = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

            formatted_results = self._format_results(retrieved_results, top_N)

            prompt = self.PROMPT_TEMPLATE.format(
                retrieved_results=formatted_results,
                user_query=user_query
            )

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                model=model_name,
                temperature=0.1,   # Improvement #3: stability
                max_tokens=300
            )

            generation = chat_completion.choices[0].message.content.strip()

            # Extra guard: if the model drifted, fallback cleanly
            if not generation:
                return "There are no good products that fit the request based on the retrieved results."

            return generation

        except Exception as e:
            print(f"Error during RAG generation: {e}")
            return DEFAULT_ANSWER
