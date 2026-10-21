# What New York Thinks: methodology

Live page: https://joshgreenman1973.github.io/what-new-york-thinks/

This file explains where every number on the page comes from, what is included and left out, and the little the page calculates. Nothing is averaged, estimated or modeled.

## The caveats (the asterisk in the title)

**Polls are less reliable than they used to be.** Most people no longer answer calls from numbers they don't recognize, so pollsters reach far fewer of the people they try. They make up for it with text messages, online panels and statistical weighting so that the people they do reach resemble the electorate. That works when the people who answer are like the people who don't, and it can fail when they differ in ways the weighting misses. Every poll has a margin of error, and the New York City columns of statewide polls rest on smaller samples whose size is usually not published.

**Nobody really knows how predictive prediction markets are.** A price is what traders will pay, not what the public thinks. Many New York markets trade little money, so one trader can move a price. Manifold uses play money. There is no long record showing how well markets on state and city questions forecast outcomes.

## What the page holds

Every question about New York policy and politics in polls of all New York City or all New York State adults or voters, **fielded from January 1, 2026, through the date in the page's footer**. Each poll's questions are kept separately, one row per question. For statewide polls, the New York City column of the pollster's crosstabs is a second row, marked "city column."

## Sources

Every figure was read from the pollster's own release, toplines, marginals or crosstabs. Each row carries:

- a link to the pollster's release and, where published, to the full tables;
- the exact question wording when the pollster published it;
- a passage copied word for word from the source that contains the figures (`quote`). Where the figures exist only in a table, the passage is the table row as printed, with runs of spaces collapsed;
- field dates, who was surveyed, sample size, margin of error and method.

Independent pollsters shown by default: Siena Research Institute (statewide, about monthly), Marist Poll, Quinnipiac University Poll, Emerson College Polling (with PIX11), Suffolk University Political Research Center (CityView) and Honan Strategy Group.

