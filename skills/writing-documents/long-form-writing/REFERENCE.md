# Writing process reference

Read §1 before fragments mode, §2-3 before shape or beats mode, §4 when choosing the form of a block, §5-6 before editing or reviewing, and §7 for what `prose_lint.py` flags.

## 1. Fragments mode (explore)

**Goal:** widen what could be written. Don't commit to structure: no outline, no sections, no order beyond arrival order.

**Interview hard.** Ask follow-ups that pull out specifics:
- "What actually happened?"
- "What number would prove that?"
- "Who said it, and in what words?"
- "What would a sceptic say?"
- "What annoys you about how people usually explain this?"
- "Finish this sentence: the thing nobody admits is…"

Capture from the very first message, including the request itself.

**What counts as a fragment.** Keep anything with a chance of reaching the finished piece. It only has to make sense to the author, not to a stranger. Typical catches: a line that sounds right but has no slot yet; an assertion plus the single reason behind it; a story, an example, a snippet of code or a comparison; an unfinished hunch the author wants to come back to; something somebody said, word for word; a few loosely related observations that feel like they belong together; a gripe, an admission or a joke; and, above all, a **leading word**.

**The leading word** is the most valuable fragment. It's a short coinage or metaphor that names the central idea (in the worked example, *gate debt*: checks that outlived their reason). Once named, it shapes the title, the transitions and what gets cut. When the conversation keeps circling an idea, stop and try three or four names with the user.

**File rules** (`scripts/fragments.py` enforces them; see templates/fragments-file.md):
- The file starts with a provisional title as its only H1. Nothing else goes above the fragments: no front matter, contents list or date.
- Fragments are separated by a line containing only `---`. No headings in the body, no tags.
- **Append only.** Re-read the file from disk before every write, because the user may have edited, reordered or deleted things. `fragments.py add` appends to whatever is on disk.
- Edit or cut a specific fragment only when the user asks ("cut the last one", "sharpen that", "merge those two"). Treat those as first-class instructions.
- Append without asking each time. Mention it in passing ("adding that") and keep the conversation moving.
- If no path was given, ask once where to save it, then reuse that path for the session.

**Exit:** the user says the pile is done, or they ask to start writing. More raw material than you need is the point; most of it won't make the cut.

## 2. Grounding

A **concept** is grounded once the reader has it, either because:
- they walked in with it (a **prerequisite**, fixed before the first block), or
- an earlier block **introduced** it (grounded for every later block).

Each block **requires** grounded concepts and **grounds** new ones. The unit is the idea, not the word: a block can lean on an idea the reader lacks even without jargon. When a concept has a name, ground the idea and the term together.

- Keep the ledger: `ledger.py init --prereq …`, then `ledger.py land "<summary>" --requires … --grounds …` after each block lands. `land` refuses a block that needs something ungrounded.
- If a tempting block needs an ungrounded concept, there are two fixes. Add a grounding block first, or promote the concept to a prerequisite (`ledger.py promote`), which narrows the audience. Decide which with the user.
- The trade-off: require too much up front and you shut readers out; ground too much inside and the opening drowns in definitions.
- If the user rewrites or deletes a landed block, update the ledger (`ledger.py undo`, then re-land).

## 3. Shape mode vs beats mode

Both modes **exploit** a fixed pile. They read it end to end first, write to a *separate* article file, treat the pile as **read-only**, and keep the grounding ledger.

| | Shape mode | Beats mode |
|---|---|---|
| Unit | paragraph or block (paragraph, list, table, callout, quote, code) | beat: one move (set a scene, land a point, ask, aside, twist), from one sentence to a self-contained vignette |
| Start | settle prerequisites → 2-3 **candidate openings**, each implying a different thesis; the user picks or composes a hybrid | settle prerequisites → 2-3 **candidate starting beats**, each a different entry point, each noting what it grounds; preview what each pick unlocks |
| Loop | "Given what's written, what does the reader need next?" Pull from the pile, argue the form (§4), append once agreed | Write only the picked beat, stop, re-read from disk, then offer 2-3 reachable next beats with what each grounds (templates/beats-menu.md) |
| Feel | an editor pushing back: weak transitions don't slide, paragraphs must earn their place | choose-your-own-adventure: the user steers every pivot |
| Ends | when the user says it's done | at the natural end of the journey, not when the pile runs out |

**Shared rules**
- **Load the article fresh before each write**, since the user may have touched it. Their edits always win, and a rewrite of theirs can redirect what you write next.
- **Add text only once it is agreed**, one block or beat per write; no drafting ahead and no bundling several into one write.
- **Rewrites happen in place.** "Redo beat 3" means edit that beat and leave the rest alone.
- **The pile is a quarry.** Split, merge, paraphrase or quote fragments so the article reads in one voice.
- **Say when the pile runs dry.** Tell the user exactly what is missing ("this section needs a real incident and there isn't one here") and let them supply it or drop the section. Never fill the hole with made-up stories, figures or quotes.
- **Oversized units.** A beat that needs five paragraphs and subheadings is two beats; split it. A paragraph doing two jobs gets split or trimmed.
- **Out of scope:** editing the pile, publishing, platform formatting, or frontmatter nobody asked for.

**Challenges for shape mode**: the template lists five (redundancy, load-bearing, form, overloaded sentence, drift); raise them whenever a block lands too easily.

