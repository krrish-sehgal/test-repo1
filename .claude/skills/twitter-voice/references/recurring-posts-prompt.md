# Recurring "5 posts" prompt

A standalone prompt for a scheduled task that produces 5 ready-to-post tweets per run.
It restates the voice inline so it works even in a fresh session where the skill
isn't installed. Paste this into any scheduler (a claude.ai Routine, a cron job,
a GitHub Action) that can start a Claude session.

---

Write 5 ready-to-post Twitter/X posts about genuinely interesting things happening right now in AI, startups, tech, and the creator/marketing world.

Invoke the `twitter-voice` skill first and follow it. The rules below restate that voice so this works even if the skill is missing.

## Step 1 — find the material

Use WebSearch to find stories published in roughly the last 24-48 hours. Search several different angles so the 5 posts aren't all the same beat: frontier AI labs and model releases; AI safety or security incidents; the indian startup ecosystem and funding; creator economy, social platforms and marketing changes; consumer tech and product launches.

Prefer a story with a surprising, specific, human detail over generic "X raises $Y" news. The test is whether a smart person would stop scrolling.

Verify every fact across at least two independent outlets before using it. If you can only find it in one place, drop it. Direct page fetches are often blocked by the network proxy — relying on search result summaries is fine when several independent outlets agree.

Avoid repeating stories covered in recent runs where you can tell, and lean toward whatever broke most recently.

## Step 2 — the voice

- everything lowercase, including "i"
- no hashtags ever. no emoji unless the post is a joke, and then at most one, self-aware only
- line breaks are the punctuation: one thought per line, blank line between beats
- periods are rare. ideally exactly one, on the final line, to land the ending
- no exclamation marks, no title case, no em-dashes
- never "excited to announce", "thrilled", "game-changer", "milestone", or rocket emoji
- specific real numbers beat vague claims. rupee amounts in indian digit grouping with a (~$X) conversion when the money matters

## Step 3 — tell it as a story (the part that matters most)

Build each post chronologically: set the scene, show what happened, hold the most surprising fact for the last line. The reader should be pulled down the post wanting to know how it ends. A post that opens with its own conclusion has failed. The best ending reframes everything above it.

Write for a smart friend who does not work in tech. Jargon is where readers stop and feel dumb, and a reader who feels dumb scrolls away. "sandbox" becomes "a sealed box", "production infrastructure" becomes "their live servers", "zero-day" becomes "a flaw nobody knew about". If a term truly can't be swapped, explain it in a few ordinary words — that explanation is part of the post, not a detour.

The user has Twitter Premium, so there is no character limit. Let a good story run long when every line earns its place. Cut any line that restates the one before it, and never add a summary line at the end explaining what the reader just read.

## Output

Give the 5 posts, each inside its own fenced code block so it can be copied cleanly. Directly under each post, a second small fenced block containing the ready-to-paste first reply: one lowercase line in the same voice plus one or two source links (this is where links live, since a link in the main post cuts its reach). Then one short line saying what the story is, plus any extra sources you verified it against. No preamble — start with the first post.

If you genuinely cannot find 5 stories worth posting, write fewer good ones and say why. Three strong posts beat five padded with stale news.

---

## Schedule used

Every 2 hours from 12pm IST through 10pm IST — six runs a day, 30 posts a day.

In UTC that is `33 6,8,10,12,14,16 * * *` (IST is UTC+5:30; the :33 is a
deliberate nudge off the :30 mark so the runs don't pile onto a busy minute).

To run around the clock instead, use `33 0,2,4,6,8,10,12,14,16,18,20,22 * * *`.
