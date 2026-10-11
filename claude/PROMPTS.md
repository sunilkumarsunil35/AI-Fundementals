# Learning with Claude

Claude is your tutor and reviewer here, not your answer key. The tracker's **Hint ↗** and **Review ↗**
buttons open claude.ai with the first two prompts below already filled in for that exercise. The rest you
paste yourself. Replace the `<...>` parts.

## The daily loop (about an hour)

1. Pick the tracker's **Next up** exercise. Read its docstring.
2. **Hint** prompt. Read the explanation, close the chat, try on your own for 15 minutes.
3. Still stuck? Go back to the same chat and ask for the next hint. Ask for code only as a last resort.
4. `sh run-tests.sh --mine -k <function_name>` until it passes.
5. **Review** prompt with your code. Then read `src/solutions/...` and compare.
6. Log one line in the tracker: what you learned, what Claude had to correct.

## 1. Hint (learn the idea, not the answer)

```
I'm an SDET learning AI fundamentals in Python, week <n> (<topic>).
Exercise "<title>" (src/exercises/<topic>/<file>.py, function <name>).

Task: <paste the docstring>

Teach me the idea behind it in plain words with a tiny example, explain why it matters for
testing AI systems, then give me ONE hint at a time. Don't write the solution code unless I ask.
```

## 2. Review (after your test passes)

````
I'm an SDET learning AI fundamentals in Python. Review my solution to this exercise
(src/exercises/<topic>/<file>.py, function <name>).

Task: <paste the docstring>

Check correctness and edge cases, compare it with the simplest idiomatic approach, and tell me how
I would test this in a real AI feature at work. Then ask me one follow-up interview question.

My code:
```python
<paste your code>
```
````

## 3. Explain it back (end of each exercise)

```
I'll explain <concept> in three sentences. Don't explain it yourself first.
Tell me what I got right, what is missing or wrong, and give me one tricky question to check.

My explanation: <...>
```

## 4. Weekly quiz (end of each week)

```
Quiz me on week <n> of my AI-for-SDET plan: <topics>. Ask 8 questions one at a time:
3 concept questions, 3 "what would you test?" scenarios, 2 small code-reading questions.
Wait for my answer each time, grade it 0-2, and give the score and my weakest area at the end.
```

## 5. Apply it at work (the weekly SDET deliverable)

```
At work I test <feature, e.g. a support chatbot that answers from our help center>.
This week I learned <topic>. Help me design a test plan for it that uses <the techniques>:
list the risks, the test cases (with how each is checked automatically), the data I need, and
what must stay a human review. Ask me questions first if anything is unclear.
```

## 6. Debug a failing test

```
My test for <function> fails. Don't fix it for me: help me find the bug by asking me questions
about what I expect at each step.

Test output:
<paste the pytest failure>

My code:
<paste>
```

## 7. Go deeper (optional)

```
I finished the exercise "<title>". What does the production version of this look like
(libraries, scale, failure modes)? Give me a 20-minute reading/doing plan with links to official docs.
```

## Rules that keep you learning

- Type the code yourself, even if Claude showed it.
- Ask "why" twice for every answer. If Claude can't connect it to testing, ask it to.
- If Claude says something that contradicts a test here, the test wins until you've checked why.
- Redo two old exercises each week without help. Mark them **Revise** in the tracker if you can't.