## 4. Choosing the form of a block (argue it out loud)

| Choice | Use the first when… | Use the second when… |
|---|---|---|
| Prose vs list | it carries an argument, with causes, contrasts and because | items are truly parallel and the reader scans |
| Inline vs callout (`> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`) | the aside belongs to the argument | it would derail the main line and a reader can skip it |
| Table vs repeated prose | the same 3+ fields repeat 3+ times | fewer repeats, or the fields differ |
| Quote vs paraphrase | the reader needs the speaker's own phrasing | you are borrowing the point, not the voice |
| Fenced block vs inline code | several lines, or something the reader will copy and run | one name, flag or value inside a sentence |
| Heading vs bold lead-in | the reader navigates to it | it's a label inside a section |
| Diagram vs prose | there are 4+ parts with relationships (see system-diagrams) | it's a sequence a sentence can carry |

## 5. Default style rules (override with templates/style-guide.md)

**Clarity**
- One idea per paragraph, with the topic sentence first.
- The key claim goes in a short sentence.
- Keep the subject and verb close together and early.

**Concision**
- Cut warm-ups ("In this article we'll…"), signposts ("It's worth noting"), recaps ("In conclusion…") and filler (basically, actually, in order to).

**Concreteness**
- Use numbers, names, examples and the specific case before the general rule.
- Replace "significant" with the figure.

**Commitment**
- Hedge only where you are genuinely unsure, and then say what you're unsure of.
- No weasel sources ("many experts say").

**Verbs**
- Use the active voice, with the actor named.
- Prefer verbs to nominalisations ("decide", not "make a decision").

**Voice**
- Keep the author's register, person and tense consistent.
- Edits should sound like the author on a good day, not like you.

**Assistant tells to avoid**
- Stock words: delve, tapestry, landscape, seamless, robust, leverage, unlock, elevate, testament to.
- Patterns:
  - "not just X, it's Y";
  - triads of adjectives;
  - em dashes everywhere;
  - every paragraph closing on a moral;
  - rhetorical questions as transitions;
  - "Here's the thing:";
  - emoji bullets.

**Structure**
- Use descriptive headings with one case style throughout, lists for parallel items, and tables for repeated fields.
- Link text says where the link goes; never "click here".

**Accuracy**
- Check every fact, number and quote against the source. Open every link.
- Any claim the author can't back gets softened or cut.

## 6. Reviewing prose (yours or someone else's)

1. Read the whole piece once before commenting. Write down the takeaway in one sentence. If you can't, that's the first finding (structure).
2. Run `prose_lint.py <files>` and triage:
   - every `fix` is must-fix;
   - each `style` finding is usually worth changing;
   - `note` findings are judgement calls. Drop those that don't apply to this author.
3. Check the structure: does the opening earn attention, and does the end deliver what it promised? Is every concept grounded before use? Are there sections that could go without loss?
4. Write the report with templates/edit-report.md:
   - Must fix (errors, unclear or unsupported claims, broken links), then Structure, then Style.
   - Give the location, the problem and a concrete rewrite for each.
   - Include the "Kept on purpose" list.
5. Preserve the voice. Don't rewrite whole paragraphs in your style. If you're asked to apply edits, make the smallest change that fixes each issue, then re-run the lint.

Fix structure before sentences: polishing paragraphs in a structure that doesn't work wastes the polish.

## 7. prose_lint.py rules

| Rule | Severity | Flags |
|---|---|---|
| doubled | fix | "the the" (allows "had had", "that that") |
| placeholder | fix | TODO, TK, TBD, FIXME, XXX, lorem ipsum, `[insert…]`, `[citation needed]` |
| click-here | fix | link text "here", "click here", "this link" |
| filler | style | basically, actually, just, in order to, due to the fact that, it's important to note that… (with replacement) |
| ai-phrase | style | ~70 stock words and phrases (delve, landscape, seamless, leverage, moreover…) with plain replacements |
| nominal | style | made a decision, give consideration to, conduct an investigation… (all tenses) |
| weasel | style | many people say, studies show, experts agree… |
| throat-clear | style | a paragraph opening with "In this article we'll…", "Let's dive…", "Have you ever wondered…" |
| empty-close | style | In conclusion / To sum up / Ultimately, / Overall, |
| not-x-but-y | style | "it's not just X, it's Y", "not only X but Y", "less about X and more about Y" |
| long-sentence | style | over `--max-words` (default 30) |
| em-dash | style | 2+ dashes on a line, or over `--dash-per-1k` (default 4) per 1000 words |
| hedge, intensifier | note | perhaps, arguably, sort of…; very, extremely, truly + word |
| passive | note | be + past participle (common adjectives excluded); ask who acts |
| triad | note | "a fast, cheap, and reliable…" |
| sentence-start | note | 3+ sentences in a row with the same first word |
| heading-case | note | headings that mix Title Case and sentence case |
| repeat-word | note | the same 6+ letter word twice within 12 words |
| exclaim | note | exclamation marks in prose |

Skipped: frontmatter, fenced and indented code, inline code, URLs, HTML comments, table separators. Output format: `path:line:col: severity rule: message [suggestion]`. Use `--only`/`--skip` to pick rules, `--json` for tools, and `--strict` to exit 1 on any finding (CI). The heuristics are deliberately simple; a finding is a prompt to look, not a verdict.
