from domain.chat import Message


def format_chat_history(messages: list[Message]) -> str:
    if not messages:
        return ""
    return "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in messages])


def format_knowledge_context(faqs: list[dict]) -> str:
    return "\n\n".join([f"Q: {faq['question']}\nA: {faq['answer']}" for faq in faqs])
