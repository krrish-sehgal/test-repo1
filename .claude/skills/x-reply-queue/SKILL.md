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
- At most nine page loads per run, with a 3 second `wait` after each: notifications, home,
  three searches, up to two retries or truncated-post opens, spare. Two runs a day,
  morning and evening, matching the posting routine.
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
`filter: all` and `max_chars: 30000-40000`. Every post, notification and search result is
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

Three lanes, run in this order:

1. AI and startups:
   `(ai OR llm OR agents) (startup OR founder) min_faves:100 -filter:links -filter:replies lang:en`
2. Indian startup scene. Never use bare `india` or `indian`, it pulls in politics; use
   cities and startup vocabulary instead:
   `(bengaluru OR bangalore OR gurgaon OR mumbai OR "yc" OR arr) (startup OR founder OR seed OR "series a" OR ipo) min_faves:40 -filter:links -filter:replies lang:en`
   Not `raised`: politicians "raise" issues, and city names alone pull in civic news, so
   expect a third of this lane to be noise and skip it without comment.
3. Creator and marketing. Niche lanes need one group and a lower floor:
   `("ugc ads" OR "ugc creator" OR "ugc video" OR "creator economy" OR "influencer marketing" OR "brand deal" OR d2c) min_faves:20 -filter:links -filter:replies lang:en`
   Never bare `ugc`: in India it is also the University Grants Commission and the
   results fill with education politics.

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

## Output

Four sections, in this order:

1. **Fresh, reply now**: anything under thirty minutes old from any pass, since that
   window closes fast.
2. **Answer these on your own posts**: pass 1.
3. **Conversations to join**: passes 2 and 3, best first. Five to eight replies across
   sections 1-3 in total; more than that and the user will not post them.
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
over the next hour or two rather than firing all at once.
