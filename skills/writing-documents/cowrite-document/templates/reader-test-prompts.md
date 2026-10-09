# Reader-test prompt pack

Use these with a reader who has seen nothing but the document: a fresh sub-agent, or a fresh chat session the user opens. Paste the whole document above the prompt. Never include the drafting conversation, notes or your own summary: the point is to see what the document alone conveys.

## A. Question test (one prompt per predicted reader question)

```
You are reading the document above for the first time. You have no other
context about the project, team or company.

Question: {question}

Reply in exactly this format:
ANSWER: <your answer, citing the section heading you relied on>
CONFIDENCE: high | medium | low
UNCLEAR: <anything in the document that was ambiguous for this question, or "none">
ASSUMED: <knowledge the document seems to expect you to already have, or "none">
```

Score each reply against the answer the authors intended:
- **pass**: correct, high confidence, nothing unclear;
- **partial**: correct but low confidence, or needed an assumption;
- **fail**: wrong, missing, or answered from guesswork.

## B. Whole-document checks (one prompt each)

1. **Ambiguity.** "List every sentence or term in the document above that a reader could reasonably interpret in two different ways. Quote it and give both readings."
2. **Assumed knowledge.** "List the acronyms, names, systems, past events and decisions the document refers to without explaining. For each, say whether the document still makes sense without knowing it."
3. **Contradictions.** "List any statements in the document that contradict each other: numbers, dates, scope, owners, or recommendations. Quote both sides."
4. **The ask.** "In one sentence each: what does this document want the reader to do or decide, by when, and why? If you can't tell, say so."
5. **Skim test.** "Read only the title, the headings and the first sentence of each section. What is the document's main point and its main argument?"
6. **Hostile reviewer.** "You are a sceptical senior reviewer. Name the three weakest points in the argument and the evidence that would be needed to fix each."

## C. Predicting reader questions

Good test questions are ones a real reader would ask when deciding whether to care, agreeing to the decision, or implementing it:

- What is being proposed or decided, in one sentence?
- Why now, and what happens if we do nothing?
- What does it cost (money, people, time), and who pays?
- What changes for my team / for users?
- What alternatives were considered and why were they rejected?
- What are the risks and how would we know it's going wrong?
- What do you need from me, and by when?
- How will we measure success?
- What is explicitly out of scope?
- Who owns the next step?

Pick 5-10 of these that match the document type, and add 2-3 specific ones ("does the migration need downtime?").

## D. Results table

| # | Question | Intended answer | Reader answer | Score | Fix in section |
|---|---|---|---|---|---|
