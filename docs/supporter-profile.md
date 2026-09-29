# Supporter profile: quiz round 2 (2026-09-28)

Adds to the original 51-question interview summarised in docs/affinity.md. Questions were
neutral multiple choice; answers below are Kevin's. These define how each factor is judged in the
next full re-rate. Ratings are league-agnostic: the same club gets the same score in any league.

## Culture (supporter culture)
- Main signal: atmosphere (noise, singing sections, choreography, away following).
- A small crowd that is loud and loyal scores higher than a big, quiet one.
- Ultra groups: judged group by group (raise or lower based on what the group stands for and does).
- New stadium in the same city: a temporary drop that fades after some years (not permanent).

## Values
- Ticket prices / affordability: one factor among several ("some").
- Political or social identity is judged by the stance:
  - raises Values: anti-fascist / left-wing identity; regional identity (Basque, Catalan, Scottish, ...)
  - lowers Values: sectarian rivalry; nationalist / right-wing identity; owner-driven political messaging
  - community or religious roots: no effect either way
- Sponsors that count against: sports betting and arms makers (existing), plus firms owned by
  authoritarian states (state airlines, tourism boards, ...). Crypto/NFT and fossil fuels: no effect.
- Raise Values: community work, investment in a women's team, a local academy pathway, a formal fan voice
  (board seats, golden share, fan advisory boards).
- Fan violence (hooliganism, attacks on rival fans, serious disorder): penalised on the same scale as
  tolerated racism (up to -30).

## History
- Measures significance first: famous moments, influence on the game, place in football culture.
- A club liquidated and re-formed by its fans keeps all of the old club's history.
- Clubs in newer leagues get credit for the clubs, leagues or amateur roots they grew out of.

## Ownership
- Ideal: fan / member ownership (supporters' trusts, member clubs, 50+1).
- Conduct counts more than structure: an outside owner who runs the club well scores on that.
- Leveraged buyouts (purchase debt loaded onto the club): serious, just short of state backing (-25).
- Private equity / sports investment funds: a strong negative, on the scale of multi-club (-4 to -8).
- Overspending well beyond the club's natural income counts against the club.

## Style of play
- Rewards intensity: pressing, energy, running for each other.
- Weight stays about where it is (8 of 90).

## Weights
- Trade-offs: an elite atmosphere under a PE fund beats a fan-owned club with a quiet crowd
  (Culture > Ownership). Strong community values beat a big history with poor conduct (Values > History).
- Values is too low. The increase is spread across the other factors.
- Working proposal for the re-rate (sum 90, as now): Culture 26, Values 28, History 16, Ownership 12,
  Style 8 (was 28 / 22 / 18 / 14 / 8). Confirmed 2026-09-28 after the research.

## Nations
- A country's government record (human rights, press freedom) counts strongly, on the scale of
  state-backed club ownership (goes beyond the old "federation tied to the regime" rule).

## Women's clubs (NWSL)
- The men's and women's games are rated in their own contexts. They are not on level footing
  economically or culturally, so equitable adjustments apply: crowds, history, investment and ownership
  are judged against the women's game, not against men's clubs.
- League-agnostic still holds within each game (a women's club scores the same in any women's league).
- Player-welfare record counts in Values.

## Heritage bonus
- Clubs: drop the regional heritage bonus. Keep only the hometown bonus (Sacramento Republic +4).
- National teams: keep the national heritage bonus (up to +10).

# Quiz round 3: players and team culture (2026-09-28)

Players and the squad were not covered before. Answers below. Not yet applied to scores: needs a research
run for the Team factor (see scripts/affinity/research/BRIEF.md, "Team factor").

## Team (replaces Style of play)
- Style becomes Team: how they play (intensity, pressing, running for each other) plus team culture.
- Team-culture signals that count: the player-fan bond (players celebrate with fans, stay after defeats,
  show up in the community) and a stable, humble squad (low churn, no big-ego stars, long-serving captains).
  Fight and a clean dressing room were not picked as signals of their own.
- Icons count only while at the club (Reus-type bond), then they pass into History.
- A defining, long-serving coach (Klopp, Streich, Simeone) raises Team while there.
- Women's clubs: squads and players who led the equal-pay and welfare fights raise Team.
- Time window: the last 3 seasons.

## Values additions
- Player conduct counts, and the club's response counts on top (racist abuse, violence by a player; charity
  and speaking up on social issues raise).
