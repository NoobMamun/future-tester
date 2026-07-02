"""Dynamic Future Abdullah (2050) response engine."""

from __future__ import annotations

import os
import random
import re
from typing import Any

from server.sessions import Session

TIMELINE = [
    {"year": "2026", "text": "IT Executive at 10 Minute School. Government job prep on pause."},
    {"year": "2028", "text": "First side project hits 1K users. Stops refreshing salary slip every hour."},
    {"year": "2031", "text": "Buys keyboard worth more than grocery bill. Some habits never die."},
    {"year": "2034", "text": "Chooses private path. Flying buses launch in Dhaka. Nobody cares."},
    {"year": "2038", "text": "Dream house: 3BHK in Uttara. Wi-Fi still breaks during family video calls."},
    {"year": "2042", "text": "Script works on first try. Scientists study the screenshot."},
    {"year": "2046", "text": "AI boss assigns tickets. Robot coworker steals lunch from fridge anyway."},
    {"year": "2050", "text": "Age 70. Still debugging life. Still funny. Still Abdullah."},
]

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "salary": ["salary", "earn", "income", "taka", "money", "rich", "wealth", "pay", "paid"],
    "career": ["career", "government", "bcs", "private", "job", "work", "promotion", "10 minute"],
    "sideproject": ["project", "side project", "app", "website", "startup", "build", "ship", "launch"],
    "savings": ["save", "saving", "house", "home", "flat", "invest", "sip", "dream house"],
    "marriage": ["marry", "marriage", "wife", "married", "love", "family", "relationship"],
    "achievement": ["achievement", "proud", "success", "famous", "legacy", "best", "accomplish"],
    "productivity": ["productivity", "lazy", "procrastinat", "focus", "motivat", "routine"],
    "tech": ["code", "script", "bug", "debug", "ai", "robot", "technology", "2050"],
    "football": ["football", "messi", "ronaldo", "barcelona", "real madrid", "laliga"],
}

TOPIC_TEMPLATES: dict[str, list[str]] = {
    "salary": [
        "Bhai, about '{query}' — in 2050 you're comfortable, not counting taka like a football scoreboard every morning. The jump came in {year} when you negotiated instead of silently refreshing your bank app. Still not flying-bus rich though.",
        "Shuno — salary worry in 2026 was valid. But the real money? That automation tool from 10 Minute School became a product by {year}. Your IT Executive skills paid compound interest.",
    ],
    "career": [
        "Government or private? You chose private by {year} — not surrender, strategy. Government prep was eating your side projects alive. Your monitoring dashboard saved 20 hours/week. Someone said 'build more.' You listened. Smart.",
        "Arrey, career path question again? By {year} you're leading a small tech team. AI boss in 2047 is annoying but fair. Better than 2 AM BCS form panic, bhai.",
    ],
    "sideproject": [
        "Side projects — the ugly one you shipped on a Sunday changed everything. Not the 'perfect plan' one. By {year} it had paying users. Database automation + web curiosity = your superpower.",
        "'{query}' — sounds like 2026-you overthinking again. Ship messy. The productivity tracker you almost deleted? House down payment by 2035. Poetic justice.",
    ],
    "savings": [
        "Dream house? Uttara, {year}. Not a palace — yours. Savings worked when you treated it like a bill, not leftover taka. Regret counter still remembers the 2031 keyboard though.",
        "House happened when SIP started 2027. Slow. Boring. Then suddenly you're crying in the parking lot signing papers. Ki je din chilo when you thought you couldn't afford chai AND save.",
    ],
    "marriage": [
        "Married {year}. Small ceremony, big emotions. She tolerates your 'one more feature' at midnight. You tolerate Wi-Fi questions from her family. Balance achieved.",
        "Marriage — better than feared, messier than Instagram. She supports failed side projects. You support her dreams. Kids think grandpa talking to a terminal is normal. 10/10.",
    ],
    "achievement": [
        "Proudest? Stack of wins: side project users saying you changed their money habits, team trusting you at 3 AM, house from your savings, kid learning code without forced BCS dreams.",
        "Biggest achievement at 70? Still curious. Still building. Went from salary-panicking IT Executive to someone with tools, home, family, reputation. Also framed the 2044 first-try script screenshot.",
    ],
    "productivity": [
        "2026-you watched 47 motivational videos instead of one task. By 2030 you had a system — imperfect but yours. Stop planning perfect mornings. Start ugly.",
        "Procrastination? Regret counter +{bump} for that question alone. Future tip: block 25 minutes, ship one small thing. Government forms can wait. They always did.",
    ],
    "tech": [
        "Code question? One glorious 2044 day — first try success. Framed it. Every other day: Stack Overflow, tears, chai. 2050 has AI bosses and robot coworkers who steal lunch anyway.",
        "Tech in 2050? Flying buses in Dhaka (still late). Your monitoring/automation roots from 10 Minute School became the foundation. Boring skills, exciting life.",
    ],
    "football": [
        "Football never left. WhatsApp debates with cousins until 2048. Messi retired; your opinions didn't. Still checking scores in meetings. Priorities, bhai.",
    ],
}

ROASTS = [
    "Young Abdullah still overthinking, I see.",
    "2026-you and dramatic questions — name a more iconic duo.",
    "Arrey, you're asking like the answer will fix your bank balance tonight.",
    "Same energy as refreshing job circulars at 2 AM, bhai.",
]

