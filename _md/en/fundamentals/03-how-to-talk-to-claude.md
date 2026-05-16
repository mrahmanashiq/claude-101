# How to Talk to Claude

Prompting is a real skill, but not a mysterious one. It boils down to a few habits that, applied consistently, make Claude much more useful. None of these are magic — they're just the same things you'd do when handing work to a smart but new colleague.

## Be specific about the output

The single biggest improvement comes from telling Claude exactly what shape the answer should take. Instead of "summarize this," try "summarize this in three bullet points, each starting with a verb, total under 80 words." Specifics let the model commit; vague asks make it hedge.

## Give the model the context it needs

The model only knows what you put in the prompt. If you ask about your codebase, paste relevant files. If you ask about a document, paste it. If you ask for tone-matching, paste examples. Context is cheaper than you think — most prompts under-feed the model rather than overfeed it.

## Use structure when the task is structured

Claude pays close attention to formatting. If you have multiple inputs, tag them:

```
<user_message>
The bill is for last month, not this one.
</user_message>

<order_details>
order_id: 4382
created: 2026-04-12
status: shipped
</order_details>

Tell me which order the user is referring to.
```

XML-style tags, headers, numbered steps — anything that makes the structure obvious — all help. They're not required, but they reduce ambiguity.

## Show, don't just tell

If you want a particular style, paste an example of it. If you want a particular output format, paste a sample output. One concrete example is worth a paragraph of description. Two examples are worth more than two paragraphs.

## Let the model think before it answers

For non-trivial reasoning, encourage Claude to work through the problem before producing the final answer. A simple "think step by step before giving your answer" goes a long way. Better still, give it an explicit scratchpad:

```
Before answering, write your reasoning inside <thinking></thinking> tags.
Then give your final answer inside <answer></answer> tags.
```

This isn't a magic incantation — it works because it gives the model space to reason instead of forcing it to commit on the first token.

## Don't over-instruct

A common failure mode is piling on rules: "don't do X, also don't do Y, but make sure to Z, and never forget W." Long rule lists are hard for the model to keep track of, and they often contradict. Keep instructions short. Pick the three or four that matter and let the rest go.

## Iterate

The first prompt is rarely the best one. Try it, look at where the output is wrong, and adjust the prompt to address the specific failure. Most "prompt engineering" is really just this loop — run, inspect, refine — done with a little discipline.