- A club standing by a player facing credible abuse or violence allegations: strong negative (Values -2 or more).
- Player welfare applies to all clubs, men's included (contracts, mental health, treatment of injured or released players).
- One-club players and academy graduates in the first team: a small raise (the academy pathway already counts).

## Not added
- Underdog status: only through History (famous runs), no extra credit.
- US players, clubs visited in person: no bonus.

## Adjustments
- Rivals of clubs Kevin follows: Schalke 04 and Bayern Munich (Dortmund) -5; Seattle Sounders FC, Seattle Reign
  and Vancouver Whitecaps FC (Cascadia) -5; Everton -2 (friendly derby). Manchester United and Republic's USL
  rivals: none.
- Republic link: +2 while a former Sacramento Republic player is on the roster.

## Weights (of 90)
Values 26, Culture 26, History 14, Ownership 12, Team 12 (was 28 / 26 / 16 / 12 / Style 8). Revised after the
research: Values and Culture equal (first quiz answer was 26 / 24 / 14 / 10 / 16).

# Quiz round 4: The Blind Draw (2026-09-29)

75 blinded questions (artifact "The Blind Draw"; bank, hidden key, answers and analysis in scripts/affinity/quiz4).
Methods, chosen to get past stated-preference bias:
- Indirect everyday items (30): each option carries hidden loadings on 16 constructs (the five factors plus track
  record, recency, localism, rivalry, association, penalty severity, forgiveness, underdog, novelty, loyalty, women's game).
- Forced-choice pairs (12): two equally desirable statements on different factors (ipsative, Thurstonian-style), so
  social desirability cancels out and the factors must be ranked.
- Discrete-choice experiment (16): pairs of anonymous clubs over 8 attributes, fitted with a ridge conditional logit
  (revealed weights). Fit: 14 of 16 choices predicted.
- Blind vignettes (13): real clubs described without names, gut-rated 0-10, compared with the model (r = 0.82 before).
- Checks: 3 reversed repeats (2 consistent; forgiveness split: forgives changed people and new owners, but "some
  mistakes should follow a person for good"), an attention check (passed), response times.

Findings (sources agreeing):
- Values first (pairs 4/5, DCE strongest factor, everyday +0.54).
- History and Team up: nostalgic picks (classic film, throwback jersey, old neighborhood; pairs chose story, legend,
  roots) and team-first picks (watch the players, heart over management, steady team at work; everyday Team +0.71).
- Culture lower than weighted: better view over loud section, "somewhere I agree with" over "loud and alive".
- Ownership lowest (pairs 0/4, DCE weak), though private-equity and tech buyouts still worry him.
- Fan violence weighed very heavily in the trade-offs (about 3 levels of Values) and Galatasaray's gut rating was far
  below the model: violence penalties doubled. Sportsbook sponsor: a modest negative (already in Values).
- Rival ownership: Arsenal (Rams owner) was the biggest overrating in the gut check: rival ownership raised to -5.
- Brighton overrated: its owner's betting fortune now counts (-3).
- Track record: split (trade-offs strong, gut ratings prefer less). Kept at +/-20%. Recency: judges a body of work,
  not the last season, so half-life 4 seasons.
- Loyalty very high (+0.9): same barber, favorite places, steady teams. Localism moderate (+0.27; roots for Sacramento
  things "all the time"). Association moderate. Women's game: picked the men's game (no change: the women's-context
  rule is about fair rating, not preference). Underdog: mild, no change.
Result: gut-rating fit r 0.817 -> 0.833; weights Values 27, Culture 20, History 17, Team 16, Ownership 10.
