import json
import os
import random
import re
import urllib.request
import urllib.error

from dotenv import load_dotenv
from services.question_bank import QUESTION_BANK

load_dotenv()


def _normalize_topics(topic_text):
    if not topic_text:
        return []
    raw = re.split(r"[,;\n|]+", str(topic_text))
    topics = []
    for item in raw:
        t = re.sub(r"^\s*[-*•]\s*", "", item.strip())
        t = re.sub(r"^\s*\d+\s*[.):-]\s*", "", t).strip()
        if t and t.lower() not in {x.lower() for x in topics}:
            topics.append(t)
    return topics


def _remove_question_number(text):
    if not text:
        return ""
    text = str(text).strip()
    for pattern in (
        r"^\s*Question\s*\d+\s*[:.)-]\s*",
        r"^\s*Q\s*\d+\s*[:.)-]\s*",
        r"^\s*\d+\s*[:.)-]\s*",
    ):
        text = re.sub(pattern, "", text, count=1, flags=re.I)
    # Handle accidental double numbering: Q1. 1. Question
    for _ in range(3):
        new = re.sub(r"^\s*(?:Q\s*)?\d+\s*[:.)-]\s*", "", text, count=1, flags=re.I)
        if new == text:
            break
        text = new
    return text.strip()


def _is_non_question_line(line):
    if not line:
        return True
    s = re.sub(r"\s+", " ", str(line).lower()).strip()
    blocked = {
        "questions", "questions:", "question paper", "question paper:",
        "general instructions", "general instructions:", "instructions", "instructions:",
        "section a", "section a:", "section b", "section b:", "section c", "section c:",
        "answers", "answers:", "solutions", "solutions:", "good luck",
        "all questions are compulsory.", "answer all questions.",
        "read each question carefully before answering.",
        "read every question carefully.", "answer according to the marks allotted.",
        "show your working wherever necessary.", "write your answers clearly.",
    }
    if s in blocked:
        return True
    if s.startswith(("topic:", "topics:", "subject:", "difficulty:", "answer:", "solution:")):
        return True
    return bool(re.fullmatch(r"[-_=*#\s]+", s))


def _clean_questions(text, requested):
    if not text:
        return []
    text = str(text).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"```(?:text|markdown)?", "", text, flags=re.I).replace("```", "")

    # Prefer numbered-question extraction, including multi-line questions.
    marker = re.compile(r"(?im)^\s*(?:Q(?:uestion)?\s*)?\d+\s*[.)\-:]\s+")
    starts = list(marker.finditer(text))
    candidates = []
    if starts:
        for i, m in enumerate(starts):
            end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
            candidates.append(text[m.start():end].strip())
    else:
        # Accept bullets if the model ignored numbering.
        candidates = re.split(r"\n\s*(?=[-•*]\s+)", text)
        if len(candidates) <= 1:
            candidates = text.splitlines()

    result = []
    seen = set()
    for raw in candidates:
        q = _remove_question_number(raw)
        q = re.sub(r"^\s*[-•*]\s+", "", q).strip()
        q = re.sub(r"\s+", " ", q).strip()
        if not q or _is_non_question_line(q) or len(q) < 15:
            continue
        # Remove an accidental leading second number after line joining.
        q = _remove_question_number(q)
        key = q.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(q)
        if len(result) >= requested:
            break
    return result


def _topic_instruction(topics):
    topic_list = "\n".join(f"- {t}" for t in topics)
    return f"""
USER-SUPPLIED TOPICS (STRICT WHITELIST):
{topic_list}

Every question MUST be directly based on at least one of these topics.
Do not use another chapter or unrelated concept just because it belongs to the subject.
If a topic is a specific mathematical/computing concept, ask questions that actually test that concept.
Do not create generic 'What is X?', 'Define X', or 'Compare X' questions unless that is genuinely appropriate to the supplied topic.
For Mathematics, prefer calculations, evaluations, derivations, proofs, applications and problem solving.
Topic names are internal instructions. Do not print topic labels in the questions.
"""


def _ai_prompt(subject, topics, difficulty, questions):
    return f"""You are an expert university examination paper setter.

SUBJECT: {subject}
DIFFICULTY: {difficulty}
NUMBER OF QUESTIONS: {questions}

{_topic_instruction(topics)}

Generate exactly {questions} genuine examination questions.
Return ONLY a numbered list, one question per item:
1. ...
2. ...
3. ...

Rules:
- No answers or solutions.
- No General Instructions.
- No section headings.
- No metadata.
- No topic headings.
- Do not repeat questions.
- Keep every question academically meaningful and specific to the supplied topics.
- For multiple supplied topics, distribute questions across them when possible.
"""


def _call_ollama(prompt, model, host, temperature=0.65):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature}
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{host}/api/generate", data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("response", "") or ""


