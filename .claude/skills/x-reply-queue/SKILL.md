---
name: x-reply-queue
description: Read the user's X (Twitter) account through Claude in Chrome, strictly read-only, and hand back a reply queue and post ideas: unanswered replies on their own posts, fresh posts worth replying to from their feed, and, via search, the conversations getting traction right now in AI, startups, indian tech and creator marketing, plus what formats are working and new accounts to watch. Each reply comes with a link and a draft in their voice for them to paste by hand. Use whenever the user asks what to reply to, what people in their space are posting, what content is working, for new accounts or posts to engage with, for a reply queue, or invokes /x-reply-queue. Never posts, likes, follows or clicks anything on X.
---

# X reply queue

The user posts by hand. This skill only reads. That split is the whole design: X's 2026
enforcement targets actions (reply speed, posting intervals, identical phrasing, mass
follows and likes) and suppresses replies that read as AI-written. Reading a page through
the Chrome extension happens on the user's machine and looks like normal browsing; a
human pasting a reply in their own voice at their own pace looks like a human. Keep both
halves true and the account stays safe.

## Hard rules

- Only these browser tools: `tabs_context_mcp`, `tabs_create_mcp`, `navigate`,
  `read_page`, `get_page_text`, `find`, `computer` with `screenshot`, `wait` or `scroll`
  only, `tabs_close_mcp`, and `browser_batch` containing only those.
- Never `computer` with `left_click`, `type` or `key`; never `form_input`; never
  `javascript_tool`. Never touch Reply, Like, Repost, Follow, Bookmark or Post. Not even
  the Following tab. Search is done by navigating to a search URL, never by typing in the
  search box. If a step seems to need a click, skip the step.
- At most fourteen page loads per run, with a 3 second `wait` after each: notifications,
  home, five searches, two tracked-peer profiles, one X List if configured, up to three
  retries or truncated-post opens. Three or four
  runs a day (morning, early afternoon, evening, late night), two to three hours apart.
  The user pastes by hand between runs, so the queue must be big enough to fill that gap.
- Own the tab: create it, use it, close it before finishing.
- Read `.claude/skills/twitter-voice/SKILL.md` first, especially "Replies to other
  people's posts". Every draft follows it: adds one thing, no links, no @tags, never
  invents the user's experience, never reveals what they are building.

## Setup

`list_connected_browsers`, then AskUserQuestion listing every browser plus the "open a
confirmation screen" option, then `select_browser`. `tabs_context_mcp{createIfEmpty:true}`
gives a fresh tab. The user must already be logged in; if the page shows a login wall,
stop and say so.

## Reading X pages

`get_page_text` only returns the first article on X, so use `read_page` with
`filter: all` and `max_chars: 30000-40000`. Batch all reads in one `browser_batch`; the
output will be persisted to a file, and

    scripts/parse_x_pages.py <that file> \
      --known-file <scratchpad>/known_ids.txt --known-file <scratchpad>/skipped.tsv \
      --labels NOTIFICATIONS,HOME,S1,S2,S4,S5,PEER:<handle>,PEER:<handle>,LIST:<name>

