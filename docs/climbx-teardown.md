# ClimbX teardown (climbx.so), read-only walkthrough on 2026-09-12

Account: @KrrishSehgal3, Founding plan ($29/mo, 800 AI credits/day, resets 00:00 UTC).
X account is connected via OAuth **with posting permission** ("used for scheduled posts and
media uploads"). Nothing was posted, replied, scheduled, drafted, blocked or keyed during
this walkthrough.

## Product map

| Section | What it is | Backing API |
|---|---|---|
| How to win on X | Daily loop: post (4 slots), Engage (20 replies), reply on X feed, answer own comments. Four guide pages. | `GET /api/growth-plan` |
| Inspiration | Three tabs: 10 AI-drafted posts/day in your voice; outlier posts from tracked creators; random outliers. | `inspiration/daily-posts`, `inspiration/outliers?handles=`, `inspiration/scan?handles=` (6 scans/day), `inspiration/random-outliers?minMultiplier=1.5&recency=30d`, `inspiration/suggestions` |
| Engage | One post at a time, 40 replies + 40 skips per day, posts under 16h. Filters: size (Any/Big/Peers), lane (Any/Early/Hot). Second source: a public X List. | `engage/bootstrap`, `engage/fresh-outliers?size=peers`, `engage/refresh-candidates?size=&lane=`, `engage/post-exists?id=`, `engage/campaign-suggestions` |
| Studio | Composer with engagement prediction (impressions range), "X ranking potential" score from X's published action weights, Post Coach (22 checks against voice rules), thread support, Save / Mark posted / Schedule / Open on X. | `library/*`, `voice` |
| Calendar | Posting schedule with 4 slots/day, pulls what you already posted from X. | `calendar/posts?from=&to=` |
| Analytics | Daily refresh. Format classifier (Story, List, One-liner, A/B choice), niche classifier, avg replies, impressions, engagement rate. Viral posts excluded from averages. Weekly report. | (page-level) |
| Profile | Insights: each post scored vs rolling median of the 20 posts around it ("5.87x median"); auto-derived do-more / do-less rules. Voice: adaptive persona prompt, account tier detection, goal text, 3 niches. Engage persona: products, about you, writing rules. | `voice`, `onboarding` |
| Library | Drafts, scheduled, saved ideas, used ideas. | `library/my-posts`, `library/saved`, `library/used` |
| Settings | Multiple X accounts (3), delegates (agency login), API keys (read-only or read-write, 5 publishes/day), MCP at `https://climbx.so/mcp` (OAuth 2.1 or Bearer key). | `me/billing`, `credits`, `me/x-connection`, `account/delegates` |
| Ideas | Public roadmap with votes. "Marketing mode for Engage" (18 votes) is next: replies that mention your product. | |

Tracking: `POST /api/product-events` on every screen; Umami-style analytics script at `/3d023b02b6a78da3/script.js`.

## How Engage actually works

1. Your 3 niches (Entrepreneurship & Startups, Software & Dev, Build in Public) expand into
   search topics: the niche names plus AI-suggested keywords (startup execution, product
   roadmap, software startup, founder updates, ai product, user feedback). You can star up
   to 3 topics so they always show, add your own, or add "don't show" topics.
2. It searches X server-side for posts under 16h that clear an engagement floor relative
   to the author's size ("fresh outliers"), tagged with which topic found them.
3. Size filter: Peers = accounts near yours, Big = large accounts. Lane: Early = few
   replies yet, Hot = already busy. Card shows replies/reposts/likes/views and a "Live
   conversation, N replies" strip.
4. "Reply on X" opens X's own compose intent with your text pre-filled. ClimbX does not
   post the reply itself; you press Post on X. That is why the guide says "ClimbX records
   replies completed through Engage" and why the 40/day counter exists.
5. "Draft with AI" is locked until you have written some replies yourself ("Reply in your
   own words first so we can learn your voice"). Skip has a "with a reason" dropdown; both
   feed the ranking.
6. "Use idea" turns the post into a Studio draft. "Block" hides the author in ClimbX only.
7. `post-exists?id=` is called before showing a card, so deleted posts are dropped.

## How Inspiration works

- Tracked creators (currently @DanielSmidstrup, @sflorimm, @TTrimoreau). Each creator's
  posts are scored as a multiple of that creator's own baseline; "outliers" are 1.5x+,
  "bangers" 3x+. Six scans a day.
- The guide's rule: track people one stage ahead (5K-20K followers), not huge accounts.
- Daily posts: 10 drafts generated at midnight UTC from your goal text and voice prompt.
  Today's ten are all variations on "build in public without revealing details", i.e. the
  goal text was paraphrased ten times. Regenerating costs 300 credits.

## What is worth stealing for our own setup

- **Peers filter.** Engage's best default is accounts near your size; our lanes lean big.
  Add a size read (author follower count from the profile hover is not available in
  read_page, so use views-to-likes ratio as a proxy) and prefer 2-20x.
- **Early vs Hot lanes.** We already score replies-to-likes; make it an explicit toggle
  in the queue output: "early" (under 10 replies, under 2h) gets listed first.
- **Outlier multiple against the author's own median.** Their insights compare a post to
  the author's 20 surrounding posts. Add to the x-reply-queue's "what is working": open
  2-3 tracked peer profiles and flag posts running 3x above that profile's typical views.
- **Skip reasons as training data.** We have known_ids but no reason log. Add a one-word
  reason per skipped candidate so the lanes can be tuned from evidence.
- **X Lists as a source.** A public list of 20-30 peers is a cleaner feed than search.
  Create one on X by hand and add `https://x.com/i/lists/<id>` as a pass in the queue.
- **Daily loop counter.** 4 posts, 20 replies, own-comments pass, follow-up pass. Ours is
  the same loop; theirs puts the numbers on a dashboard.
- **Post Coach checks and ranking score.** A draft-time checklist against the voice rules
  is cheap to add to the twitter-voice skill's Process section.

## What ours does better

- Voice. Their drafts are generic thought-leader prose ("A product can be public in
  direction and private in detail"). None of the ten would pass the twitter-voice skill.
- Safety. Ours never holds an X token. ClimbX holds a posting-scoped OAuth grant. Its
  Schedule and Post buttons publish through the API, which is the exact footprint X's
  2026 enforcement looks at, and its own settings page warns links are blocked.
- Search precision. Their topics are keyword bags; ours are tuned operator queries with
  exclusions learned from noise.
- Reply quality control. Ours drafts in two registers, hedges opinions, never reveals the
  product. Theirs has a "marketing mode" on the roadmap to mention your product in replies.

## Things to decide

- Whether to keep the posting permission on the X connection. Analytics, Inspiration and
  Engage all work with read scope. Revoking write (Settings > Reconnect X, or X > Settings >
  Connected apps) removes the risk of anything ever being published through it.
- Whether to add the three tracked creators, or better ones at the 5K-20K stage in the
  India AI/startup lane, to our own watch list.
