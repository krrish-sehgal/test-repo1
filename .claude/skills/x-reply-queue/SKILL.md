---
name: x-reply-queue
description: Read the user's X (Twitter) account through Claude in Chrome, strictly read-only, and hand back a reply queue: unanswered replies on their own posts plus fresh posts worth replying to, each with a link and a drafted reply in their voice for them to paste by hand. Use whenever the user asks what to reply to, to check their notifications or feed, for a reply queue, for posts to engage with, or invokes /x-reply-queue. Never posts, likes, follows or clicks anything on X.
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
  the Following tab. If a step seems to need a click, skip the step.
- At most six page loads per run, with a 3 second `wait` after each. Two runs a day,
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

## Pass 1: notifications (highest value)

`navigate` to `https://x.com/notifications`, wait, `read_page` with `filter: all` and
`max_chars: 40000`. `get_page_text` only returns the first article on X, so use the tree.

Each notification is an `article`. The ones that matter:

- **A reply to the user**: contains `generic "Replying to"` followed by a link to the
  user's handle, a `generic` with the reply text, a `link "N hours ago"` whose href is the
  reply's own status URL, and a `group` like `"1 reply, 16 views"`. **`0 Replies` means
  the user has not answered it yet.** Queue it. Skip anything older than 24 hours.
- **"liked your reply" / "liked your post"**: not a task, but note who. An author liking
  the reply under their own post is the reply strategy working; those people are the
  best targets for the next pass.
- **"followed you"**: note the handles. New followers who also replied are relationship
  targets.

Skip pure noise ("yes", "he hee") unless the person is someone the user has an active
thread with, in which case a one-line warm reply keeps it alive.

## Pass 2: home feed

`navigate` to `https://x.com/home`, wait, `read_page` the same way. Each post is an
`article` with the author link, a `link "N minutes ago"` whose href is the post URL, the
text in a `generic`, and a `group` with counts. Pick posts that are:

- fresh: under two hours, ideally under thirty minutes (early replies inherit the post's
  reach)
- from someone the user follows, has bell-notified, or who has engaged with them before
- in the user's lane: AI, startups, indian tech, creator and marketing work
- answerable with something real: a number, a sharper framing, a fair disagreement

Skip: engagement bait ("comment below", "which one are you"), promoted posts, anything
with hundreds of replies already (the reply will be buried), and posts whose text is
truncated unless it looks strong enough to open.

If a candidate is truncated (`button "Show more"`), `navigate` to its status URL and
`get_page_text`, which works on a single-post page. Budget two of these per run.

## Output

Two sections. Under each item: one line saying who, how old, and why it is worth it;
the link on its own line; then the drafted reply in a fenced block. Lead with anything
under thirty minutes old, since that window closes fast. Five to eight items total; more
than that and the user will not post them, and a queue they skip teaches nothing.

End with two lines: who engaged since last time (authors who liked or replied, new
followers worth following back), and anything skipped on purpose and why.

The user copies each reply, opens the link, pastes, posts. Suggest they space them out
over the next hour or two rather than firing all at once.
