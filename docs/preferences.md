# Kevin's preferences: the ledger behind the Affinity model (compiled 2026-10-09)

Compiled 2026-10-09 from:
- kevin_msgs.txt: 240 messages, 2026-09-28 to 2026-10-09. 159 were typed by Kevin; the rest are subagent reports and image-only messages.
- Five queued messages that kevin_msgs.txt is missing, recovered from the session transcript and marked [queued].
- The assistant turns just before Kevin's short replies, read from the session transcript, to work out what "B", "1 and 2", "the word" and similar replies answered.
- docs/supporter-profile.md, docs/affinity.md, CLAUDE.md, research/REVIEW.md, players/feedback.json, players/observations.json, research/cascadia/*, players/SCORING_BRIEF.md.
- The raw quiz answers in scripts/affinity/quiz4 to quiz12, which I decoded myself.

Anything older than 2026-09-28 is known only from the docs: the original 51-question interview ("the Principled Romantic") and quiz rounds 2 and 3. Their wording is the docs' summary, not Kevin's own.

Conventions:
- **[CURRENT]** marks the rule in force. **[SUPERSEDED]** marks an earlier version.
- "Gut fit" means the correlation between the model and Kevin's 0-10 gut ratings of 26 anonymous clubs (13 from quiz round 4, 13 from round 5).
- Current numbers come from data/suite_data.json and players/ratings.json as of 2026-10-09.

---

## A. Goals and principles in Kevin's own words

Quotes are exact, typos included, with UTC dates.

### Purpose and method
- 2026-09-29: "I enjoy digging into the personality test adjacent methods. Develop another refining series of questions. Research blinding techniques where the questions may seem general or unrelated to the topic at hand, but correlate with it, as a way to reduce response bias. Go nuts, ask whatever off the wall things you can think of if you can correlate it with the data. I'm big on data, so let's do at least a few dozen more questions, pull it all into the model and refine ratings and balances. You have carte blanche."
- 2026-09-29: "The anonymous clubs thing is a bit of a misnomer because at least half the time I can discern which club it is from the context clues."
- 2026-10-02: "I think the next true iteration of this is a true heart-over-head accounting. Going forward, when I watch a match neutrally, I will try to remember to report back which team I found myself pulling for and which players (or coaches) I enjoyed or did not enjoy watching."
- 2026-10-02: "yes, and also remove the affinity scores from the match cards, so it doesn't influence me. and the pickem projections. keep those housed in their own silos. and then ship it"
- 2026-10-06: "Let’s do an offshoot of the affinity ratings and apply it to players. We’ve done tons of research and surveys to identify my preferences and archetype already so use that as the basis of the rating. I’m giving you latitude to determine the best algorithm to use."
- 2026-10-06: "I'm not good at the whole budget thing. I think a different method would be better."
- 2026-10-06: "Needs more refinement, I think. I'm guessing that, being a newer fan, name recognition is pulling a bigger influence here than my stated preferences, as the majority of the players I'm familiar with are either major stars or those that play for the teams I've been following."
- 2026-10-06: "I don't know enough about them to do this. That's why I wanted independent research." This declined the factor-score corrections page.
- 2026-10-06: "let's do more this or that by name, but try to limit the confounding factors for each. i'm thinking like choosing between two current liverpool players, or between two global superstars without connections to any of my teams, or two otherwise similar players with different styles, kind of like the blind matchups but try to limit the variables to 1 or 2 per choice, with the option to pass if I feel I don't know enough about one or both players to make an honest assessment (which should be counted as part of the analysis, too)."
- 2026-10-06: "let's put these rankings into words and I'll offer a response if I disagree. sell me on why each of the top 10 active men should be amongst my personal top 10. lets go one at a time starting with number 10. use my responses to tune the model."
- 2026-10-07: "I want a full integration of the player and club sides with bilateral influence and a full reprocessing of both models (or one unified model?) run it and ship it."
- 2026-10-09 (the rebuild brief): "i feel like weve doner a lot of adding and changing. lets do a full audit, backtest, and recalculate with a more cohesive algortihm. review all of our conversations and quiz results to build one monolithic model across all teams, nations, players, leagues etc. take your time. do your research. make it good and let's get rid of this piecemeal system that has grown from scattered ideas over timne"

### Knowledge base (do not judge by familiarity)
- 2026-10-06 [queued]: "Keep in mind, for the "don't know" answers that I've only seriously been following the sport for less than a year. I've heard of many of those mentioned, but didn't watch them in their day, so I feel it unfair to assess them through that lens"
- 2026-10-06: "A big factor in all of this is that I really only started following the sport closely with the 2026 world cup, so my knowledge base is the past 4-6 months plus what I've gained by osmosis over that time. I've read "How to Watch Soccer" by Ruud Gullit and am currently in the early pages of "The Soccer 100" to try to understand some more historical context."
- 2026-10-06: "Big challenge with the women's list: I've not watched any women's football outside of NWSL, and mostly only Thorns matches, so my knowledge beyond that and casual observance of past World Cups is about the extent of my women's game background."

### Clubs: what a club should be
- 2026-09-28 (track record): "Include an overarching performance factor. This does not need to be one of the rated factors, but maybe an overall coefficient that evaluates and rates consistently successful clubs better. This does not mean domination, but rather consistent success over time, and maintaining positioning in or near the top tiers (or the tier analyzed for lower tier leagues) over time. It should also contain a weighting factor for recency. i.e. I'm not interested in a team that won a trophy in 1965, but now spends 30+ matchdays a year staring at the relegation line."
- 2026-09-29: "My preference for global-scale teams is tier 1, mid-table or higher regularly, with occasional runs at championships, cups, and champions league type competitions. My interest in lower tier football is primarily regional (Sacramento, Portland, etc)"
- 2026-09-29, **the bandwidth explanation**: "The issue is bandwidth. To properly follow a club, I need at least some context of the competition. This is why I’ve basically limited myself to LFC, BVB, Portland Timbers/Thorns, and SRFC. Because that alone requires familiarity with premier league, Bundesliga, champions league, mls, NWSL, and USL. plus any associated cups they compete in like carabao, DFb pokal, open cup, leagues cup, etc."
- 2026-09-28 (association): "Something else, I've been thinking about is a sort of "association factor." The way that multi-club ownership groups get a demerit, there should be some sort of association/alignment in other ways, e.g. Portland Timbers/Thorns shared supporters, or Liverpool, Dortmund, Celtic all having ties to YNWA. IDK if it's a +/- type thing or just a "pull" or "influence" adjustment in the rankings"
- 2026-09-28 (location and big-4): "This won't matter outside the US clubs, but geographic proximity and other big-4 rivalries matter as well. Take my big-4 supported teams (Sacramento Kings, San Francisco Giants, San Francisco 49ers, San Jose Sharks) and their rivals into account as well as my location in Sacramento. There are also some sneaky links between big-4 teams in the US and many global squads. Those can be considered, too." Followed by "not just distance, but rivalry, too".
- 2026-09-29 (Cascadia): "I need to rectify something, once and for all. Let's do a deep dive into Portland versus Seattle. I've followed Timbers for about half a season, and having the Sounders rated above them, obviously is giving mixed feelings and has me questioning it. That said, half a season is not a lifetime of support. If the Sounders truly do fit my profile and preferences better, I'd be open to reconsidering. Let's go through a process like we've done in the past, solely to determine this conflict, though the findings can and should guide the ratings engine for the the rest of the affinity system, should that be useful."
- 2026-10-02 [queued]: "(as long as timbers stay above sounders on merit lol)". This was the condition attached to removing the rival penalties.
- 2026-09-30 (squad interplay): "we should factor in interplay between club squads and international squads, either as part of the team component or separately. ... 1. Liverpool currently has 4 key players from the Netherlands (van Dijk [captain], Gako, Gravenberch, Frimpong). Since Liverpool is a highly rated cub on my affinity index, this should elevate the Netherlands as well. 2. Athletic Club, famously, only fields players with Basque/Spanish roots. Teams that field larger shares of domestic players should also get a boost. I would maybe look at this similarly to the track record factor where it's based on the past 10 seasons with a decay factor. And I'd lean towards it maybe bumping the team rating up or down 1-2 points, rather than a multiplicative factor."
- 2026-10-02: "go ahead keep USL in. it's de facto top flight anyway without pro/rel in the US"
- 2026-10-02: "ownership issues should be folded into the ownership category. re weight if needed to improve gut fit"
- 2026-10-06 (Dortmund): "Honestly, I'm feeling a little pull away from Dortmund through this process. I was drawn to them via the same things that drew me to Liverpool, but the natural affinity hasn't materialized the same way."
- 2026-10-06: "1. let's go half-weight for now 2. I wouldn't lower it directly, but assess it objectively as you would any other team that I hadn't identified as a favorite from the outset"
- 2026-10-07: "Apply the dortmund change to all clubs. Base it solely on affinity rating, not my stated favorites"
- 2026-10-09, **plastic fans**: "i want one more thing across all the rankings. americans often get acccused of being "plastic" fans account for that however you see fit. I don't want that label"
- 2026-10-08 [queued]: "The irony that the English team I've chosen to follow is from like the only area of England not covered by my heritage lol"
- 2026-09-29 (family questionnaire): "...allow her to establish some clubs to back should she choose (they don't have to be the same as mine!)". 2026-09-30: "don't need to update the family app. that was just a one time thing. consider it deprecated."

### Players: who should top the lists
- 2026-10-07, **the role-model goal**: "Basically, at the end of the day, these lists should be topped by players that I'd like my son to look up to. Players that are humble, unselfish, play the game the right way, respect their opponents and the officials, make time for fans, stand up and speak out for what is right, avoid legal trouble and controversy, live a respectable life, on and off the pitch, all while delivering performances on the pitch worthy of the highlight reels and the history books."
- 2026-10-06, **penalty cap**: "no cap. shitheads need not apply."
- 2026-10-06 (loyalty): "he belongs, my one push is on loyalty. it seems that it just took a bit to find the right fit. i'd expect young players to move about a bit early on as they establish themselves. expecting a 13-year-old academy signing to give 20+ years to one club is noble, but not realistic"
- 2026-10-06 (money leagues): "he belongs, but I'm not a fan of the Saudi league in general. Top players jumping to a 3rd-tier league just because its backers have more oil money than they know what to do with is...bleh. I want guys that want to compete at the highest level, not collect a fat paycheck against minor leaguers"
- 2026-10-06 (late-career moves): "seems about right. i won't hold a sunset move to Galaxy against him. lot's of folks move to so-cal in their golden years"
- 2026-10-06 (Zidane): "Didn't bruv insult his family or something like that? I feel like it was out of character and heat of the moment, not fitting a pattern." When the record showed a pattern, he answered "leave it as is".
- 2026-10-07 (media): "I would say that pushing a transfer through the media is far worse than having discussions behind closed doors. One is business, the other is manipulation."
- 2026-10-07 (position): "Do the same overall. It matters very little."
- 2026-10-06 (match observation): "when I was watching an early-season AVFC match, I couldn't help but notice how possessions ended, more times than not, when the ball got to George Hemmings' feet. Not that Hemmings is an elite player, but it was a frustrating pattern to watch as someone that was pulling for Villa at the time"

### Working agreements (CLAUDE.md, learned over earlier sessions)
- Terminology: "Affinity" (not HAI), "Matches" (not "Games"), "Affinity pick", "Match of the week".
- Never overwrite results he entered.
- Plain, short replies.
- Offer a pass/"don't know" option in quizzes. Lean on research for history.
- Excel trackers are deprecated.
- "Ship it" means take it live without asking: commit, push, open the PR and merge. 2026-09-28 [queued]: "for future reference, across all code projects, if I say "ship it" I want you to do whatever needs to be done to take it live."

---

## B. Rules he decided

Each rule gives its date and source, his words where they exist, and any later change. **[CURRENT]** marks what is in force today.

### B1. Factor structure and weights (clubs and nations)

**Factors.**
- Original interview: five factors, each scored 0-10: Values, Supporter culture, History & identity, Ownership, and Style of play.
- 2026-09-28, round 3: Style was replaced by **Team**, defined as how they play plus team culture.
- [CURRENT] The factors are Values, Culture, History, Ownership and Team.

**Weights, Culture / Values / History / Ownership / Team.**
- Original: 28 / 22 / 18 / 14 / 8.
- Round 2 proposal (2026-09-28): 26 / 28 / 16 / 12 / 8. Kevin confirmed it in REVIEW.md. His words in the profile: "Values is too low."
- Round 3 (2026-09-28): 26 / 26 / 14 / 12 / 12. Kevin's first quiz answer had been 24 / 26 / 14 / 10 / 16.
- Round 4 (2026-09-29): 20 / 27 / 17 / 10 / 16.
- Round 5 (2026-09-29): **[CURRENT] Values 26, Culture 23, History 16, Team 15, Ownership 10.** This averaged round 4 with his own 100-point budget split, which was Culture 25, Values 25, History 15, Team 15, Ownership 10, plus 10 for winning.

**Stated trade-offs** (round 2, 2026-09-28):
- Culture beats Ownership: an elite atmosphere under a PE fund beats a fan-owned club with a quiet crowd.
- Values beats History: strong community values beat a big history with poor conduct.

**League-agnostic** (round 2) [CURRENT]: the same club gets the same score in any league. This holds separately within the men's game and within the women's game.

**Sub-weights inside the factors** (round 5, 2026-09-29):
- Culture: ground 50, loud section 25, loyal through bad years 15, away following 10.
- Values: community 20, women's team 20, causes 20, academy 15, affordable tickets 15, fan voice 10.
- Team: player-fan bond 40, stable core squad 25, icon or defining coach 20, pressing 15.

He asked to "run the re-rate with the new sub-weights". The result did not improve the gut fit (0.746 against 0.747) and the research behind it was thin. Kevin: "Scrap it" (2026-09-29). [CURRENT] The sub-weights are recorded but not applied; they survive only as guidance in the research brief.

**Precision.**
- 2026-09-30: "Let's do a full re-run and take all the other ratings to the tenths place." [CURRENT] Culture, Values, History and Ownership carry one decimal. Team is a whole-number base plus the interplay bump.
- Display, 2026-09-30: "component ratings should always read to the tenth, unless they are 0 or 10, even if it lands on a whole number". [queued] "and do the same for the overall, but only exclude 0 and 100". [CURRENT]

**Sixth factor and Connection** (2026-10-02, review of the add-ons):
- No sixth factor. A weighted Connection factor fitted worse.
- [CURRENT] Connection is a display group of adjustments.

**Cap.** 2026-09-28: "go with ±20% and cap at 100". [CURRENT] Club Affinity is capped at 100.

### B2. Culture
- **[CURRENT]** Main signal is atmosphere: noise, singing, choreography, away following. A small, loud, loyal crowd beats a big, quiet one (round 2).
- **[CURRENT]** Anchor Culture on evidence such as attendance and atmosphere, not reputation (the USL recalibration).
- **Ultra groups** are judged group by group (round 2).
- **Stadium rule:**
  - [CURRENT] A historic ground beats an NFL stadium.
  - A recent move made for convenience, or sharing an NFL/CFL stadium, is -1 Culture. A ground that has been home for decades counts nothing against the club.
  - A new stadium in the same city is a temporary drop of about -1 for roughly 5 seasons (round 2).
  - Cascadia r1 (2026-09-29): sharing an NFL stadium should count "A little". [CURRENT]
- **Loyalty through bad years** counts. Round 5's quick sort pulled hardest for loyalty: "Sold out for 40 straight years" and "Relegated, and crowds grew".
- **A modern ground with great sightlines is fine.** In round 5 he would take the new ballpark with perfect views. Round 6 contradicts this; see D.

### B3. Values
- **Political or social identity** (round 2) [CURRENT]:
  - Raises Values: anti-fascist or left-wing identity; regional identity (Basque, Catalan, Scottish and so on).
  - Lowers Values: sectarian rivalry; nationalist or right-wing identity; owner-driven political messaging.
  - Community or religious roots have no effect either way.
- **Raises Values** (round 2) [CURRENT]: community work, investment in a women's team, a local academy pathway, a formal fan voice (board seats, golden share, fan advisory board).
- **Ticket prices** are "one factor among several" (round 2).
- **Sponsors:**
  - Sports betting counts against (original rule). Arms makers count against: Dortmund and Rheinmetall, -1 Values (original).
  - Firms owned by authoritarian states count against (round 2).
  - Crypto/NFT and fossil fuels have no effect (round 2). Note: player round 11 counts crypto against players; see D.
  - Casino money behind an owner is fine. Sacramento Republic's tribal-casino ownership is fine (original).
  - Casino-brand sponsors without a sportsbook count half (REVIEW, 2026-09-28): Reading V5, Leicester V5, QPR stays 5. Seattle's tribal casino has no effect.
  - A casino with a sportsbook inside counts "Partly" (Cascadia r3). [CURRENT] Values -1 (rules re-rate R4).
  - An owner who owns the betting sponsor counts worse than a normal betting sponsor: Stoke V3 (REVIEW).
  - Sponsors from Partly Free states count in full (Cardiff V4). State firms or tourism boards of any non-Free country count in full (REVIEW).
  - Signed future sponsor deals count now (REVIEW).
- **Brighton** (round 4, 2026-09-29): the owner's fortune from sports betting costs -3. It was later folded into Values (2026-10-02).
- **Fan violence:**
  - Round 2: same scale as tolerated racism, up to -30.
  - Round 4: doubled, because Galatasaray's gut rating was far below the model.
  - Round 5: re-scaled to 1.5x the pre-round-4 values. [CURRENT]
- **Players** (round 3, 2026-09-28) [CURRENT]:
  - Player conduct counts, and the club's response counts on top.
  - A club standing by a player facing credible abuse or violence allegations is a strong negative (Values -2 or more), but not after an acquittal.
  - Player welfare applies to every club, men's included.
  - One-club players and academy graduates are a small raise (+1 unless the academy is already credited).
- **Cascadia r6** (2026-09-29): a women's team majority-owned by private equity but run by the club is "Better" than having no women's team.
- **Cascadia r5:** formal fan power, such as a vote on the GM, matters "Some".
- **Southampton Spygate** stays in both Values and the adjustment (REVIEW). This is a deliberate double count.

### B4. History
- **Significance first** (round 2) [CURRENT]: famous moments, influence on the game, place in football culture.
- **A club liquidated and re-formed by its fans** keeps all of the old club's history (round 2).
- **Clubs in newer leagues** get credit for the clubs, leagues or amateur roots they grew out of (round 2).
- **Icons** count in Team only while at the club. After that they pass into History (round 3).
- **Underdog status** gets no extra credit beyond History, for example famous runs (round 3, round 4 "mild, no change").
- **Player icons feed club History** (2026-10-07). [CURRENT] The best 5 icons with 4+ seasons move History by up to ±1 (players_link.py).

### B5. Ownership
- **Fan or member ownership is the ideal** (round 2). Conduct counts more than structure: an outside owner who runs the club well scores on that.
- **Specific calls** (original):
  - Timbers ownership 5, "judge on today". It became 6 after Cascadia.
  - Sacramento Republic ownership 8.
- **State-backed ownership:**
  - -25 (original) [CURRENT].
  - Satellites of a state-controlled group pay half, -12 (Troyes, NYCFC), plus multi-club. The owner club keeps -25 (REVIEW, 2026-09-28) [CURRENT].
- **Multi-club** (original -4 to -8):
  - Only the secondary clubs pay; the flagship gets 0. Nagle's Huddersfield and Republic count as neither, since that is not a network (REVIEW).
  - Round 5: x0.75.
  - 2026-10-02: folded into Ownership. [CURRENT]
- **Private equity:**
  - Round 2: a strong negative, on the scale of multi-club.
  - REVIEW: only real PE funds count, not US sports investment groups. This dropped PE for Liverpool, Leeds, Villa, Charlton and Walsall.
  - PE and multi-club for the same owner add up.
  - Round 5: x1.5. [CURRENT] PE stays a hard line, about -4 to -12.
- **Leveraged buyouts:**
  - Round 2: serious, "just short of state backing (-25)".
  - REVIEW: smaller, Man Utd -10 and Burnley -8.
  - Round 5: x1.2. [CURRENT] About -10 to -12.
- **Overspending** beyond natural income counts against the club (round 2). Man City overspend -6 applied (REVIEW). 2026-10-02: folded into Ownership. [CURRENT]
- **Penalties from a previous owner are dropped**, for example Everton's overspend (REVIEW). [CURRENT]
- **Owner misconduct** that had consequences and was not repeated counts "About half" (Cascadia r2). [CURRENT] Rules re-rate R1 gives +1 back.
- **Announced plans** count now, fully (Cascadia r4 "Yes, fully"). [CURRENT] R2: a stadium move gives +1 for a welcomed upgrade and -1 if opposed or worse. A sale gives -1 to PE, multi-club or an opposed owner, and +1 to fans or a respected local.
- **Staff and owner conduct toward players** (welfare, pay, exile groups) counts in Ownership (round 3).
- **"ownership issues should be folded into the ownership category. re weight if needed to improve gut fit"** (2026-10-02):
  - A true fold made the gut fit worse at every weight tried (0.712 to 0.752 against 0.776). Man City, Chelsea and Man Utd would have gained 17 to 25 points.
  - The assistant offered a card-level grouping instead. Kevin never answered (see E).
  - [CURRENT] State, PE and LBO stay separate hard-line adjustments.

### B6. Team
- **Round 3 definition** (2026-09-28): how they play (intensity, pressing, running for each other), the player-fan bond, a stable and humble squad, current icons, and a defining long-serving coach.
  - Fight and a clean dressing room were not picked as signals.
  - Time window: the last 3 seasons.
  - Women's clubs also count player activism (equal pay, welfare).
- **Cascadia r7:** a coach who has been there 10 years matters more than the style of play. [CURRENT] R3: a coach of 5+ seasons gives Team +1. Three or more permanent coaches in 3 seasons gives Team -1.
- **Style of play:** round 2 rewarded intensity (pressing, energy, running for each other). Round 5 and 6 rank pressing low (15 of 100 within Team). [CURRENT] Pressing no longer leads.
- **Squad interplay, homegrown share** (2026-09-30, Kevin's idea, "bumping the team rating up or down 1-2 points, rather than a multiplicative factor"): [CURRENT] up to ±2 on Team, with a 4-season half-life.
- **Player influence** (2026-10-07) [CURRENT]: the best 5 current players move Team by up to ±1.5.

### B7. Hard lines and penalties (clubs and nations)
- **Tolerated racism** or far-right fan groups: up to -30 (Lazio -30).
- **Nations:**
  - Repeated UEFA discrimination sanctions: -8 to -15.
  - Authoritarian federation: -10 (original). Replaced by the government record rule below.
- **Super League signatories:**
  - Original: -2 if they withdrew, -3 if they withdrew late, -5 if still backing.
  - Round 5: x1.5. [CURRENT]
- **Franchise or relocation:**
  - -10 for RB Leipzig and NC Courage (REVIEW). MK Dons -15.
  - Round 5: x0.4, giving MK Dons -6, RB Leipzig -4, NC Courage -4.
  - 2026-10-02: folded into History. [CURRENT]
- **Severity order** (round 5 best-worst, 2026-09-29) [CURRENT basis for scaling]:
  1. racism
  2. authoritarian-state owner
  3. private equity = debt buyout = ultras violence
  4. owner politics = Super League
  5. overspending = betting sponsor = arms sponsor
  6. multi-club feeder
  7. relocation (least bad)
- **No cap on stacked adjustments** (REVIEW, 2026-09-28). [CURRENT]
- **Old wrongs fade** (round 5, decay +0.39; violence 8 years ago cost little, last season's a lot):
  - Proposed rule: incidents older than about 5 years count half unless the behaviour continues.
  - It was in the scrapped sub-weights run and no penalty qualified then. [CURRENT] Not applied.
  - Round 6 e15 picked "Remember" over "Forgive"; see D.
- **Minor penalties fold into factors; hard lines stay** (2026-10-02 add-on review). Kevin approved the package by replying "go ahead keep USL in" to "Want me to go ahead?".
  - [CURRENT] Folded: multi-club and overspend into Ownership; franchise into History; betting owner and other conduct into Values.
  - [CURRENT] Kept as adjustments: racism, state ownership, fan violence, PE, LBO, Super League, government record. Without them the gut fit dropped to 0.560.

### B8. Track record (clubs only)
- **2026-09-28, his request (A):** consistent success, near the top tier (or the tier analysed), weighted for recency, no credit for ancient trophies.
- **Range history:**
  - First built at ±10%.
  - Kevin: "go with ±20% and cap at 100" (2026-09-28), so that Dortmund would pass Union Berlin.
  - Round 4: kept at ±20%, half-life 3 → 4 seasons. "Judges a body of work, not the last season."
  - Round 5: ±15%, "which keeps Dortmund above Union Berlin".
- **Reference tier** (2026-09-29, Kevin: "tier 1, mid-table or higher regularly..."; "do both and ship it"): clubs outside North America are judged against the top flight. USL clubs keep their own tier (regional interest). League One and League Two clubs dropped 12-16 points.
- **2026-10-02 add-on review** [CURRENT]:
  - ±5% (k = 0.95 + 0.01 P), top-flight clubs only.
  - "go ahead keep USL in. it's de facto top flight anyway without pro/rel in the US", so the USL Championship counts as top flight.
  - Championship and lower English clubs get no coefficient.
  - Gut fit: 0.723 at ±15% for everyone, 0.776 at ±5% for the top flight, 0.788 with none.
- **Trophies vs steady finishes** (round 5): a single trophy beats five near-top finishes (+0.64), but "a cup last season" was negative and every method ranked winning low.
- **Nations:** no track record.

### B9. Association (club-to-club ties)
- **2026-09-28 [CURRENT]:** "go with two-way, and skip rival pairs", then "go with your recommendation".
  - A club always gains from a partner rated above it, and loses only to partners rated below 50.
  - Strengths: strong 15%, medium 8%, light 4%. Combined link weight capped at 15%; total pull capped at ±5.
  - Low-confidence ties, stadium-only US pairs and kit-heritage ties were dropped, leaving 56 ties.
  - Ownership ties never count here.
- **Rival-pair skip:** this became moot when the rival penalties were removed (2026-10-02). [CURRENT] Sounders and Reign now link.
- **Celtic (YNWA)**, one of Kevin's own examples, is not linked. Celtic exists only as a heritage club since 2026-10-08 and has no link in links.json (see E).

### B10. Location, big-4 teams, rivals
- **Kevin's teams:** Kings, Giants, 49ers, Sharks (2026-09-28).
- **Rivals:**
  - Full weight: Lakers, Dodgers, Seahawks, Rams, Cowboys, LA Kings, Ducks, Golden Knights.
  - Half weight: A's, Raiders, Packers.
  - "count warriors as a half-rival with kings" (2026-09-28). [CURRENT]
- **Distance:**
  - Round 5's "Two hours from Sacramento" pull raised the bonus from +3 to +4.
  - [CURRENT] North American clubs get 4 × (1 − miles/800). Republic is excluded because it has the hometown bonus.
- **Market** [CURRENT]:
  - Bay Area +0.5, which is +1 minus 0.5 for the Warriors.
  - LA -2, Dallas -1, Las Vegas -1.5.
  - Seattle -1 since 2026-10-02, when the rival penalty was removed and the exemption ended.
- **Ownership ties to Kevin's teams:**
  - Kevin's team: ownership +2, minority +1 (Leeds, Huddersfield, Republic, Thorns, Whitecaps, Bay FC, Rangers).
  - Rival: -3 ownership and -1.5 minority at first; round 4 raised them to -5 and -2.5 [CURRENT]; a former owner -1; half for half rivals.
  - Big-4 cap ±4, raised to ±6 in round 4. [CURRENT]
  - Passive fund stakes (Arctos, Sixth Street revenue deals) and ended ties do not count. Chelsea gets 0 since the Clearlake buyout.
- **Football rival penalties:**
  - Round 3 (2026-09-28): Schalke and Bayern (Dortmund's rivals) -5; Seattle Sounders, Seattle Reign and Vancouver (Cascadia) -5; Everton -2 ("friendly derby"). Manchester United and Republic's USL rivals got none.
  - **Removed 2026-10-02:** "and let's remove the explicit rivalry penalties. ship it." with [queued] "(as long as timbers stay above sounders on merit lol)". It shipped once the add-on review put the Timbers back above the Sounders. [CURRENT] No rival penalties. Today: Timbers 80.1 (12th), Sounders 79.0 (16th).
- **Republic link** (round 3): +2 while a former Republic player is a regular at a higher-tier club (now LAFC, Aaron Long). [CURRENT] It moved into the big-4 connection items on 2026-10-02.

### B11. Hometown, heritage, home nation
- **Clubs** (round 2) [CURRENT]: the regional heritage bonus was dropped. Only the hometown club, Sacramento Republic FC, gets +4.
- **Nations, heritage** (round 2): kept as a tiebreaker up to +10.
  - 2026-10-08, after "big update on the heritage side. Ancestry released their annual model update." [CURRENT] 0.4 × Ancestry share, capped at +10. Regions are split across nations, for example Ulster 2/3 Northern Ireland and 1/3 Republic of Ireland.
- **Home nation:**
  - 2026-09-28: the United States +10.
  - 2026-10-09 plastic-fan check: [CURRENT] +20, "twice the largest ancestry bonus".
  - heritage.json's rule text still says +10, which is stale.
- **Heritage clubs** (2026-10-08): "based solely on my DNA heritage shares, rank my top club and nation teams" → "combine with my affinity rankings" → "the word" (that is, research and rate the 15 heritage clubs).
  - [CURRENT] 15 clubs from his Ancestry regions are scored like every other club, with no regional bonus. They show as a separate "Heritage clubs" filter.
  - The combined club ranking that used a region bonus in chat (Portsmouth +5.2 and so on) was a one-off view, not a model rule.
- **US players and clubs visited in person** get no bonus (round 3). For players see B15.

### B12. Nations
- **Government record** (round 2, "counts strongly, on the scale of state-backed club ownership"):
  - [CURRENT] -5 to -25, from Freedom House and RSF, and only for Partly Free or Not Free countries.
  - REVIEW: Ukraine and Moldova -5.
- **All 48 nations of the 2026 World Cup** (2026-09-28): "expand the nations affinity page to include all nations from the 2026 world cup, even if they are not listed in any matches". [CURRENT]
- **Squad interplay for nations** (2026-09-30) [CURRENT]: players at clubs he rates above 63 lift their nation, players at clubs below 35 pull it down, and captains count 1.5x. Bump = link/3, up to ±2.

### B13. Women's game
- **Round 2** [CURRENT]: men's and women's clubs are rated in their own contexts, with equitable adjustments for crowds, history, investment and ownership. League-agnostic within each game. The player-welfare record counts in Values.
- **Round 3:** squads who led the equal-pay and welfare fights raise Team.
- **Players:**
  - Women are scored against the women's game (SCORING_BRIEF).
  - Quiz 7 s01: separate lists ("Their own separate lists"). [CURRENT]
  - A woman's spell at a European club the tracker rates only for its men's side counts as neutral (2026-10-07, answer "1 and 2"). [CURRENT]
  - The money-league penalty applies to men only.
- **Kevin's women's background** is NWSL, mostly Thorns, plus past World Cups casually. The list rests on research.
- **2026-10-06, "both, start with the Thorns"**: he approved an NWSL tag and filter on the women's list (built) and a walkthrough of NWSL players. The walkthrough stalled after the first player, Fleming (see E).

### B14. Leagues, bandwidth, familiarity
- **No familiarity bonus.** The EFL +8 proposal was rejected: "I’m not sure that’s the right move." The same reply set out the tier-1 preference.
- **Bandwidth is not Affinity** (2026-09-29, "do both and ship it"). [CURRENT] "Your leagues" and "Meets your clubs" tags plus an "In your competitions" filter. They never change a score, because adding points lowered the gut fit.
- **USL** counts as top flight for track record (2026-10-02).
- **League filter display** (2026-10-02): "Premier League - Aston Villa - 3 (61)", that is, league rank then overall rank. [CURRENT]

### B15. Player Affinity

**Basis** (2026-10-06): his existing preference research. He gave latitude on the algorithm and asked for active and all-time lists of 50-100 each.

**Weights.**
- The round 7 100-point budget was dropped ("I'm not good at the whole budget thing").
- Named head-to-heads were rejected as name recognition.
- [CURRENT] Weights are fitted to mystery-player pairs (rounds 8 and 9) plus the round 10 controlled named pairs: CH 25, WK 27, LO 17, AB 5, ST 16, LE 10. Fitted connection and penalty multipliers apply.

**Role model × performance** (2026-10-07, "yes, apply it and ship it") [CURRENT]:
- Player Affinity = 100 × (role/100)^0.6 × (perf/100)^0.4.
- perf = 0.40 Greatness + 0.35 Legacy + 0.25 Joy to watch. The shares are fixed, not fitted, because his goal names performance as a requirement.

**Penalties** (round 7 best-worst m1-m9) [CURRENT]:
- Base severities: abuse allegations 18, racist abuse 14, match-fixing 14, violent conduct 7, authoritarian ambassador 7, tax fraud 5, doping 4, Saudi move 3, forced transfer 3, rival move 2. All are then scaled by the fit multiplier, about x2.9.
- Dropped or acquitted cases count 30%. An apology counts 60% (quiz 7 s06 "It counts less").
- A move made as a coach counts half.
- Starring for a state-owned club was ranked least bad in both of its sets and is not penalised separately.

**Caps.**
- "no cap. shitheads need not apply." (2026-10-06) [CURRENT] Penalties stack with no cap.
- Provocation discount (Zidane, offered): declined, "leave it as is".
- Borderline incidents for Keegan (1974 Bremner fight) and Matthäus (Gladbach → Bayern): "both before my time, so, no opinion". Claude kept both.

**Loyalty** (2026-10-06) [CURRENT]: judge from when a player settles, around 23. Youth moves and loans do not count. A late-career move abroad or to MLS is not disloyal ("won't hold a sunset move to Galaxy against him").

**Money leagues** (2026-10-06, answer "B") [CURRENT]:
- A move to a Saudi, Qatari, Emirati or Chinese Super League club costs by age at the move: 7 at 29 or younger, 4 at 30-33, 2 at 34+, before the multiplier (about -19 / -11 / -5.5 effective).
- Moves found in the club list count too.
- Coaches pay 3 × 0.5. Men only.

**Club connection.**
- Quiz 7 s05: "Big boost" for players who starred for his clubs. s04: "a little" against players whose best years were at a club he dislikes.
- 2026-10-06: Dortmund at half weight.
- 2026-10-07: "1 and 2", then "Apply the dortmund change to all clubs. Base it solely on affinity rating, not my stated favorites".
- [CURRENT] Each season counts by club Affinity alone: up to +0.6 per season, down to -0.6, gains capped at +4, losses at -3. Followed clubs get nothing extra. Women's clubs read NWSL ratings only.

**US internationals.** Quiz 7 s07: "Get a small boost". [CURRENT] +2 (in connection).

**Era.**
- Quiz 7 s02: "Count a bit less". Overridden by Kevin's [queued] 2026-10-06 note: "I feel it unfair to assess them through that lens".
- [CURRENT] No era discount. Not knowing a player is never a judgement on him.

**Position.**
- Quiz 7 s03: he most loves watching Playmaker / No. 10 and Full-back.
- The boost was set at +3 and fitted at +7.2, then +5.9.
- 2026-10-07: "Without position bonuses or demerits" / "Do the same overall. It matters very little."
- [CURRENT] POS_BOOST = 0. His taste for flair survives in Joy to watch, and the SCORING_BRIEF anchors still say he loves No. 10s and attacking full-backs.

**Values in Character.**
- Round 11 (2026-10-07, "another quiz that explores personal values alignment"), as logit weights:

  | Trait | Weight |
  |---|---|
  | betting | -3.1 |
  | refused Pride | -2.8 |
  | rainbow armband | +2.5 |
  | speaks on racism | +2.3 |
  | left campaign | +2.2 |
  | right campaign | -1.8 |
  | fair play | +1.2 |
  | funds schools | +1.1 |
  | private life | +0.3 |
  | criticises FIFA/owners | -0.2 |

- Round 11 direct answers:

  | Statement | Answer |
  |---|---|
  | takes the knee | ++ |
  | rainbow armband | ++ |
  | backs a left-leaning politician | ++ |
  | backs a right-leaning politician | -- |
  | talks about faith | 0 |
  | talks about mental health | ++ |
  | criticises FIFA or owners | 0 |
  | fronts betting or crypto | -- |
  | flashy social-media lifestyle | 0 |
  | funds a hometown hospital or school | ++ |
  | known for diving | - |
  | switches national teams | - |

- "Do another one on different topics. And strengthen it in the ratings." Round 12 weights:

  | Trait | Weight |
  |---|---|
  | indiscipline | -2.8 |
  | feuds | -2.3 |
  | rows with fans | -2.0 |
  | taunts | -1.7 |
  | women's game | +1.3 |
  | time with fans | +1.2 |
  | private jet | -0.9 |
  | mental health | +0.9 |
  | climate | +0.2 |
  | Common Goal | 0 |

- Round 12 direct answers:

  | Statement | Answer |
  |---|---|
  | refugees | ++ |
  | union | ++ |
  | badge-kiss then transfer request | -- |
  | contract pushed via the media | -- |
  | honest interviews | ++ |
  | vegan/sustainable | + |
  | plays through injury | 0 |
  | owns a lower-league/fan-owned club | ++ |
  | outside interests | ++ |
  | early national-team retirement | 0 |
  | referee dispute after the match | -- |
  | youth mentor | ++ |

- [CURRENT] VALUES_X doubled from 0.3 to 0.6 ("strengthen it").
- Media rule [CURRENT]: contract_media -4 ("pushing a transfer through the media is far worse than having discussions behind closed doors. One is business, the other is manipulation."). Talks behind closed doors are not penalised.
- Forced-transfer baggage and the media tag both apply. The double count for Isak and Dembélé was flagged and left in.
- Coutinho and Courtois media tags were cleared: "were they publicized before a resolution was reached?" → "yes, clear them", because leaks are not the player's own push.

**Lists** [CURRENT]: men's and women's, active and all-time. The all-time list includes active players. All 100 men of The Soccer 100 were added (2026-10-08).

**Position labels.** "Endo at CB? He’s a CDM." (2026-10-08). Use a player's real role, not emergency cover positions.

### B16. Clubs ↔ players integration
- 2026-10-07 "full integration ... bilateral influence ... run it and ship it". [CURRENT]
  - Club → player: connection per club season.
  - Player → club: the best 5 current players move Team by up to ±1.5, and the best 5 icons move History by up to ±1.
  - Player scores used here leave out connection, so the two sides don't echo.
- Kevin left it open whether this should be "one unified model?". The rebuild brief now asks for "one monolithic model".

### B17. Plastic-fan check (2026-10-09, "account for that however you see fit. I don't want that label")
- [CURRENT] Global brands lose points by Deloitte Money League rank: top 5 -3, 6-10 -2, 11-20 -1. Liverpool -3, Dortmund -1.
- Celebrity bandwagons lose -2: Inter Miami and Wrexham.
- US home nation +20.
- Players unchanged.

### B18. App silos (affects how preferences are measured)
- [CURRENT] No Affinity or pick 'em on match cards (2026-10-02).
- A "Pulled for" row (home / away / neither, plus a note) appears on neutral matches.
- Pick 'em is scored on the 90-minute score: 2 points for the result, 3 for the exact score (CLAUDE.md).

---

## C. Concrete judgements usable as test labels

"Model then" is the value shown to Kevin at the time. "Now" is the current value, given where useful.

### C1. Direct statements and corrections

| Entity type | Item(s) | Judgement | Date | Source quote / note |
|---|---|---|---|---|
| Club | Dortmund vs Union Berlin | Dortmund should rank above Union | 2026-09-28 | "I'm a little surprised that there wasn't as much movement between Dortmund & Union Berlin"; chose ±20% so Dortmund passed Union. Later softened: Dortmund to be judged "objectively as you would any other team" (2026-10-06). Now Union 86.3 (4th) > Dortmund 83.3 (7th). |
| Club | Timbers vs Sounders | Timbers above Sounders, on merit | 2026-09-29, 2026-10-02 | Cascadia decider Portland +8. "(as long as timbers stay above sounders on merit lol)". Now 80.1 vs 79.0. |
| Club | Timbers vs Sounders (gut) | Wants Portland to win a dead-rubber derby; would pick the Timbers from zero; switching would NOT feel like betrayal | 2026-09-29 | Cascadia g1=Portland, g2=Timbers, g3="No" |
| Club | Thorns vs Timbers | Should not be dragged down by the link (implied) | 2026-09-28 | Accepted "gain from better, lose only to disliked" |
| Club | Brighton | Overrated (gut 3 vs model 65.1) → owner's betting fortune -3 | 2026-09-29 | Round 4 vignette. Now 64.6. |
| Club | Arsenal | Overrated: gut 2 vs model 66.1, the biggest gap. Kroenke owns the Rams (rival). | 2026-09-29 | Round 4 vignette → rival ownership -5. Now 60.5. |
| Club | Newcastle | Overrated slightly (gut 1 vs 35.3) | 2026-09-29 | Round 4 vignette |
| Club | Galatasaray | Far below model (gut 3 vs 60.2) → violence doubled | 2026-09-29 | Round 4 vignette. Now 56.8. |
| Club | Celta Vigo | Gut 10 vs model 77.1 (underrated) | 2026-09-29 | Round 5 vignette. Now 77.6. |
| Club | PSV, Sporting CP, Juventus | Rated well below model (gut 5 / 4 / 3 vs 83.1 / 81.3 / 58.9) | 2026-09-29 | Round 5 vignettes |
| Club | Sunderland, Monterey Bay | Above model (gut 7 vs 66.5; 5 vs 41.1) | 2026-09-29 | Round 5 vignettes |
| Club | AFC Wimbledon | Gut 8 (model 80.6) | 2026-09-29 | Round 4 vignette. It dropped to 0.0 track record under the top-flight rule, then no coefficient. Now 80.6 (10th). |
| Club | Wrexham | Gut 4 (model 57.2) | 2026-09-29 | Round 4. Now 65.8 (-2 celebrity bandwagon). |
| Club | Republic | Sacramento Republic ownership 8; hometown +4; Culture 9, History 6 (REVIEW) | original / 2026-09-28 | "Sacramento Republic C9 H6" |
| Club | Portland Thorns | Values back to 8 (research had cut it to 6 over the Yates report) | 2026-09-28 | REVIEW answers |
| Club | Timbers | Ownership "judge on today" = 5, then 6 after Cascadia (past misconduct counts half) | original / 2026-09-29 | |
| Club | Sounders | Culture 9 (NFL stadium), later 8; History 8 → 7; Ownership 6 → 5 | original / 2026-09-29 | Cascadia |
| Club | Dortmund | No favourite treatment; judge like any club | 2026-10-06 | "I wouldn't lower it directly, but assess it objectively" |
| Club | Liverpool | Pull stays strong (contrast with Dortmund) | 2026-10-06 | "the natural affinity hasn't materialized the same way" (as with Liverpool) |
| Club | Kings ↔ Warriors | Warriors are a half rival | 2026-09-28 | "count warriors as a half-rival with kings" |
| Club | Saudi Pro League (as a league) | Negative | 2026-10-06 | "Top players jumping to a 3rd-tier league ... bleh" |
| Club | Lower-tier English clubs | Interest only regional; global clubs should be tier 1 | 2026-09-29 | Rejected the EFL +8 familiarity bonus |
| Player | Wataru Endo | Is a CDM, not a CB | 2026-10-08 | "Endo at CB? He’s a CDM." |
| Player | Bukayo Saka | Belongs in active top 10 (then #10, 82.2) | 2026-10-06 | "he belongs, next". Now #4, 84.8. |
| Player | Martin Ødegaard | Belongs (then #9, 82.4); Loyalty was too low | 2026-10-06 | Loyalty rule. Now #12, 78.1. |
| Player | Christopher Trimmel | Belongs (#8, 82.5) | 2026-10-06 | "I don't know much about him but sounds like someone I would support" / "he belongs". Now #18, 75.9. |
| Player | Roberto Firmino | Belongs (#8, 83.3), but the Saudi move should cost more (age-scaled option B) | 2026-10-06 | Now #15, 76.6. |
| Player | Sebastián Blanco | Unknown | 2026-10-06 | "hard to say. not familiar with him". Now #62. |
| Player | Mohamed Salah | #7 "seems about right" (83.4) | 2026-10-06 | Also gut 9 (round 7). Now #20, 75.0. |
| Player | Trent Alexander-Arnold | #6 "fair assessment" (83.6) | 2026-10-06 | Now #29, 71.7. |
| Player | Shinji Kagawa | Unknown | 2026-10-06 | "not sure, unfamiliar". Now #39. |
| Player | Thomas Müller | Belongs at #3 despite being a Bayern lifer (90.7) | 2026-10-06 | "Agree with your assessment". Now #1, 89.0. |
| Player | Marco Reus | #2 "seems about right" (91.8); a late Galaxy move is not held against him. But gut 6 in round 7. | 2026-10-06 | Now #19, 75.0. |
| Player | Andy Robertson | "possibly" #1 (97.2) | 2026-10-06 | Now #2, 86.6. |
| Player | Zidane | Wondered if the 2006 headbutt was provoked and out of character; accepted the record once it showed a pattern | 2026-10-06 | "leave it as is" (27.3; now 25.4). Gut 7 in round 7. |
| Player | Keegan, Matthäus | No opinion on the borderline incidents | 2026-10-06 | "both before my time, so, no opinion" |
| Player | Coutinho, Courtois | Clear the media-push tags (leaks, not the player's own push); forced-transfer penalty stays | 2026-10-07 | "were they publicized before a resolution was reached?" → "yes, clear them" |
| Player | Isak, Rashford, Salah, Lewandowski, Mbappé, Kvaratskhelia, Chloe Kelly, Dembélé | Media pushes count -4 | 2026-10-07 | "One is business, the other is manipulation." |
| Player | George Hemmings (Villa) | Negative: possessions die at his feet | 2026-10-06 | observations.json. Signal: ball security / keeping moves alive. Not in the pool. |
| Player | Lists in general | Should be topped by role models who also perform | 2026-10-07 | Role-model goal (A) |
| Player | Liverpool squad, position-neutral | Asked to rank without position bonus; "It matters very little" | 2026-10-07 | → POS_BOOST 0 |
| Player | Jessie Fleming | Asked "does 75.7 match what you've seen?", no answer | 2026-10-07 | Open |

### C2. Gut ratings of anonymous clubs (0-10; the 26-vignette test set)

| Club | Gut | Model then | Now | Round |
|---|---|---|---|---|
| Celta Vigo | 10 | 77.1 | 77.6 | 5 |
| AFC Wimbledon | 8 | 80.6 | 80.6 | 4 |
| Bodø/Glimt | 7 | 90.9 | 85.3 | 4 |
| Sunderland | 7 | 66.5 | 69.6 | 5 |
| Union Berlin | 6 | 85.3 | 86.3 | 4 |
| Athletic Club | 6 | 100 | 99.1 | 4 |
| Napoli | 6 | 79.3 | 74.3 | 5 |
| Leeds United | 6 | 70.0 | 72.2 | 5 |
| Detroit City FC | 6 | 78.0 | 77.1 | 5 |
| Real Madrid | 5 | 65.5 | 52.5 | 4 |
| Marseille | 5 | 58.1 | 52.6 | 5 |
| PSV Eindhoven | 5 | 83.1 | 74.9 | 5 |
| Monterey Bay FC | 5 | 41.1 | 45.1 | 5 |
| Wrexham | 4 | 57.2 | 65.8 | 4 |
| Bay FC | 4 | 41.3 | 44.0 | 4 |
| Sporting CP | 4 | 81.3 | 74.4 | 5 |
| Brighton | 3 | 65.1 | 64.6 | 4 |
| Galatasaray | 3 | 60.2 | 56.8 | 4 |
| Juventus | 3 | 58.9 | 53.2 | 5 |
| Oakland Roots SC | 3 | 67.3 | 68.6 | 5 |
| Inter Miami CF | 2 | 30.9 | 25.3 | 4 |
| Arsenal | 2 | 66.1 | 60.5 | 4 |
| Chelsea | 2 | 30.2 | 28.0 | 5 |
| Newcastle United | 1 | 35.3 | 36.4 | 4 |
| Lazio | 0 | 26.8 | 22.1 | 4 |
| Manchester City | 0 | 18.7 | 12.9 | 5 |

Correlation with today's model: r = 0.778. Caveat (Kevin, 2026-09-29): he recognised at least half of these clubs, so they are not strictly blind.

### C3. Club head-to-heads, rapid fire, round 6 (2026-09-29; named, pairs within 8 points)

Format: picked > not picked (model at the time). The model then agreed on 15 of 36; it agrees on 16 of 36 today. The picks lean to EFL clubs (18 of 26 won), which Kevin attributes to familiarity and bandwidth, not fit.

| # | Pick > not picked (model then) |
|---|---|
| 1 | West Ham > Fenerbahçe (47.5 v 49.6) |
| 2 | Ipswich > Augsburg (48.2 v 48.7) |
| 3 | Shrewsbury > Real Salt Lake (52.1 v 60.0) |
| 4 | Crystal Palace > Orlando City |
| 5 | Sheffield Wednesday > Bologna (63.8 v 69.6) |
| 6 | Coventry > Wrexham |
| 7 | Orlando Pride > Phoenix Rising |
| 8 | Torino > Oxford |
| 9 | Accrington > Levante (54.6 v 58.2) |
| 10 | Swindon > Rennes |
| 11 | Southampton > Parma |
| 12 | Hartford Athletic > FC Dallas (50.9 v 58.5) |
| 13 | Doncaster > Málaga |
| 14 | New England > Millwall |
| 15 | Cardiff > Auxerre |
| 16 | Brest > Swansea |
| 17 | Vancouver > Colorado Springs |
| 18 | Sporting KC > Angel City |
| 19 | Reading > Fulham |
| 20 | Gotham > Club Brugge |
| 21 | Rochdale > D.C. United |
| 22 | Leyton Orient > Mainz (65.3 v 69.6) |
| 23 | Lille > Villarreal |
| 24 | Peterborough > Galatasaray (55.4 v 62.9) |
| 25 | Charlton > Inter |
| 26 | Notts County > Schalke (65.0 v 72.6) |
| 27 | San Diego Wave > Atlanta United |
| 28 | Columbus Crew > Arsenal |
| 29 | Napoli > Portsmouth |
| 30 | Wolves > LASK |
| 31 | Washington Spirit > Plymouth |
| 32 | Brentford > New Mexico United (63.3 v 70.9) |
| 33 | Sunderland > Barnsley |
| 34 | Bromley > Monaco |
| 35 | Leicester > Oakland Roots (60.8 v 67.3) |
| 36 | Bolton > Cambridge |

### C4. Club traits, round 6 (34 paired comparisons, 2026-09-29)

Ranked from his picks:
- **Top:** anti-racist stance (won 4 of 4), serious community work (4 of 4), a real women's team.
- **Next:** a coach who defines the club, players who hug the fans, the same captain for 10 years.
- **Middle:** legendary history, then near the top most years.
- **Low:** the crowd traits (100-year-old ground, crowds through relegation, loud singing, away following) and a trophy last season.
- **Bottom:** relentless pressing, fan ownership, cheap tickets, and "two hours from home" (0 of 3).

Notable pairs:
- Near the top most years > a trophy last season.
- Same captain for 10 years > owned by its fans.
- Cheap tickets > owned by its fans.
- A legendary history > owned by its fans.

### C5. Player gut ratings (round 7, 2026-10-06; 0-10, "dk" = don't know)

| Player | Gut | Now |
|---|---|---|
| Salah | 9 | 75.0 |
| van Dijk | 9 | 80.1 |
| Haaland | 9 | 63.1 |
| Bellingham | 8 | 66.5 |
| Modrić | 8 | 71.3 |
| Sophia Wilson | 8 | 79.5 |
| Rapinoe | 8 | 88.8 |
| Kane | 7 | 81.0 |
| Mbappé | 7 | 45.9 |
| Yamal | 7 | 62.4 |
| Zidane | 7 | 25.4 |
| Donovan | 7 | 82.5 |
| Ronaldo | 6 | 0.0 |
| Messi | 6 | 40.9 |
| Vinícius | 6 | 64.6 |
| Reus | 6 | 75.0 |
| Beckham | 5 | 65.6 |
| Pulisic | 4 | 62.7 |

He answered "dk" for Bonmatí, Horan, Rashford, Neymar, Son, Müller, and every all-time icon except Zidane, Beckham, Donovan and Rapinoe. That includes Maradona, Cantona, Totti, Cruyff, Maldini, Ronaldinho, Keane, Gerrard, Henry, Iniesta, Sinclair, Drogba, Dalglish, Suárez, Rooney and Xavi.

Correlation with today's model: r = 0.34. The gut ratings track talent and fame, while the model tracks character. This gap is the central tension (see D).

### C6. Named player head-to-heads

**Round 10, controlled pairs (2026-10-06).** Picks: picked > not picked, with the factors each pair tested.
- Szoboszlai > Mac Allister (LE, POS)
- Szoboszlai > Gakpo (LO, POS)
- Gakpo > Gravenberch
- Mac Allister > Gravenberch
- Schlotterbeck > Ryerson
- Jobe Bellingham > Anton
- Ryerson > Anton
- Kyle Edwards > Velde
- Chará > Mora
- Vitiello > Desmond
- Da Costa > Kamal Miller
- Velde > Pantemis
- Kane > Vinícius
- Yamal > Pedri
- Saka > Lautaro

Passes:
- Both players unknown: Frei/Simón, Frei/Oblak, Son/Oyarzabal, Hegerberg/Williamson, Banda/Rolfö, Bronze/Debinha, Chawinga/Oberdorf, Nico Williams/Musiala, Dalglish/Rush, Rush/Hyypiä, Dalglish/Barnes, Fowler/Owen.
- Partial pass: Gavi/Rice, Nico Williams/Bruno Fernandes, Oyarzabal/Kane.

The current model agrees on 9 of 15.

**Round 8, named pairs (2026-10-06).** These were judged to follow name recognition. Picks:
- Salah > Reus
- van Dijk > Núñez
- Tyler Adams > Zidane
- Gakpo > Sancho
- Szoboszlai > Messi
- van Dijk > Neymar
- Rice > Luis Díaz
- Haaland > Brandt
- Sophia Wilson > Sinclair
- Yamal > Henderson
- Ronaldo > Bruno Fernandes
- Brandt > Mbappé
- Lewandowski > Luis Díaz
- Bellingham > Mbappé
- Zidane > Firmino
- Isak > Sancho
- Bellingham > Tyler Adams
- Saka > Beckham
- Rice > Ronaldo
- Kane > Yamal
- Donovan > Rodri
- Palmer > Pulisic
- Sophia Wilson > Kerr
- Ødegaard > Suárez
- Salah > Gravenberch
- Alisson > Henderson
- Mac Allister > Vinícius
- Wirtz > Kanté
- Neymar > Núñez

Rodri vs Suárez was skipped. The current model agrees on 18 of 29.

### C7. Player attribute picks (round 7 this-or-that, 2026-10-06)

Picked > not picked:
- Captain for 12 seasons > Ballon d'Or winner
- Nutmegs and no-look passes > Wins every tackle
- Speaks out against racism > Scores the winner in a final
- Stays after relegation > Leaves to win the Champions League
- Academy kid > Record signing
- Applauds the fans after every loss > Scores 30 a season
- Quiet, lets his football talk > Big personality
- **Grinder who never stops running > Genius who drifts out**
- Funds free school meals > Wins the treble
- Played for your club > Best in the world at his position
- Ten years of steady excellence > One moment everyone remembers
- Playmaker > Goal machine
- Never dives > Wins penalties
- Took a pay cut to stay > Won everything abroad
- Retired at boyhood club > Last big payday in Saudi Arabia
- Leads by example > Leads by shouting
- Openly backs LGBTQ+ fans > Keeps out of politics
- **Superstar who delivered > Overachiever who got the most from his gifts**
- Model professional > Flawed genius
- You watched his whole career > A legend from before your time
- Pioneer of the women's game > Star of the men's game
- Hometown hero > World famous
- **Winger who beats his man > Defender who reads the game**
- Ran to celebrate with the away end > Went straight back

Other round 7 answers:
- Budget: CH 30, WK 20, LO 15, AB 10, LE 10, ST 10, CO 5. This was later discarded.
- Choices: s01 separate lists; s02 "a bit less" for players before his time (overridden); s03 Playmaker + Full-back; s04 "a little" against players whose best years were at a club he dislikes; s05 "Big boost" for his clubs (overridden 2026-10-07); s06 apology "counts less"; s07 US internationals "small boost"; s08 trophies "matter some".

### C8. Cascadia decider, item by item (2026-09-29)

Head to head, signed toward Portland (+) or Seattle (−) on a -3 to +3 scale:

| Dimension | Lean |
|---|---|
| ground | +3 |
| sponsors | +3 |
| owner conduct | +2 |
| direction | +2 |
| history | +1 |
| supporters | 0 |
| practical | 0 |
| fan voice | −2 |
| academy | −2 |
| community | −1 |
| women's link | −1 |
| coach | −1 |
| squad | −1 |
| record | −1 |

Importance (0 / 1 / 2 / 3 / 5):
- 3: supporters, ground, community, squad, history, direction.
- 2: owner, voice, sponsors, women, coach, academy, record.
- 1: practical.

Scenarios (happiness 0-10):

| Scenario | Score |
|---|---|
| Two trophies in five years, but a new suburban stadium | **8** |
| No trophies, but the old ground still packed and loud | 6 |
| The owner fans once told to sell, decent but trophyless | 5 |

### C9. Family Club Draft (2026-09-29; deprecated, context only)
- Kevin's own run matched his Affinity at 0.905. His top 6 were the Thorns, Liverpool, Athletic, Dortmund, Union and Republic.
- Persona: "The Underdog Romantic, with a big heart". It was "The Idealist" before a fix.
- He picked the giant stadium and the dynasty, which put Arsenal in his top 10.

---

## D. Conflicts and how each was resolved

1. **Track record: stated preference vs gut ratings.**
   - What he said: he asked for a performance coefficient and wanted ±20% so Dortmund passes Union. Round 4's trade-offs weighted the record strongly (DCE +0.6), and the round 5 single-trophy item came out at +0.64.
   - What the data showed: every round 5 method ranked winning low (budget 10 of 100, everyday 0.0, "cup last season" negative). The gut fit rises as the effect shrinks (0.728 at ±20% up to 0.785 at ±5%; 0.788 with none).
   - Resolution: ±20% → ±15% (round 5) → ±5% for the top flight + USL only (2026-10-02). Today the model has Union above Dortmund again, which conflicts with his 09-28 judgement. That judgement was effectively superseded by "assess [Dortmund] objectively" and the pull away from Dortmund.
   - The Cascadia scenario score (8 for trophies plus a suburban stadium vs 6 for an old loud ground) also says winning matters more in a concrete trade than his abstract rankings suggest. **Unresolved in the model.**
2. **Lower-tier English clubs.**
   - What he said: lower-tier interest is "primarily regional", and global clubs should be tier 1, mid-table or better.
   - What the data showed: his gut and named picks favour EFL clubs (AFC Wimbledon 8, Sunderland 7, Notts County > Schalke, and so on).
   - Resolution: the stated rule won. Judged against the top flight, League One/Two clubs dropped 12-16 points and the fit fell from 0.747 to 0.723. Then on 2026-10-02 lower English clubs were taken off the coefficient entirely, which restored AFC Wimbledon to 10th.
   - The familiarity bonus (EFL +8) was rejected. Bandwidth is shown as tags and filters, never as points.
3. **Culture's weight.**
   - Round 4 (forced pairs 1 of 4, DCE -0.21) and round 6 (crowd traits low) put it low. Round 5's budget gave it 25, equal to Values, and its trade-offs weighted the crowd most (DCE C +1.43).
   - Resolution: averaged to 23.
4. **Ground vs modern stadium.**
   - Round 5: ground 50 of the Culture budget, but he'd take the new ballpark with perfect views. Round 6 e12: "Old ballpark > New ballpark". Cascadia: ground +3 for Portland, yet the suburban-stadium-with-trophies scenario scored 8.
   - Resolution: historic ground is preferred, and an NFL stadium counts "a little". Not fully reconciled.
5. **Distance and localism.**
   - Round 5 quick sort: "Two hours from Sacramento" +1.25, one of the strongest pulls; localism +0.67. Round 6: "two hours from home" lost all 3 matchups and ranked last. Round 4: localism +0.27.
   - Resolution: kept at up to +4. The rapid-fire round was called too noisy to move weights.
6. **Women's game.**
   - Round 4's single item picked the men's game (WOM -0.67). Round 5's quick sort pulled strongly ("Women's team sells out" +1.21). Round 6 ranked a women's team near the top. Round 7 picked "Pioneer of the women's game > Star of the men's game".
   - Resolution: no preference adjustment. The women's-context rule is about fair rating; women's teams count in Values.
7. **Forgiveness and decay.**
   - Round 4 was inconsistent: he forgives changed people and new owners, but "some mistakes should follow a person for good". Round 5 found old wrongs fade (+0.39), with violence 8 years ago cheap and last season's costly. Round 6 e15 picked "Remember" over "Forgive".
   - Players: an apology counts less (60%), and dropped or acquitted cases 30%. Clubs: penalties from a previous owner are dropped, and owner misconduct with consequences and no repeat counts half.
   - Resolution: the general 5-year decay for club incidents was **never applied**; none qualified in the scrapped run.
8. **Talent vs character for players.**
   - Mystery pairs put Greatness at about 5% and Team player first. His round 7 gut ratings track talent (Haaland 9, Mbappé 7, Zidane 7, Ronaldo 6, Messi 6; r = 0.34 with the model).
   - He picked "Superstar who delivered" over "Overachiever", "Genius" over "Grinder" (round 6 e10), and "Winger who beats his man" over "Defender who reads the game". Yet round 7 p08 picked "Grinder" over "Genius". The pick was reversed between rounds.
   - Round 10: Team player called only 3 of 7 of his named picks, while Joy to watch called 5 of 7.
   - Resolution: the role-model × performance geometric mean with fixed performance shares (2026-10-07), justified by his goal statement ("all while delivering performances ... worthy of the highlight reels and the history books").
   - Still open: the walkthrough players he endorsed have since fallen a long way. Trent is #29 against #6 "fair assessment"; Salah #20 against #7 "about right"; Reus #19 against #2 "about right"; Trimmel #18; Ødegaard #12. Only Müller, Robertson and Saka are still in the top 10.
9. **Club connection for players.**
   - Quiz 7 s05 asked for a "Big boost" for his clubs, and the fit was 73-75% with followed clubs boosted. On 2026-10-07 he said "Base it solely on affinity rating, not my stated favorites".
   - Resolution: his explicit later instruction wins; the fit fell to 71%. The player connection cap (+4) and the club-side Liverpool -3 brand penalty both now pull Liverpool players down.
10. **Era discount.**
    - Quiz s02 said "count a bit less". His [queued] note on 2026-10-06 said that judging pre-era players through his not-knowing is "unfair".
    - Resolution: no era discount.
11. **Position preference.**
    - He loves playmakers and full-backs (s03), and the fitted boost was +5.9 to +7.2 (it called 4 of 5 pairs). He then said "It matters very little".
    - Resolution: POS_BOOST 0. His explicit word won over the fit (73% → 71%).
12. **Values on stance-taking.**
    - "Criticises FIFA or owners" scored 0 / -0.2. Yet he wants players who "stand up and speak out for what is right", and he values anti-racism, Pride and union work highly.
    - Resolution: weights by issue. Political stances are signed: left +2.2, right -1.8.
13. **Crypto and fossil fuels.**
    - For clubs, crypto/NFT and fossil-fuel sponsors have no effect (round 2). For players, "fronts a betting or crypto brand" is "--" (round 11).
    - Not reconciled across clubs and players.
14. **US connection.**
    - Clubs: round 3 said "US players, clubs visited in person: no bonus". Players: quiz 7 s07 gave US internationals a "small boost" (+2).
    - Plastic fan: Kevin "doesn't want that label". This led to brand penalties and a home-nation US +20. The +20 is twice the heritage cap and sits uneasily with "glory hunting is the charge": Liverpool, the club he actually follows, takes -3.
    - The US +20 was Claude's call under "however you see fit". **Worth re-checking with Kevin.**
15. **Ownership fold.**
    - Kevin: "ownership issues should be folded into the ownership category. re weight if needed to improve gut fit". A true fold lost fit and let Man City and others gain 17-25 points.
    - The assistant recommended a card-level fold. Kevin answered a different question ("yes" to the Pulled-for button) and never ruled on it.
    - Resolution: penalties stay separate. **His instruction is not literally implemented.**
16. **Timbers vs Sounders.**
    - Cascadia's verdict was Portland +8. Removing the rival penalties put the Sounders ahead on track record and homegrown share. His condition: "as long as timbers stay above sounders on merit".
    - Resolution: the 2026-10-02 add-on review (±5% track record) restored the Timbers on merit. A binding adjustment was offered and not used. The rebuild must keep the Timbers above the Sounders without a decree.
17. **Rival penalties vs association.**
    - Round 3 set -5 penalties. On 2026-09-28 he said "skip rival pairs" in association. On 2026-10-02 he removed all rival penalties.
    - Resolution: [CURRENT] no rival penalties, and the association now links Sounders and Reign. The big-4 rival market and ownership items remain: sports rivals still count, football rivals don't.
18. **Dortmund.**
    - Followed club (bandwidth list) and "Dortmund above Union" (09-28), versus "feeling a little pull away" and "assess it objectively" (10-06).
    - Resolution: no favourite treatment anywhere. Dortmund now sits 7th, below Union.
19. **Double counts that were accepted.**
    - Southampton Spygate sits in both Values and the adjustment (REVIEW, his choice).
    - Isak and Dembélé pay forced transfer plus the media tag (flagged, left in).
    - Coutinho and Courtois media tags were cleared.
20. **Familiarity in the gut data.** Kevin pointed out the anonymous clubs were recognisable, so the "blind" gut set is partly a named set. The rebuild should not treat the 26 vignettes as clean blind labels.
21. **Stale documentation.** These conflict with the code and are not preference conflicts:
    - heritage.json says US +10; it is +20.
    - The rescore.py header says k = 0.85 + 0.03 P; it is 0.95 + 0.01 P.
    - The players/model.py docstring describes the old fixed-club connection.
    - The whitepaper (claude.ai doc) is out of date. Claude flagged this on 2026-10-02 and Kevin never answered.

---

## E. Asked for, or offered and left open, never implemented

1. **Heart-over-head calibration.**
   - Kevin, 2026-10-02: "the next true iteration of this is a true heart-over-head accounting." The "Pulled for" row exists, but the data sits in his Firestore and is not reachable from the repo.
   - "are you recording my pulled for ratings anywhere?" (2026-10-05) drew an offer of a "Pulled for" log screen with a copy button. He never answered, and it was not built.
   - The plan was to replace the vignettes as the fit test after about 30 pulls and to add a per-club "heart" adjustment after about 75. Neither has happened.
2. **"Who stood out" player tap** after matches, and match-note capture. Offered on 2026-10-06; not built. One observation (Hemmings) is logged.
3. **Splitting Greatness into "on-ball reliability" and "star talent"**, prompted by the Hemmings note. Deferred until more notes arrive.
4. **Ownership "fold into the ownership category"** (2026-10-02). Neither the card-level grouping nor the true fold was done (D15).
5. **NWSL women's walkthrough** ("both, start with the Thorns"). It stalled at the first player, Fleming ("does 75.7 match what you've seen?"). Moultrie, Sophia Wilson and the other NWSL players were never covered. Chará (#10 at the time) was never walked through either.
6. **Desailly:** the tabloid-only allegation (-58.8) is still counted in full. "Discount allegations that only appear in tabloids?" got no answer.
7. **National-team switching tag:** round 11 rated it "-", but it was never tagged (Iñaki Williams, Diego Costa, Thiago Motta and others). Offered on 2026-10-07; no answer.
8. **Incident decay** (old club incidents count half after about 5 years): recorded in the research brief, never applied.
9. **Round 5 sub-weights inside the factors:** scrapped, recorded only.
10. **Celtic association (YNWA)**, one of Kevin's own examples. Celtic is not in links.json. It exists only as a heritage club (since 2026-10-08), and the Liverpool/Dortmund/Celtic YNWA link was never added.
11. **Heritage clubs, open calls:**
    - Rangers multi-club -3 (secondary to Leeds).
    - Hearts and Union SG: Bloom stakes.
    - Plzeň: owner's arms fortune -3.
    - Linfield: racism -6.
    - Celtic: violence -4.
12. **Self-consistency test** (repeat 8 mystery pairs flipped to measure his noise ceiling) and an **interaction-traits round** (talent counting only with effort; redemption outweighing baggage). Offered on 2026-10-06; not done.
13. **Using player Affinity in the app**, for example Match of the week or "players to watch" on cards. Offered and not built. It would also conflict with the silo rule, which keeps Affinity off match cards.
14. **Soccer 100 reading feedback.** He is reading the book, and Claude asked him to report who stood out. No entries have been logged. The book's 100 men were added and ranked (2026-10-08); Kevin made no comment on the ranking.
15. **"(or one unified model?)"** (2026-10-07). Two linked models were kept. The 2026-10-09 brief now asks for "one monolithic model across all teams, nations, players, leagues".
16. **Whitepaper update.** The claude.ai doc artifact is stale since 2026-10-02 (track record, rival penalties, adjustments).
17. **Republic women's team.** Research found none, so its women's-team sub-score was 4 in the scrapped sub-weights run. Claude asked Kevin to correct it if wrong; no answer.
18. **Familiarity / "clubs I'd pick when I see the name".** This was raised and resolved as tags only. If the heart-over-head data later shows a persistent named-club lean, this question returns.
19. **Family Club Draft:** deprecated on Kevin's instruction. Do not refresh it.