**Polls paid for by advocacy groups** are in the file but hidden unless a reader switches them on ("Include polls paid for by advocacy groups" in the table's filters). Their rows are marked "advocacy," and their question framing can reflect the sponsor's aims. As of October 21, 2026, there are four: Siena for the New York Civil Justice Institute, a tort-reform group (fielded January 20-25); Echelon Insights for Tusk Strategies, in a fight over a startup tax (March 24-26); Data for Progress for the Institute for Middle East Understanding (May 20-26); and Moxie Strategies for the Firefighters Association of the State of New York (July 22-28). Some of their questions are message tests, which present an argument before asking the question.

**Left out for quality:** Pollfinity Research (June 11-14, 2026; 229 registered voters, unweighted, and its topline and crosstab files disagree by one to two points on several items) and John Zogby Strategies (January 6-8, 2026; the release gives no question wording or full results).

## What is included and left out

Included: polls by a named organization that publishes field dates, sample size and its questions and results.

Left out, and listed in `data/gaps.json`:

- polls of a single congressional or legislative district (for example Emerson's NY-7, NY-10 and NY-12 polls in May 2026);
- campaign, party or interest-group polls released without full questions and results;
- any poll whose figures could be found only in news coverage (for example parts of Honan Strategy Group's June and October 2026 polls);
- questions about respondents' own behavior rather than policy or politics (for example how they bet on sports), and non-political questions (a Pope Leo XIV favorability item, a baseball poll).

Honan Strategy Group's June 2026 memo published results for Jewish and non-Jewish likely voters but no figure for all voters. The page shows the two figures it published and does not combine them.

## How the research was done and checked

The polls were gathered on October 21, 2026, in five passes, one per group of pollsters, under the rules in `research/SPEC.md`: every figure from a document fetched in that session, a verbatim passage for every question, nothing from news coverage alone. The raw results of each pass are in `research/`.

Checks run before publishing:

1. **Against an already-verified file.** The Mamdani favorability and approval figures in nine polls (Siena January through September, Quinnipiac September and October, Marist April) were compared with the Mamdani poll tracker (https://vitalcity-nyc.github.io/mamdani-poll-tracker/), which was verified separately. Statewide and New York City figures matched in every case.
2. **Re-reading the sources.** Two questions were drawn at random from every poll (36 in all). The source documents were downloaded again and the quoted passage searched for. 33 were found word for word or as the same row of figures. The other three were on sites that refuse automated downloads; they were checked against the copies saved during research and against the live page, and all three matched.

## Reading the figures

- **Who was asked.** All adults, registered voters or likely voters, as the pollster describes the sample. Siena switched from registered to likely voters in August 2026; the charts say "registered voters or likely voters" when a line mixes both.
- **Asked of part of the sample.** Some questions went to only part of the sample, such as registered Democrats in a primary question. The row says so, and those rows are kept apart from questions put to everyone.
- **Kinds of question** are never combined: job approval, favorability, an excellent-to-poor grade, a matchup, support for a policy, and right track or wrong direction are different questions. Two pollsters asking about the state's direction in different ways (Siena's "right track" and Quinnipiac's "satisfied") are charted separately.
- **Totals and breakdowns.** Where a pollster printed "total approve" beside "strongly approve" and "somewhat approve," the bar shows the totals and the opened row shows the full breakdown.
- **Rounding.** Figures appear as published. Emerson's toplines carry one decimal (42.9) where its release rounds (43); Suffolk's marginals carry two (28.60). Results may not sum to 100.
- **"<1"** is shown as published and drawn as zero width.

## What the page calculates

- **Dot positions.** Each dot sits at the poll's last field date.
- **Lines in the charts** join readings of the same question, asked of the same group in the same place. Answers are matched across polls by label; candidates are matched by last name, because pollsters label them differently ("Democrat Kathy Hochul," "Kathy Hochul").
- **"Latest reading of each question only"** keeps, for each question, place and group, the reading with the latest last field date.
- **The buttons** under "Pick a person or an issue" gather rows by subject. A person's button collects every question about that person. An issue's button collects questions by topic and subject words (for example, "Taxes on the rich" collects questions whose subject mentions a millionaire tax, income tax, corporate tax or the pied-a-terre tax). The markets under a panel are those whose question names the person, or names New York and the issue.
- **Crime and health care buttons** cover New York only. They leave out immigration questions that merely mention crime or hospitals, and Marist's general question on whether gun control or gun rights should be the higher priority, which says nothing about New York.
- **Automatic buttons.** Any other subject that three or more independent polls have asked about gets its own button, so issues that keep coming up appear as polls are added.
- **"Where it ranks."** For crime, health care, the cost of living, housing, immigration, taxes and schools, the panel lists each question that asked people to pick the most important issue, with the share choosing that issue and its place among the answers. The place counts how many answers drew a larger share, leaving out "other," "don't know" and refusals; equal shares are called a tie. This ranking is the one calculation the page makes from published figures.
- **The opening sentence** names the latest statewide poll of the Hochul-Blakeman race asked of all respondents.

## Prediction markets

The market list loads live from the New York prediction markets tracker (https://joshgreenman1973.github.io/experiments/nyc-prediction-markets/), which reads the public data of Kalshi, Polymarket and Manifold every six hours; its own methodology explains which markets count as New York markets. If the live file can't be reached, the page falls back to `data/markets-snapshot.json`, saved when the page was last built. Prices are shown in cents on the dollar for yes. Nothing about the markets is recalculated here.

## Updating

Add a poll only after its primary release has been fetched and a verbatim passage recorded, in a new or existing file in `research/`, then run `python3 build.py`. The build checks for missing sources, quotes and categories, folds detailed versions of a question into their main row, and regenerates `data/polls.json`, `data/questions.csv`, `data/meta.json`, `data/gaps.json` and the market snapshot.