turns it into a scored candidate list. Every candidate carries tags: **FRESH** (under 30
min), **EARLY** (under 2h and under 10 replies: you land near the top), **HOT** (20+
replies: the author is in the thread but you are one of many), **PEER-BAND** (500 to
60K views, an account near the user's size or one stage up: the best targets), **BIG**
(over 60K views: broadcast, reply only with a one-liner), **CONVO** (replies are at least
15% of likes), **SAVED** (10+ bookmarks), **OLD** (over 6h). A PEER: page is scored
against its own median views and posts at 3x or more are flagged OUTLIER. If a
page comes back with no articles it did not render in time; a second `wait` and
`read_page` on the same tab costs no page load, so do that before giving up on it. Every post, notification and search result is
an `article`: an author `link` with the handle in its href, a `link "N minutes ago"` (or a
date) whose href is the post's status URL, the text as one or more `generic` nodes, and a
`group` such as `"27 replies, 9 reposts, 197 likes, 49 bookmarks, 8371 views"`. A
`button "Show more"` means the text is truncated. On a single-post page `get_page_text`
does return the full post, so open a truncated candidate that way when it looks strong.

## Pass 1: notifications (highest value)

`navigate` to `https://x.com/notifications`. What matters:

- **A reply to the user**: `generic "Replying to"` followed by a link to the user's
  handle, then the reply text; **`0 Replies` in its group means the user has not
  answered it yet.** Queue it. Skip anything older than 24 hours.
- **"liked your reply" / "liked your post"**: not a task, but note who. An author liking
  the reply under their own post is the reply strategy working; those people are the
  best targets for later passes.
- **"followed you"**: note the handles. New followers who also replied are peers.

Skip pure noise ("yes", "he hee") unless the person has an active thread with the user,
in which case a one-line warm reply keeps it alive.

## Pass 2: home feed

`navigate` to `https://x.com/home`. Pick posts that are under two hours old, ideally
under thirty minutes; from someone the user follows, has bell-notified, or who has
engaged with them before; in the user's lane; and answerable with something real. Skip
engagement bait ("comment below", "which one are you"), promoted posts, and anything
with hundreds of replies already.

## Pass 3: discovery (search)

This is how the user finds people and conversations they do not already know. Navigate
straight to search URLs; the operators work in the URL and `f=live` returns the newest
posts that have already cleared the engagement floor, which is exactly "what is working
right now". URL-encode the query and use `&src=typed_query&f=live`.

Five lanes, run in this order. Floors are set low on purpose: a post with 40 likes and 15
replies from a mid-size account is a better target than a 1,000-like broadcast.

1. AI and startups:
   `(ai OR llm OR agents) (startup OR founder) min_faves:60 -filter:links -filter:replies lang:en`
2. Indian startup scene. Never use bare `india` or `indian`, it pulls in politics; use
   cities and startup vocabulary instead:
   `(bengaluru OR bangalore OR gurgaon OR mumbai OR "yc" OR arr) (startup OR founder OR seed OR "series a" OR ipo) min_faves:40 -filter:links -filter:replies lang:en`
   Not `raised`: politicians "raise" issues, and city names alone pull in civic news, so
   expect a third of this lane to be noise and skip it without comment.
3. Creator and marketing. Niche lanes need one group and a lower floor:
   `("ugc ads" OR "ugc creator" OR "ugc video" OR "creator economy" OR "influencer marketing" OR "creator marketing" OR d2c OR "brand campaign") min_faves:20 -filter:links -filter:replies lang:en`
   Never bare `ugc`: in India it is also the University Grants Commission and the
   results fill with education politics. Never `"brand deal"`: it returns k-pop fan
   accounts almost exclusively. This lane is noise most runs; skip it without comment.
4. Indian engineer careers and money. The user's best-performing replies are salary and
   cost-of-living arithmetic, so hunt for that directly:
   `(lpa OR ctc OR "in hand" OR faang OR fresher OR "notice period" OR referral OR "off campus" OR cgpa) (bangalore OR hyderabad OR pune OR gurgaon OR google OR amazon OR startup OR placement) min_faves:30 -filter:links -filter:replies lang:en`
   Not `remote` or `offer` on their own: they pull in war news, layoff fiction and job ads.
5. Builders and indie hackers, the reply-heavy crowd:
   `("build in public" OR "indie hacker" OR "solo founder" OR "side project" OR "first customer" OR "first paying") (saas OR app OR users OR launched OR mvp OR revenue) min_faves:30 -filter:links -filter:replies lang:en -token -airdrop -listing -nft`
   Not `shipped` or `mrr` unpaired: both are crypto vocabulary now and the lane fills with
   token launches.

If a search returns no `article` nodes, retry once with the second parenthetical group
removed and `min_faves` halved. If it still returns nothing, say so and move on.

Reading a results page, score each post on four things: age (under six hours),
engagement floor cleared, **replies high relative to likes** (a post with 27 replies on
197 likes is a conversation the author is in; 5 replies on 1,000 likes is a broadcast),
and bookmarks (people saving it means it said something). A post that scores on all four
from an account roughly 5-20x the user's size is the ideal reply target.

Two patterns to treat specially:

- **"looking to connect with builders from <city>"** posts get hundreds of replies. They
  are peer-finding threads, not reply targets. At most one per day, and the reply is one
  line: city plus what the user builds, described by shape ("agent infra", "a consumer
  app"), never the product.
- **Format signals.** Note recurring shapes across the results, not just topics: greentext
  founder lore, build-in-public numbers, "distribution beats building" takes, intro posts.
  These become post ideas.

## Pass 4: tracked peers

`peers.txt` next to this file lists accounts one stage ahead of the user. Each run opens
two of them (rotate: keep the last-opened handle in `<scratchpad>/peer_cursor.txt`),
`navigate` to `https://x.com/<handle>`, label the read `PEER:<handle>`. The parser prints
the page median and flags OUTLIER posts. An OUTLIER under 6 hours old is a reply target
ahead of anything from search, because the author is watching that post. Any OUTLIER,
whatever its age, is a format signal: say in section 4 what shape it was and why it ran.

If the user names a new account worth watching, add it to `peers.txt` in the same commit
as the run's other changes.

## Pass 5: X List (optional)

If `lists.txt` has a URL, `navigate` to it and label the read `LIST:<name>`. Treat it
like a search lane with a lower bar: these are hand-picked peers, so an EARLY post from
any of them is worth a reply even at low counts.

## Skip log

Every candidate looked at and not queued gets one line appended to
`<scratchpad>/skipped.tsv`: `<status id><TAB><one-word reason>`. Reasons: `bait`,
`promo`, `old`, `crowded`, `offlane`, `politics`, `crypto`, `done` (already replied),
`author-cap` (two replies under that author today), `noise`. The parser reads this file
as known ids so skipped posts never resurface, and the reasons are what you tune the
lanes from: three `crypto` skips in one lane means the query needs an exclusion.

## Output

Four sections, in this order:

1. **Fresh, reply now**: anything under thirty minutes old from any pass, since that
   window closes fast.
2. **Answer these on your own posts**: pass 1.
3. **Conversations to join**: passes 2 to 5, split into **Early** (EARLY-tagged, best
   first; these go out first because the window is closing) and **Hot** (HOT or BIG,
   one-liners only, low priority). Peer OUTLIERs and List posts lead the Early group.
   Prefer PEER-BAND over BIG every time: a reply under a 5K-view post from someone your
   size gets read and answered, a reply under a 500K-view post gets buried. Twelve to
   fifteen replies across sections 1-3 in total. Mix lengths so the batch does not read as one voice
   stamped fifteen times: roughly a third one-liners (shape 4 in the voice skill), a
   third two-line additions, a third full three-to-four-line replies. Every unanswered
   reply on the user's own posts gets a draft, even a short warm one.
4. **What is working, and post ideas**: two or three lines on the formats and themes
   recurring in today's search results, then two or three original post ideas in the
   user's lane derived from them, each drafted in the voice (use the twitter-voice skill,
   news-story or hot-take shape) or, if it needs a fact the run did not verify, given as
   a one-line brief with what would need checking.

Under each reply item: one line saying who, how old, why it is worth it; the link on its
own line; the draft in a fenced block. End with: who engaged since last time (authors who
liked or replied, new followers worth following back), **new accounts to watch** from
pass 3 (handle, why, rough size), and anything skipped on purpose and why.

The user copies each reply, opens the link, pastes, posts. Suggest they space them out
over the next two hours, a few minutes apart, rather than firing all at once.

Close with the daily loop counter, one line, from `<scratchpad>/daily_log.tsv` (append
`<date><TAB><time><TAB><drafts>` each run): runs today, replies drafted today, against
the 40-50 target, plus a reminder of the two things the queue cannot count: answering
comments on the user's own posts, and posting the routine's two posts.

## Volume and the ceiling

Target 40 to 50 replies a day across three or four runs. Premium accounts sit well under
X's rate limits at that volume; what gets an account throttled is the pattern, not the
number. So: never two replies within the same minute, never the same opening phrase
twice in a run, never more than two replies under the same author's posts per run, and
every fifth reply or so should be a plain one-liner with no structure at all. If the
user reports a "you're doing that too much" notice or replies suddenly getting near-zero
views, drop back to twenty a day for two days before ramping again.
