# Recurring posts prompt

The standalone prompt used by the twice-daily cloud routine. It restates the voice so it
works in a fresh session, but its first job is to check out the working branch and read
the real skill files. Paste this into any scheduler that can start a Claude session.

---

Write 3 ready-to-post Twitter/X posts, in the user's personal voice, about genuinely interesting things happening right now in AI, startups, tech, and the creator/marketing world. This runs twice a day (around 8:50am and 4:50pm IST); the user posts them by hand at the times you suggest.

SETUP, in this order
1. The repo is checked out at its default branch. Switch to the working branch first: `git fetch origin claude/social-media-marketing-r8rtcp && git checkout claude/social-media-marketing-r8rtcp`
2. Read `.claude/skills/twitter-voice/SKILL.md` and `.claude/skills/twitter-voice/references/examples.md`. They are the authority on voice and shape; follow them. The voice rules further down are a fallback summary in case those files are missing.
3. List `posts/` and read the six most recent files there, if any. Those are the stories sent in recent runs. Do not repeat them. A genuinely new development in an already-covered story is fine, but say that it is a follow-up.
4. Run `TZ=Asia/Kolkata date` so you know the current IST time and whether this is the morning or evening run.

STEP 1 — FIND THE MATERIAL
Use WebSearch to find stories published in roughly the last 24 hours (up to 48 if the day is thin). Search several different angles so the posts aren't the same beat: frontier AI labs and model releases; AI safety or security incidents; the indian startup ecosystem; creator economy, social platforms and marketing changes; consumer tech launches. Prefer a story with a surprising, specific, human detail over generic "X raises $Y" news; the test is whether a smart person would stop scrolling. Verify every fact across at least two independent outlets; if you can only find it in one place, drop it. Direct page fetches are often blocked here; search-result summaries are fine when several independent outlets agree.

STEP 2 — THE VOICE (fallback summary of the skill)
everything lowercase, including "i". no hashtags in the body, ever. no emoji unless the post is a joke, then at most one, self-aware only. line breaks are the punctuation: one thought per line, blank line between beats. periods are rare, ideally exactly one, on the final line. no exclamation marks, no title case, no em-dashes. never "excited to announce", "thrilled", "game-changer", "milestone", or rocket emoji. specific real numbers beat vague claims; rupee amounts in indian digit grouping with a (~$X) conversion when the money matters.

STEP 3 — TELL IT AS A STORY (the part that matters most)
Build each post chronologically: set the scene, show what happened, hold the most surprising fact for the last line. A post that opens with its own conclusion has failed; the best ending reframes everything above it. Write for a smart friend who does not work in tech: "sandbox" becomes "a sealed box", "production infrastructure" becomes "their live servers", "zero-day" becomes "a flaw nobody knew about". The user has Twitter Premium, so there is no character limit; let a good story run long when every line earns its place, and never add a summary line at the end.

STEP 4 — SUGGESTED POSTING TIMES
Give each post a suggested posting time in IST. Morning run: spread the three across 10:00am to 2:30pm. Evening run: spread them across 6:30pm to 9:30pm. Keep them at least 90 minutes apart, and put the strongest post in the strongest slot (weekday 10–11am or 8–9pm).

OUTPUT, for each post
- one plain line: `post at <time> IST`
- the post in its own fenced code block, with an @tag line at the end for accounts the story is about (only handles you are sure of; say when one couldn't be verified)
- a second fenced code block with the ready-to-paste first reply: one lowercase line in the same voice plus one or two source links. Links live here, never in the post, because a link in the main post cuts its reach.
- one short line saying what the story is, plus any further sources you verified it against.
No preamble; start with the first post. If you genuinely cannot find three stories worth posting, write fewer and say why; two strong posts beat three padded with stale news.

FINALLY, save and push the log
Write the full output to `posts/<YYYY-MM-DD>-<morning|evening>.md` (IST date), then `git add posts && git commit -m "posts: <date> <slot>" && git push origin claude/social-media-marketing-r8rtcp`. If the push fails, try once more, then move on; the posts in this session are the deliverable, the file is the memory for future runs.

---

## Schedule

Twice a day, 3 posts each, six a day in total:

- 8:50am IST — posts for the 10am–2:30pm window
- 4:50pm IST — posts for the 6:30pm–9:30pm window

In UTC (IST is UTC+5:30) that is a single cron: `20 3,11 * * *`.

Why two runs and not six: most of a post's engagement arrives in its first 15–30
minutes and the algorithm rewards early velocity, so posts should land hours apart
in peak windows, not stacked. And a run every two hours kept finding nothing new,
because nothing breaks in two hours. Two runs eight hours apart each get a real
window of fresh news (overnight US news in the morning, the day's India and Europe
news in the evening).