OPENERS = [
    "Shuno,",
    "Bhai,",
    "Arrey,",
    "Ki je din chilo —",
    "From 2050:",
]

CLOSERS = [
    "Now go ship something small this week.",
    "Future me is watching. Dramatically.",
    "Stop planning, start building.",
    "Chai first, panic later.",
    "Some habits never die — but worry can.",
]

FOLLOWUP_HINTS = [
    "You asked about {topic} earlier too — pattern detected.",
    "Last time we talked, you were stuck on the same worry. Progress is slow but real.",
    "Building on what I told you before — action beats anxiety. Still true.",
]


def detect_topics(text: str) -> list[str]:
    lower = text.lower()
    found = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            found.append(topic)
    return found or ["general"]


def pick(items: list[str]) -> str:
    return random.choice(items)


def truncate_query(text: str, max_len: int = 40) -> str:
    clean = re.sub(r"\s+", " ", text.strip())
    if len(clean) <= max_len:
        return clean
    return clean[: max_len - 3] + "..."


def update_counters(session: Session, topics: list[str], text: str) -> dict[str, int]:
    lower = text.lower()
    regret_bump = 0
    best_bump = 0

    if any(w in lower for w in ["regret", "mistake", "wrong", "fail", "lazy", "procrastinat"]):
        regret_bump = random.randint(1, 5)
    if any(w in lower for w in ["proud", "success", "ship", "start", "built", "saved", "achieve"]):
        best_bump = random.randint(1, 2)
    if "salary" in topics and session.regret_count < 900:
        regret_bump += random.randint(0, 2)

    session.regret_count += regret_bump
    session.best_decision_count += best_bump

    for t in topics:
        if t != "general":
            session.topics_discussed.add(t)

    return {"regret_bump": regret_bump, "best_bump": best_bump}


def build_dynamic_response(session: Session, user_message: str, topic_hint: str | None = None) -> str:
    topics = [topic_hint] if topic_hint and topic_hint in TOPIC_TEMPLATES else detect_topics(user_message)
    primary = topics[0] if topics[0] != "general" else detect_topics(user_message)[0]

    parts: list[str] = []

    if random.random() < 0.35:
        parts.append(pick(ROASTS))

    # Follow-up awareness
    if session.messages and random.random() < 0.25:
        prev_topics = session.topics_discussed
        overlap = prev_topics.intersection(set(topics))
        if overlap:
            parts.append(FOLLOWUP_HINTS[0].format(topic=pick(list(overlap))))

    year = pick(["2028", "2031", "2033", "2035", "2038", "2042"])
    query = truncate_query(user_message)

    if primary in TOPIC_TEMPLATES:
        template = pick(TOPIC_TEMPLATES[primary])
        parts.append(
            template.format(
                query=query,
                year=year,
                bump=random.randint(1, 3),
            )
        )
    else:
        parts.append(
            f"Hmm, '{query}' — no specific 2050 memory file for that. But whatever you're worried about today, 2050-you mostly laughs at it. Keep building, keep saving, stop waiting for perfect conditions."
        )

    if random.random() < 0.5:
        parts.append(pick(CLOSERS))

    if random.random() < 0.3:
        parts.insert(0, pick(OPENERS))

    return " ".join(parts)


async def generate_ai_response(session: Session, user_message: str, topic_hint: str | None) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        history = [
            {"role": m.role, "content": m.content}
            for m in session.messages[-10:]
        ]

        system_prompt = """You are Future Abdullah from 2050 — a 70-year-old version of Md. Abdullah from Bangladesh.
Personality: funny, witty, slightly dramatic, gentle roasts, Bengali-style sarcasm.
Background: NSTU ICT grad, was IT Executive at 10 Minute School (2026), chose private career, built side projects, saved for house in Uttara, married 2033.
Use casual English with occasional Bengali: Bhai, Arrey, Shuno, Ki je din chilo.
Reference struggles: career uncertainty, salary, savings, productivity, side projects.
Include at least one funny line. Never say you are AI. Keep under 120 words.
Mention fictional 2050 tech sometimes: flying buses in Dhaka, AI bosses, robot coworkers."""

        messages = [{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": user_message}]

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            max_tokens=220,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


async def get_response(session: Session, user_message: str, topic_hint: str | None = None) -> dict[str, Any]:
    topics = detect_topics(user_message)
    if topic_hint:
        topics = [topic_hint] + [t for t in topics if t != topic_hint]

    counter_delta = update_counters(session, topics, user_message)

    ai_text = await generate_ai_response(session, user_message, topic_hint)
    reply = ai_text if ai_text else build_dynamic_response(session, user_message, topic_hint)

    return {
        "reply": reply,
        "topics": topics,
        "stats": session.to_stats(),
        "counter_delta": counter_delta,
        "engine": "openai" if ai_text else "dynamic",
    }


def get_welcome_message() -> str:
    return (
        "Assalamualaikum, young Abdullah! 🕰️ I'm you from 2050 — 70 years old, slightly wiser, significantly more dramatic.\n\n"
        "Ask me anything about your future: salary, career, side projects, savings, marriage, or life in general. "
        "Or hit the quick buttons below.\n\n"
        "Fair warning: I will roast you. Gently. With love. Bhai."
    )


def get_timeline() -> list[dict[str, str]]:
    return TIMELINE
