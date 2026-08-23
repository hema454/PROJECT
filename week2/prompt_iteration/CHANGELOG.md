# Prompt Iteration Log — Article Summarization

## Version 1 (baseline)
**Prompt:**
```
Summarize this article in 3 bullet points.


The city council approved a $4.5M budget for downtown road repairs on Wednesday.
The project will begin in April and is expected to take six months. Officials said
the repairs will affect Main Street, Oak Avenue, and Third Street, with detours
planned during peak construction. Local business owners expressed concern about
reduced foot traffic during the repair period, while the mayor's office said the
long-term infrastructure investment was necessary and overdue.
```
**Changed:** N/A (starting point)
**Expected:** N/A
**Actual:** - The city council approved a $4.5 million budget for downtown road repairs, set to start in April and last six months.  
- Repairs will impact Main Street, Oak Avenue, and Third Street, with planned detours during peak construction.  
- Local business owners are worried about decreased foot traffic during repairs, while the mayor's office emphasizes the project's importance for long-term infrastructure.

## Version 2
**Prompt:**
```
Summarize this article in 3 bullet points. Do not include your own opinion.


The city council approved a $4.5M budget for downtown road repairs on Wednesday.
The project will begin in April and is expected to take six months. Officials said
the repairs will affect Main Street, Oak Avenue, and Third Street, with detours
planned during peak construction. Local business owners expressed concern about
reduced foot traffic during the repair period, while the mayor's office said the
long-term infrastructure investment was necessary and overdue.
```
**Changed:** Added a negative instruction: "Do not include your own opinion."
**Expected:** AI stops adding opinions entirely.
**Actual:** - The city council approved a $4.5 million budget for downtown road repairs, set to begin in April and last six months.
- The repairs will impact Main Street, Oak Avenue, and Third Street, with planned detours during peak construction times.
- Local business owners are worried about reduced foot traffic during the repairs, while the mayor's office emphasizes the importance of the long-term infrastructure investment.

## Version 3
**Prompt:**
```
Summarize this article in exactly 3 bullet points. Each bullet must state only a fact from the article — a specific event, number, or quote. Do not add analysis, commentary, or evaluation.


The city council approved a $4.5M budget for downtown road repairs on Wednesday.
The project will begin in April and is expected to take six months. Officials said
the repairs will affect Main Street, Oak Avenue, and Third Street, with detours
planned during peak construction. Local business owners expressed concern about
reduced foot traffic during the repair period, while the mayor's office said the
long-term infrastructure investment was necessary and overdue.
```
**Changed:** Replaced the vague negative instruction with a positive, concrete rule: each bullet must state a specific fact (event/number/quote).
**Expected:** AI produces purely factual bullets, no opinion, no hedging phrases.
**Actual:** - The city council approved a $4.5M budget for downtown road repairs on Wednesday.  
- The project will begin in April and is expected to take six months.  
- The repairs will affect Main Street, Oak Avenue, and Third Street, with detours planned during peak construction.

## Version 4
**Prompt:**
```
Summarize the article below in exactly 3 bullet points. Each bullet must state only a fact from the article — a specific event, number, or quote. Do not add analysis, commentary, or evaluation.

<article>

The city council approved a $4.5M budget for downtown road repairs on Wednesday.
The project will begin in April and is expected to take six months. Officials said
the repairs will affect Main Street, Oak Avenue, and Third Street, with detours
planned during peak construction. Local business owners expressed concern about
reduced foot traffic during the repair period, while the mayor's office said the
long-term infrastructure investment was necessary and overdue.

</article>
```
**Changed:** Wrapped the article text in <article> tags to clearly separate instructions from content.
**Expected:** AI stays more focused on facts within the article, less drift, especially on longer articles.
**Actual:** - The city council approved a $4.5M budget for downtown road repairs.  
- The project is set to begin in April and will take six months to complete.  
- The repairs will impact Main Street, Oak Avenue, and Third Street, with planned detours during construction.

## Version 5
**Prompt:**
```
Summarize the article below in exactly 3 bullet points. Each bullet must state only a fact from the article — a specific event, number, or quote. Do not add analysis, commentary, or evaluation.

Example:
<article>
The city council approved a $2M budget for park renovations on Tuesday. Construction begins in March. Three parks will be affected: Riverside, Oak Hill, and Central.
</article>
Output:
- City council approved a $2M budget for park renovations on Tuesday.
- Construction is set to begin in March.
- Three parks affected: Riverside, Oak Hill, and Central.

Now summarize this article:
<article>

The city council approved a $4.5M budget for downtown road repairs on Wednesday.
The project will begin in April and is expected to take six months. Officials said
the repairs will affect Main Street, Oak Avenue, and Third Street, with detours
planned during peak construction. Local business owners expressed concern about
reduced foot traffic during the repair period, while the mayor's office said the
long-term infrastructure investment was necessary and overdue.

</article>
```
**Changed:** Added a one-shot example showing the exact input/output format.
**Expected:** AI matches the demonstrated bullet style and length more consistently than V4.
**Actual:** - City council approved a $4.5M budget for downtown road repairs on Wednesday.  
- The project will begin in April and is expected to take six months.  
- Repairs will affect Main Street, Oak Avenue, and Third Street, with detours planned during peak construction.
