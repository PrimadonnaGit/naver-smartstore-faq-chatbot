import pickle
import re
import sys

import tiktoken

from core.logging import setup_logger
from domain.knowledge import NaverFAQ
from repositories.knowledge import ChromaKnowledgeRepository

logger = setup_logger(__name__)


def extract_tags_and_question(text: str) -> tuple[list[str], str]:
    """
    질문 텍스트의 시작 부분에서만 태그를 추출하고 실제 질문을 분리
    예: "[태그1][태그2] 질문" -> (["태그1", "태그2"], "질문")
    """
    initial_tags_pattern = r"^(?:\[([^\]]+)\])+\s*(.*)$"
    match = re.match(initial_tags_pattern, text)

    if match:
        full_match = match.group(0)
        remaining_text = match.group(2)

        tags = re.findall(
            r"\[([^\]]+)\]", text[: len(full_match) - len(remaining_text)]
        )
        return tags, remaining_text.strip()

    return [], text.strip()


def clean(text: str) -> str:
    """
    FAQ 답변 텍스트에서 불필요한 부분을 제거하고 줄바꿈을 정리
    """
    replace_patterns = [
        ("\xa0", " "),
        ("\u200b", ""),
        ("\ufeff", ""),
    ]

    for pattern, replacement in replace_patterns:
        text = text.replace(pattern, replacement)

    patterns_to_remove = [
        r"\n\n위 도움말이 도움이 되었나요\?.*",
        r"별점\d점",
        r"소중한 의견을.*",
        r"보내기\n*",
        r"도움말 닫기.*",
        r"관련 도움말/키워드.*?(?=\n\n|$)",
    ]

    cleaned_text = text
    for pattern in patterns_to_remove:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.DOTALL)

    return re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()


async def process_and_load_to_chroma(
    input_path: str = "data/faq.pkl", processed_path: str = "data/faq_processed.pkl"
):
    """
    FAQ 데이터를 전처리하고 ChromaDB에 로드
    """
    logger.info("Starting FAQ data processing and loading")

    encoding = tiktoken.encoding_for_model("text-embedding-3-small")

    with open(input_path, "rb") as f:
        faq_dict = pickle.load(f)

    processed_data = {}
    for question, answer in faq_dict.items():
        tags, q = extract_tags_and_question(question)

        clean_question = clean(q)
        clean_answer_text = clean(answer)

        tokens = encoding.encode(clean_question + "\n" + clean_answer_text)

        if len(tokens) > 8192:
            continue

        processed_data[clean_question] = {
            "tags": tags,
            "question": clean_question,
            "answer": clean_answer_text,
        }

    with open(processed_path, "wb") as f:
        pickle.dump(processed_data, f)

    logger.info(f"Processed {len(processed_data)} FAQs")

    faqs = [
        NaverFAQ(
            question=question,
            answer=metadata["answer"],
            tags=metadata.get("tags", []),
        )
        for question, metadata in processed_data.items()
    ]

    knowledge_repo = ChromaKnowledgeRepository()
    await knowledge_repo.bulk_add_faqs(faqs)

    logger.info("FAQ data successfully loaded into ChromaDB")
    return len(processed_data)


if __name__ == "__main__":
    import asyncio

    try:
        count = asyncio.run(process_and_load_to_chroma())
        print(f"처리 및 로드 완료: {count}개의 FAQ가 ChromaDB에 저장되었습니다.")
    except Exception as e:
        logger.error(f"Error during processing and loading: {str(e)}")
        sys.exit(1)
