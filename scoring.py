def score(job):
    t = (job["title"] + job["description"]).lower()

    banned = ["risk", "compliance", "middle office", "back office", "audit", "accounting", "it", "operations"]
    if any(w in t for w in banned):
        return -100

    score = 0
    good = ["asset", "portfolio", "fund", "investment", "client", "sales", "wealth", "private", "distribution", "equity", "fixed income"]
    for w in good:
        if w in t:
            score += 2

    if "intern" in t or "stage" in t:
        score += 3
    if "may" in t or "june" in t or "asap" in t:
        score += 3

    return score
