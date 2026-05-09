# Research Institute Guideline: Book Research Methodology

## Using surf, AI-Assisted Web Research, and Structured Documentation

**Document Type:** Research Methodology Guideline  
**Version:** 1.0  
**Date:** 2026-04-10  
**Scope:** Library catalog enrichment, book summaries, research documentation  
**Tools:** surf (browser automation), ChatGPT, Kagi Assistant, jq, remarquee  

---

## Executive Summary

This guideline establishes a reproducible, traceable methodology for researching and documenting books in the Research Institute's library. The approach combines AI-assisted analysis with live web search to create comprehensive, citation-rich summaries that serve both immediate browsing needs and long-term scholarly integrity.

**Key Principles:**
1. **Traceability:** Every claim must be traceable to a specific source
2. **Verification:** Multiple independent sources consulted for major assertions
3. **Reproducibility:** Methods documented so any researcher can replicate
4. **Currency:** Balance classic text analysis with modern reception and discourse
5. **Accessibility:** Write for intelligent non-specialists while maintaining depth

---

## Table of Contents

1. [Pre-Research Phase](#phase-1-pre-research)
2. [Primary Source Analysis](#phase-2-primary-source-analysis)
3. [Secondary Source Research](#phase-3-secondary-source-research)
4. [Verification and Cross-Reference](#phase-4-verification)
5. [Synthesis and Writing](#phase-5-synthesis-and-writing)
6. [Citation and Documentation](#phase-6-citation)
7. [Quality Assurance](#phase-7-quality-assurance)
8. [Template and Structure](#appendix-a-template)
9. [Tool Reference](#appendix-b-tool-reference)
10. [Example Workflow](#appendix-c-example)

---

## Phase 1: Pre-Research

### 1.1 Book Selection and Initial Assessment

**Before beginning research, establish:**

| Checkpoint | Questions to Answer |
|------------|---------------------|
| **Significance** | Why does this book merit a detailed summary? Is it a classic, controversial, foundational, or particularly relevant to our research areas? |
| **Audience** | Who will read this summary? (General researchers, domain specialists, students, visiting scholars?) |
| **Availability** | Do we have access to the full text? (Physical copy on reMarkable, PDF, library access) |
| **Existing Coverage** | What summaries already exist? (Goodreads, academic reviews, publisher descriptions) |
| **Time Investment** | Estimate: 2-4 hours for comprehensive research and writing |

**Documentation:**
- Record book metadata: Title, author, publication date, edition, ISBN, reMarkable ID
- Note why this book was selected for summarization
- Identify 2-3 key questions the summary should answer

### 1.2 Tool Environment Setup

**Ensure access to:**

```bash
# Verify surf is available
which surf
surf --help

# Verify remarquee for reMarkable integration (if needed)
remarquee --help

# Verify jq for data processing
jq --version

# Set surf socket path (if using snap Chromium)
export SURF_SOCKET_PATH=/home/manuel/snap/chromium/common/surf-cli/surf.sock

# Verify socket connection
surf kagi-assistant --list-lenses
```

**Available surf lenses:**
- `Entire Web` - Broad search
- `Academic` - Scholarly papers, IEEE, ACM
- `News 360` - Recent articles, blogs, discussions
- `Programming` - Technical developer content
- `Small Web` - Independent blogs, personal sites
- `Forums` - Reddit, HN, Stack Exchange

---

## Phase 2: Primary Source Analysis

### 2.1 Direct Text Analysis (If Full Text Available)

**If you have the book on reMarkable or as PDF:**

1. **Download from reMarkable (if needed):**
   ```bash
   # Get book ID from catalog
   BOOK_ID=$(jq -r '.books[] | select(.title | test("Book Title")) | .id' books.json)
   
   # Download as rmdoc
   remarquee cloud get "$BOOK_ID" --output book.rmdoc
   ```

2. **Key sections to read/scan:**
   - Introduction/Preface (author's stated intent)
   - Table of contents (structure and scope)
   - First and last chapters (framing and conclusions)
   - Any chapters with famous concepts
   - Index (look for repeated concepts)

3. **Extract directly:**
   - 5-10 key quotes with page numbers
   - Core arguments in author's own words
   - Structure and organization

### 2.2 AI-Assisted Primary Analysis

**Use surf ChatGPT for initial comprehensive analysis:**

```bash
surf chatgpt "Write a detailed analysis of [BOOK TITLE] by [AUTHOR]. Include:
1. What the book is about (main thesis/argument)
2. Structure and organization (how it's laid out)
3. Key concepts and definitions (the author's own terminology)
4. Notable chapters or sections
5. The author's background and perspective
6. Target audience
7. Writing style and approach

Be thorough but focus on what the book actually says, not external interpretations."
```

**Review the AI output for:**
- Accuracy (does it match what you know about the book?)
- Completeness (did it miss major sections?)
- Bias (is it over-interpretive?)

**Save this as your "primary source baseline."**

---

## Phase 3: Secondary Source Research

### 3.1 Academic and Scholarly Sources

**Purpose:** Establish scholarly credibility, find academic reception, locate citations

```bash
# Academic lens for papers, IEEE, ACM
surf kagi-assistant "[Book Title] [Author] academic papers citations scholarly reception \
educational use university courses" \
  --lens "Academic" --web-search-mode on --prompt-timeout-sec 180
```

**Look for:**
- IEEE/ACM papers citing the book
- University course syllabi using the book
- Academic reviews in journals
- Dissertation references
- 20-year/anniversary retrospectives

**Extract and save:**
- Paper titles and DOIs
- Key findings about the book's impact
- How it's used in education
- Criticisms or limitations noted by scholars

### 3.2 Professional and Practitioner Sources

**Purpose:** Understand how the book is used in industry, current relevance

```bash
# News 360 lens for recent articles, blogs
surf kagi-assistant "[Book Title] [Author] software engineering 2024 2025 \
relevance modern teams lessons" \
  --lens "News 360" --web-search-mode on --prompt-timeout-sec 180
```

**Also search:**
```bash
# Programming lens for developer perspectives
surf kagi-assistant "[Book Title] lessons for engineers developers \
practical application" \
  --lens "Programming" --web-search-mode on --prompt-timeout-sec 180
```

**Look for:**
- Blog posts applying book concepts to modern problems
- "Lessons from [Book]" articles
- Conference talks referencing the book
- LinkedIn discussions
- Hacker News threads

### 3.3 Quote Verification and Collection

**Purpose:** Ensure accuracy of famous quotes, find authoritative sources

```bash
# Entire Web lens for comprehensive quote verification
surf kagi-assistant "Best quotes from [Book Title] by [Author] \
famous passages verified accurate" \
  --lens "Entire Web" --web-search-mode on --prompt-timeout-sec 120
```

**Cross-reference with:**
- Goodreads quotes collection (community-verified)
- Supersummary or similar study guides
- Publisher's excerpt pages
- Google Books preview (if available)

**For each quote, verify:**
- Exact wording
- Chapter/section location
- Context (not misattributed or paraphrased)

### 3.4 Historical and Biographical Context

**Purpose:** Understand when/why the book was written, author's background

```bash
# General search for historical context
surf kagi-assistant "[Author] biography background \
why wrote [Book Title] historical context \
what was happening in field at time" \
  --web-search-mode on --prompt-timeout-sec 120
```

**Look for:**
- Author's career and other works
- What prompted the book
- Historical events shaping the content
- Reception when first published vs. now

---

## Phase 4: Verification and Cross-Reference

### 4.1 The Verification Checklist

For every major claim in your summary, answer:

| Check | Standard | How to Verify |
|-------|----------|---------------|
| **Primary Source** | Claim appears in original text | Quote with chapter reference |
| **Secondary Validation** | Other sources confirm | Academic papers, reputable reviews |
| **Currency** | Claim still valid/relevant | Recent articles, practitioner discussions |
| **Attribution** | Ideas credited correctly | Check who originated concept vs. who popularized |
| **Context** | Not misrepresented | Read surrounding paragraphs in original |

### 4.2 Multi-Source Validation

**Critical concepts should have 2-3 independent sources:**

Example: "Brooks's Law states that adding manpower to a late project makes it later"
- ✅ Primary: Original text, Chapter 2
- ✅ Academic: IEEE Annals of the History of Computing, Vol. 18
- ✅ Practitioner: Modern LinkedIn discussions confirming relevance

**Red flags:**
- ❌ Only found in one blog post
- ❌ Can't locate in original text
- ❌ Contradicted by multiple academic sources
- ❌ Misattributed (actually from different author)

### 4.3 Discrepancy Resolution

**When sources disagree:**

1. **Check primary source first** - Author's own words trump interpretations
2. **Consider publication date** - Later editions may revise earlier claims
3. **Distinguish description vs. prescription** - Is the book describing what happens or recommending what to do?
4. **Note controversy** - If scholars debate the book's claims, present both sides
5. **Document uncertainty** - Use phrasing like "According to..." or "Some scholars argue..."

---

## Phase 5: Synthesis and Writing

### 5.1 Document Structure

**Standard Research Institute Book Summary Structure:**

```markdown
# [Book Title]: [Subtitle if any]

**Author:** [Full Name]  
**First Published:** [Year] (Edition notes)  
**Category:** [From our taxonomy]  
**Pages:** ~[Number]  
**Reading Time:** [Estimate]  
**Difficulty:** [Beginner/Intermediate/Advanced]

---

> [Lead quote - the most representative or famous passage]

---

## What This Book Is About
[2-3 paragraphs synthesizing the core thesis, scope, and significance]

## 🎯 Core Concepts
[3-5 major ideas, each with:
- Clear definition
- Why it matters
- Modern relevance
- INLINE CITATIONS to sources]

## 🔬 Recent Perspectives (if applicable)
[Academic and practitioner reception, 2020-2025]

## 📚 What You'll Learn
[By reader type: engineers, managers, researchers, etc.]

## 🏛️ Historical Context
[When written, why, author's background]

## ⭐ Why Read This [Current Year]?
[Enduring relevance case]

## 🎓 Who Should Read This?
[Target audiences with reasons]

## 📖 Reading Guide
[Key chapters, approach, time investment]

## 💡 Key Takeaways
[Bullet summary for skimmers]

## 🔄 Relationship to Modern Practices
[How concepts map to current methods]

## 📝 Notable Quotes
[Verified quotes with chapter refs and source notes]

## 🎬 Further Exploration
[Related books, concepts to explore]

## 📋 Practical Application
[Questions for readers to apply concepts]

## 🏆 Bottom Line
[Final verdict and rating]

## 📚 Book Details for Library Catalog
[Metadata, IDs, tags]

## References and Sources
[Numbered bibliography with URLs]

## Research Methodology Note
[How this summary was created]
```

### 5.2 Writing Guidelines

**For each section:**

1. **Lead with the claim, follow with the citation**
   - Good: "Brooks argues that conceptual integrity requires strong architectural leadership (Source: Original text, Chapter 17; IEEE retrospective analysis, 1995)."
   - Avoid: "According to some sources, Brooks thought..."

2. **Attribute specific claims**
   - Good: "Recent IEEE research confirms that communication overhead scales as n(n-1)/2 (Source: [specific paper with DOI])."
   - Avoid: "Studies show that..."

3. **Distinguish author from interpreters**
   - Good: "Brooks wrote... while modern practitioners interpret this as..."
   - Avoid conflating: "The book says [actually an interpreter's opinion]"

4. **Use synthesis, not serial summary**
   - Good: Organize by concept, pulling from multiple chapters
   - Avoid: Chapter-by-chapter summary

5. **Write for the browsing researcher**
   - Front-load significance (why this matters)
   - Use formatting for scannability (headers, bullets, callouts)
   - Include practical application (how to use this knowledge)

### 5.3 Inline Citation Format

**Standard format:**
```
Claim or quote (Source: [Primary source]; [Secondary verification])
```

**Examples:**

```markdown
- Brooks's Law states that "adding manpower to a late software project makes it later" 
  (Source: Original text, Chapter 2; Wikipedia - "Brooks's law", https://en.wikipedia.org/wiki/Brooks%27s_law)

- Communication paths grow as n(n-1)/2 where n is team size 
  (Source: Original text, Chapter 2 - the mathematical formulation; 
   verified in IEEE Annals of the History of Computing, Vol. 18, Issue 4, 1996)

- The book remains a foundational text in university curricula 
  (Source: University of Michigan EECS 481 course materials, 
   http://web.eecs.umich.edu/~weimerw/2018-481/readings/mythical-man-month.pdf;
   IEEE Software retrospective, 1995)
```

**Citation placement:**
- After specific claims or data points
- After direct quotes (always)
- After paraphrased arguments
- After assertions about reception, impact, or modern relevance

---

## Phase 6: Citation and Documentation

### 6.1 References Section Structure

Organize by category for readability:

```markdown
## References and Sources

### Primary Source
[The book itself, full bibliographic record]

### Academic and Scholarly Sources
[Numbered list of IEEE, ACM, university materials]

### Book Reviews and Reading Guides
[Goodreads, Supersummary, Blinkist, etc.]

### Professional and Industry Analysis
[Blog posts, practitioner articles, conference talks]

### Historical and Biographical Context
[Wikipedia, author biographies, publisher info]

### Video and Educational Content
[YouTube summaries, lecture recordings]

### Community Discussions
[Reddit, HN, forums with notable threads]

### Related Concepts and Extensions
[Modern applications, derivative works]
```

### 6.2 Reference Entry Format

**Standard format:**
```markdown
[N]. **Source Name - Article/Document Title**
    - Brief description of what it contains
    - URL
    - Date accessed (if relevant)
    - *Note: Any special context*
```

**Example:**
```markdown
3. **Mathematical Modeling of Brooks's Law**
   - "A Mathematical Model for Explaining the Mythic Man-Month"
   - IEEE Conference Publication, DOI: 10.1109/ICESS.2008.25
   - https://ieeexplore.ieee.org/abstract/document/4054985
   - *Presents collaborative work theory and mathematical models*
```

### 6.3 Research Methodology Note

**Always include at the end:**

```markdown
## Research Methodology Note

This summary was created using a hybrid AI + web research approach:

1. **AI Analysis (ChatGPT via surf):** [What it provided]
2. **Academic Search (Kagi Assistant - Academic lens):** [What was found]
3. **Current Discourse (Kagi Assistant - News 360 lens):** [What was found]
4. **Quote Verification (Kagi Assistant - Entire Web lens):** [How quotes were verified]
5. **Cross-Reference Validation:** [How multi-source verification was done]

**Confidence Level:** [High/Medium/Low] - [Justification]
**Last Updated:** [Date]
**Researcher:** [Name/Initials if desired]
```

---

## Phase 7: Quality Assurance

### 7.1 Pre-Publication Checklist

Before saving to the library:

- [ ] **Traceability:** Can every major claim be traced to a source?
- [ ] **Quote Accuracy:** Are all quotes verified against primary or authoritative secondary sources?
- [ ] **Citation Completeness:** Are there 30+ sources for comprehensive summaries?
- [ ] **URL Functionality:** Are all links formatted correctly (not broken in Markdown)?
- [ ] **Balance:** Is there representation from academic, practitioner, and historical sources?
- [ ] **Currency:** Are there sources from 2020-2025 showing current relevance?
- [ ] **Accessibility:** Is the writing clear for non-specialists while maintaining depth?
- [ ] **Objectivity:** Are controversial aspects presented fairly?
- [ ] **Practical Value:** Would a browsing researcher find this useful for deciding whether to read the book?

### 7.2 Peer Review (Optional but Recommended)

**If domain expert available:**
- Have them check concept explanations for accuracy
- Verify that modern relevance claims are valid
- Suggest any missing perspectives

**Self-review questions:**
- Would I recommend this summary to a colleague?
- Does it fairly represent the book's strengths and limitations?
- Are there any claims I wouldn't feel confident defending?

### 7.3 Version Control

**Save with naming convention:**
```
SUMMARY - [Book Title] - [Author Last Name].md
```

**If updating later:**
- Add update note to methodology section
- Note what was added/changed
- Update "Last Updated" date

---

## Appendix A: Template

See the accompanying template file: `TEMPLATE - Book Summary.md`

(Full template structure provided in Section 5.1 above)

---

## Appendix B: Tool Reference

### surf Commands Quick Reference

```bash
# Setup
export SURF_SOCKET_PATH=/home/manuel/snap/chromium/common/surf-cli/surf.sock

# ChatGPT for comprehensive analysis
surf chatgpt "[Detailed prompt]" --timeout 180

# Kagi Assistant with different lenses
surf kagi-assistant "[Query]" --lens "Academic" --web-search-mode on
surf kagi-assistant "[Query]" --lens "News 360" --web-search-mode on
surf kagi-assistant "[Query]" --lens "Entire Web" --web-search-mode on
surf kagi-assistant "[Query]" --lens "Programming" --web-search-mode on

# List available options
surf kagi-assistant --list-lenses
surf kagi-assistant --list-models

# Browser navigation (if needed)
surf navigate --url "[URL]"
surf wait dom
```

### remarquee Commands (for reMarkable integration)

```bash
# Get book ID from catalog
BOOK_ID=$(jq -r '.books[] | select(.title | test("Book Title")) | .id' books.json)

# Download book
remarquee cloud get "$BOOK_ID" --output book.rmdoc

# List books on device
remarquee cloud ls /Books --with-glaze-output --output json
```

### jq Commands (for data processing)

```bash
# Extract specific fields from catalog
jq '.books[] | {title: .title, author: .author, id: .id}' books.json

# Filter by category
jq '.books[] | select(.category == "Software Engineering")' books.json

# Count books with IDs
jq '[.books[] | select(.id != null)] | length' books.json
```

---

## Appendix C: Example Workflow

### Complete Research Session: "The Mythical Man-Month"

**Total Time:** ~90 minutes
**Researcher:** AI-assisted (kimi-k2p5) with human oversight
**Output:** 643-line comprehensive summary with 41 inline citations and 32 references

#### Step-by-Step Log:

**Phase 1: Setup (5 min)**
```bash
# Verified surf connection
export SURF_SOCKET_PATH=/home/manuel/snap/chromium/common/surf-cli/surf.sock
surf kagi-assistant --list-lenses
# Result: Confirmed Academic, News 360, Entire Web, Programming lenses available
```

**Phase 2: Primary Analysis (15 min)**
```bash
surf chatgpt "Write a comprehensive library summary of 'The Mythical Man-Month' 
by Frederick Brooks... [full prompt]"
# Result: 800+ word analysis with historical context, key concepts, structure
# Saved as primary_source_analysis.txt
```

**Phase 3: Academic Research (20 min)**
```bash
surf kagi-assistant "What does recent academic literature say about the 
continuing relevance of The Mythical Man-Month..." --lens "Academic" --web-search-mode on
# Result: 10 IEEE/ACM sources, educational use confirmation, mathematical modeling papers

surf kagi-assistant "IEEE papers citing Brooks's Law communication overhead 
software teams" --lens "Academic" --web-search-mode on
# Result: Specific DOIs for verification
```

**Phase 4: Modern Reception (15 min)**
```bash
surf kagi-assistant "Recent articles discussions Mythical Man-Month 
Brooks's Law 2024 2025" --lens "News 360" --web-search-mode on
# Result: LinkedIn discussions, blog posts, practitioner perspectives

surf kagi-assistant "Best quotes passages Mythical Man-Month verified" 
--lens "Entire Web" --web-search-mode on
# Result: Goodreads collection, Supersummary guide, verified quotes
```

**Phase 5: Verification (10 min)**
- Cross-checked ChatGPT output against Kagi results
- Verified quotes against Goodreads authoritative collection
- Confirmed all major claims had 2-3 source support

**Phase 6: Writing (20 min)**
- Used structured template
- Added inline citations as wrote
- Organized references by category
- Included methodology note

**Phase 7: Quality Check (5 min)**
- Verified 31 reference URLs present
- Checked 41 inline citations added
- Confirmed all quotes sourced
- Validated Markdown formatting

**Final Output:**
- Document: 643 lines, 29KB
- Citations: 41 inline, 32 bibliographic
- Sources: IEEE, ACM, university materials, practitioner blogs, community discussions
- Coverage: Primary text, academic reception, modern relevance, quote verification

---

## Best Practices Summary

### Do:
- ✅ Cite primary source (the book) for all core concepts
- ✅ Add secondary verification for every major claim
- ✅ Include recent sources (2020-2025) showing current relevance
- ✅ Verify quotes against authoritative collections
- ✅ Write for the intelligent non-specialist
- ✅ Document your methodology
- ✅ Use consistent citation format

### Don't:
- ❌ Rely solely on AI-generated content without verification
- ❌ Include claims you can't trace to a source
- ❌ Paraphrase without noting it's a paraphrase
- ❌ Use only one type of source (mix academic + practitioner)
- ❌ Skip the methodology note
- ❌ Leave quotes unattributed
- ❌ Ignore contradictory sources (address them)

---

## Conclusion

This methodology produces book summaries that are:
- **Trustworthy:** Every claim traceable to sources
- **Useful:** Help researchers decide whether to invest time in the book
- **Durable:** Stand up to scrutiny and remain useful over time
- **Reproducible:** Any researcher can follow the same process
- **Respectful:** Fairly represent the author's work and ongoing discourse

**Questions or improvements to this guideline?**
Contact the Research Institute documentation team or submit updates via the standard review process.

---

**Document Control:**
- Created: 2026-04-10
- Author: Research Institute AI-assisted research methodology working group
- Review Cycle: Annual or as tools/methods evolve
- Next Review: 2027-04-10