def _generate_with_ollama(prompt, questions):
    model = os.getenv("OLLAMA_MODEL", "gemma3:latest").strip()
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    try:
        output = _call_ollama(prompt, model, host)
        result = _clean_questions(output, questions)
        if len(result) < questions:
            retry = prompt + "\nIMPORTANT: Your previous response was incomplete. Return the full requested list with exactly the requested number of questions."
            output = _call_ollama(retry, model, host, 0.55)
            result = _clean_questions(output, questions)
        return result
    except (urllib.error.URLError, TimeoutError, ValueError, OSError, json.JSONDecodeError):
        return []


def _generate_with_openai(prompt, questions):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return []
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model, temperature=0.65,
            messages=[
                {"role": "system", "content": "Generate only topic-restricted academic examination questions."},
                {"role": "user", "content": prompt},
            ],
        )
        output = response.choices[0].message.content or ""
        return _clean_questions(output, questions)
    except Exception:
        return []


def _topic_keys(topic):
    t = topic.lower().strip()
    keys = {t, re.sub(r"[^a-z0-9]+", " ", t).strip()}
    aliases = {
        "math": "mathematics", "maths": "mathematics", "mathematics": "mathematics",
        "fuzzy logic": "fuzzy logic", "fuzzylogic": "fuzzy logic",
        "database management system": "database management system", "dbms": "database management system",
    }
    if t in aliases:
        keys.add(aliases[t])
    return keys


def _question_bank_fallback(subject, topics, questions):
    subject_key = subject.strip().lower()
    bank = QUESTION_BANK.get(subject_key, {})
    result = []
    # Exact and normalized topic matching.
    for topic in topics:
        keys = _topic_keys(topic)
        for bank_topic, pool in bank.items():
            norm = bank_topic.lower().strip()
            if norm in keys or any(k == norm for k in keys):
                items = list(pool)
                random.shuffle(items)
                result.extend(items)
    # If no exact key exists, do not invent unrelated bank questions.
    unique, seen = [], set()
    for q in result:
        q = _remove_question_number(q)
        key = re.sub(r"\s+", " ", q.lower()).strip()
        if q and key not in seen:
            seen.add(key)
            unique.append(q)
    return unique[:questions]


def _apply_final_numbering(questions, total):
    final = []
    seen = set()
    for q in questions:
        q = _remove_question_number(q)
        if not q or _is_non_question_line(q):
            continue
        key = re.sub(r"\s+", " ", q.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        final.append(f"Q{len(final) + 1}. {q}")
        if len(final) >= total:
            break
    return final


def generate_question_paper(college, university, exam, exam_date, exam_time,
                            subject, topic, difficulty, marks, questions):
    total = max(1, int(questions))
    topics = _normalize_topics(topic)
    if not topics:
        raise ValueError("Please provide at least one topic.")

    prompt = _ai_prompt(subject, topics, difficulty, total)
    generated = _generate_with_ollama(prompt, total)

    if len(generated) < total:
        extra = _generate_with_ollama(
            prompt + f"\nReturn at least {total} complete questions. Do not stop early.", total
        )
        for q in extra:
            if q.lower() not in {x.lower() for x in generated}:
                generated.append(q)
            if len(generated) >= total:
                break

    if len(generated) < total:
        extra = _generate_with_openai(prompt, total)
        for q in extra:
            if q.lower() not in {x.lower() for x in generated}:
                generated.append(q)
            if len(generated) >= total:
                break

    if len(generated) < total:
        extra = _question_bank_fallback(subject, topics, total)
        for q in extra:
            if q.lower() not in {x.lower() for x in generated}:
                generated.append(q)
            if len(generated) >= total:
                break

    final_questions = _apply_final_numbering(generated, total)
    if len(final_questions) < total:
        raise RuntimeError(
            f"Only {len(final_questions)} valid questions could be generated for the supplied topic(s). "
            "Please make sure Ollama is running and try again."
        )

    topic_string = ", ".join(topics)
    paper = f"""============================================================
                    {college.upper()}

                    {university.upper()}

                    {exam.upper()}

============================================================

Subject          : {subject}
Topic            : {topic_string}
Difficulty       : {difficulty}
Exam Date        : {exam_date}
Exam Duration    : {exam_time}
Maximum Marks    : {marks}
Total Questions  : {total}

============================================================

                    GENERAL INSTRUCTIONS

All questions are compulsory.
Read each question carefully before answering.
Answer according to the marks allotted.
Show your working wherever necessary.

============================================================

                    QUESTION PAPER

============================================================

"""
    paper += "\n\n".join(final_questions)
    paper += "\n\n============================================================\n                    END OF QUESTION PAPER\n============================================================\n"
    return paper
