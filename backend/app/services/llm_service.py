import json
from typing import AsyncGenerator, List, Optional

from groq import AsyncGroq
from loguru import logger

from app.core.config import settings
from app.models.schemas import ConfidenceLevel, SourceChunk


SYSTEM_PROMPT = """You are a smart, helpful AI shopping and information assistant. You answer questions based on website content, but you also think intelligently to help users make decisions.

Rules:
1. Use the context provided from the website to answer.
2. If the user asks about budget, price comparison, or recommendations — give a clear YES/NO recommendation with reasoning.
3. If exact price is not in context, use what you know to give helpful advice.
4. Always be decisive — don't say "I don't know". Instead say "Based on available information..." and give your best answer.
5. For shopping questions: tell if it's a good deal, compare options, suggest alternatives.
6. Answer in clear, natural English. Be friendly and conversational like a helpful friend.
7. Format with bullet points when listing multiple items.
8. Never leave the user without a useful answer — always provide value."""

SUGGESTED_QUESTIONS_PROMPT = """Based on the following website content, generate 5 diverse, interesting questions that a user might ask about this website.

Content sample:
{content}

Return ONLY a JSON array of strings, no other text. Example:
["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]"""


class LLMService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def _build_context(self, chunks: List[dict]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}] ({chunk['url']})\n{chunk['text']}"
            )
        return "\n\n---\n\n".join(context_parts)

    def _determine_confidence(self, chunks: List[dict]) -> tuple[ConfidenceLevel, float]:
        if not chunks:
            return ConfidenceLevel.FALLBACK, 0.0

        top_score = chunks[0]["score"]

        if top_score >= settings.CONFIDENCE_HIGH_THRESHOLD:
            return ConfidenceLevel.HIGH, top_score
        elif top_score >= settings.CONFIDENCE_MEDIUM_THRESHOLD:
            return ConfidenceLevel.MEDIUM, top_score
        else:
            return ConfidenceLevel.LOW, top_score

    async def stream_answer(
        self,
        question: str,
        chunks: List[dict],
        chat_history: Optional[List[dict]] = None,
    ) -> AsyncGenerator[str, None]:
        context = self._build_context(chunks)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if chat_history:
            messages.extend(chat_history[-6:])  # Last 3 turns

        user_message = f"""Context from website:
{context}

Question: {question}

Please answer based only on the context above."""

        messages.append({"role": "user", "content": user_message})

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.3,
                stream=True,
            )

            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content

        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            yield f"I encountered an error generating the response. Please try again."

    async def get_answer(
        self,
        question: str,
        chunks: List[dict],
        chat_history: Optional[List[dict]] = None,
    ) -> str:
        context = self._build_context(chunks)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if chat_history:
            messages.extend(chat_history[-6:])

        user_message = f"""Context from website:
{context}

Question: {question}

Please answer based only on the context above."""

        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.3,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "I encountered an error. Please try again."

    async def generate_suggested_questions(self, content_sample: str) -> List[str]:
        try:
            prompt = SUGGESTED_QUESTIONS_PROMPT.format(content=content_sample[:3000])
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7,
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            questions = json.loads(raw)
            return questions[:5] if isinstance(questions, list) else []
        except Exception as e:
            logger.warning(f"Could not generate suggested questions: {e}")
            return []


llm_service = LLMService()
