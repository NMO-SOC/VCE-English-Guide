# Graph Report - .  (2026-08-07)

## Corpus Check
- Large corpus: 404 files · ~1,534,821 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 680 nodes · 1110 edges · 34 communities (27 shown, 7 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 141 edges (avg confidence: 0.77)
- Token cost: 1,454,683 input · 0 output

## Community Hubs (Navigation)
- VCE Study Design & Assessment Overview
- Sunset Boulevard Themes & Prompt Types
- Rainbow's End Historical Context
- Persuasive Techniques Reference
- Sunset Boulevard Film Techniques
- Exam Structure & Text List
- VCE Prescribed Text List
- site.js Utility Functions
- 2024 Sample Exam Stimuli
- Rhetorical & Structural Devices
- Creating Texts Framework
- Language & Word Choice Techniques
- Appeals to Values (Persuasion)
- Rhetorical Devices (Practice Copy)
- Appeals to Values (Practice Copy)
- Visual Language Analysis
- Visual Language Analysis (Copy)
- Study Skills & Habits
- build.py Site Generator
- Section C Persuasive Text Analysis
- Logical Fallacies
- Persuasive Techniques (Practice Exam)
- Site Infrastructure & AI Tools
- Evidence & Support Techniques
- Tone Techniques
- Deployment Pipelines
- AI Provider Config
- Exam Tab Switching
- Criteria Accordion Toggle
- Feedback Filter Toggle
- Theme Toggle
- 404 Page

## God Nodes (most connected - your core abstractions)
1. `Week-by-Week Revision Program` - 26 edges
2. `Rhetorical and Structural Devices` - 24 edges
3. `Rhetorical and Structural Devices` - 24 edges
4. `Language and Word Choice` - 21 edges
5. `Language and Word Choice` - 21 edges
6. `Section A: Analytical Response to a Text` - 21 edges
7. `Section A: Analytical Response to a Text` - 21 edges
8. `Rainbow's End (Part 03 hub)` - 18 edges
9. `Appeals to Emotion and Values` - 18 edges
10. `Appeals to Emotion and Values` - 18 edges

## Surprising Connections (you probably didn't know these)
- `High-Scoring Vocabulary Bank (public page)` --semantically_similar_to--> `Sentence Starters and Linking Words Table`  [INFERRED] [semantically similar]
  public/vocabulary.html → snippets/ss.html
- `Deploy site to GitHub Pages (workflow)` --semantically_similar_to--> `GitLab Pages job`  [INFERRED] [semantically similar]
  .github/workflows/pages.yml → .gitlab-ci.yml
- `Sunset Boulevard Shot Analysis Table` --shares_data_with--> `Film Techniques (Sunset Boulevard)`  [INFERRED]
  snippets/shotanalysis.html → public/p02-film-techniques.html
- `VCE English Exam Preparation Guide — Website (project)` --conceptually_related_to--> `VCE English Exam Prep Guide (site)`  [INFERRED]
  README.md → HANDOVER.md
- `Section C - Analysis of argument and language` --conceptually_related_to--> `buildC() — Section C marking prompt builder`  [INFERRED]
  graphify-out/converted/Exam Template_7aba19ce.md → marker-source.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **VCE English exam's three-section + assessment-criteria structure** — graphify_out_converted_exam_template_7aba19ce_section_a, graphify_out_converted_exam_template_7aba19ce_section_b, graphify_out_converted_exam_template_7aba19ce_section_c, graphify_out_converted_exam_template_7aba19ce_assessment_criteria [EXTRACTED 1.00]
- **Section prompt builders sharing a common calibration fragment** — marker_source_builda, marker_source_buildb, marker_source_buildc, marker_source_calib [EXTRACTED 1.00]
- **Essay Marker's pluggable AI backend (dispatch + two providers)** — marker_source_askai, handover_anthropic_api, marker_source_github_models_api [EXTRACTED 1.00]
- **Sunset Boulevard central relationship web (Joe, Norma, Max, Betty)** — joe_gillis, norma_desmond, max_von_mayerling, betty_schaefer [EXTRACTED 0.95]
- **Three generations of Aboriginal women in Rainbow's End (Nan Dear, Gladys, Dolly)** — gladys_character, dolly_character, nan_dear_character [EXTRACTED 0.95]
- **Site tools dependent on external services/libraries (Ask Max worker, Essay Marker API, JSZip)** — public_ask_max_worker, public_marker, jszip_library [INFERRED 0.85]
- **Rainbow's End Central Character Ensemble Analysis** — nan_dear, gladys_banks, dolly_banks, errol_fisher, papa_dear [INFERRED 0.85]
- **Part 04 Essay-Writing Instructional Pipeline** — public_p04_introduction, public_p04_what_is_needed_in_an_essay, public_p04_planning, public_p04_analytical_text_response_structure, public_p04_proofreading [EXTRACTED 1.00]
- **Symbols of Colonial Oppression in Rainbow's End** — symbol_encyclopedias, symbol_hessian, symbol_the_humpy, theme_race_and_racism, rumbalara [INFERRED 0.80]
- **VCE English Exam Three-Section Structure (A/B/C, 20 marks each)** — public_p07_exam_format, public_p07_exam_format_section_a, public_p07_exam_format_section_b, public_p07_exam_format_section_c [EXTRACTED 1.00]
- **Section C Practice and Assessment Ecosystem** — public_p06_sample_analysing_argument_essays, public_p06_section_c_from_previous_exams, public_p09_section_c_mark_allocation, public_p10_general_checklist_for_section_c_response, public_p07_strategies_for_addressing_the_requirements [INFERRED 0.85]
- **Effective Study Techniques Toolkit (Part 13 chapter)** — public_p12_assess_your_current_study_habits, public_p12_create_a_personalised_study_schedule, public_p12_implement_active_recall_and_spaced_repetition, public_p12_develop_a_healthy_study_life_balance, public_p12_collaborate_with_study_groups, public_p12_fine_tune_your_exam_day_strategy [INFERRED 0.75]
- **Effectively Studying For Exams chapter chain (hub + sub-pages + revision program)** — public_part_12_effectively_studying_for_exams, public_p12_organise_your_study_materials, public_p12_seek_help_when_needed, public_p12_utilise_practice_exams_and_past_papers, public_revision_program [INFERRED 0.85]
- **Prompt-type worked examples built on Sunset Boulevard characters** — public_prompt_types, concept_norma_desmond, concept_joe_gillis, concept_sunset_boulevard_text [EXTRACTED 1.00]
- **2025 Assessment Report section chain (hub + General/A/B/C + checklist)** — public_part_13_key_takeaways_from_the_2025_assessment_report, public_r25_general, public_r25_section_a, public_r25_section_b, public_r25_section_c, public_r25_checklist [EXTRACTED 1.00]
- **Rainbow's End Analytical Toolkit (Quotes, Symbols, Devices)** — snippets_quotetable, snippets_symboltable, snippets_tracker [INFERRED 0.80]
- **VCE Prompt-Type Analysis Method (Discuss/Extent/Agree/How Does)** — snippets_prompt_types, snippets_prompt_types_re, concept_argument_evidence_technique_effect, concept_four_prompt_types [INFERRED 0.85]
- **2025 Assessment Report Chapter Cluster** — snippets_r25_hub, snippets_r25_general, snippets_r25_section_a, snippets_r25_section_b, snippets_r25_section_c, snippets_r25_checklist, snippets_report2025 [INFERRED 0.85]
- **VCE Section C: analysing an unseen persuasive text against a shared technique taxonomy** — localpdf_practice_exam_ix_section_c, localpdf_practice_exam_viii_section_c, localpdf_persuasive_techniques_reference [INFERRED 0.85]
- **Shared VCE English set-text list curated independently across two trial exam publishers** — localpdf_practice_exam_ix_section_a, localpdf_practice_exam_viii_section_a, localpdf_practice_exam_ix_we_have_always_lived_in_the_castle, localpdf_practice_exam_viii_we_have_always_lived_in_the_castle [INFERRED 0.75]

## Communities (34 total, 7 thin omitted)

### Community 0 - "VCE Study Design & Assessment Overview"
Cohesion: 0.06
Nodes (66): Framework of Ideas (Section B), VCAA (Victorian Curriculum and Assessment Authority), VCAA 2024 English Assessment Report, VCAA 2025 English Examination Report, VCE English and EAL Study Design 2024–2027, VCE English Exam Preparation Guide (homepage), Analysing Visual Language, Analysing Written Language (+58 more)

### Community 1 - "Sunset Boulevard Themes & Prompt Types"
Cohesion: 0.06
Nodes (61): Rationale: Ask Max worker deployment gating (origin allowlist + school web filter blocks workers.dev), Colonisation and Segregation (historical context), Joe Gillis (character, Sunset Boulevard), Norma Desmond (character, Sunset Boulevard), 'Discuss' prompt type, 'Do you agree?' prompt type, 'How does…' prompt type, 'To what extent do you agree?' prompt type (+53 more)

### Community 2 - "Rainbow's End Historical Context"
Cohesion: 0.07
Nodes (60): Assimilation Policy (1950s Australia), Bank Manager, Cummeragunja (Aboriginal settlement), Dolly Banks, Errol Fisher, Ester, Gladys Banks, Jane Harrison (playwright) (+52 more)

### Community 3 - "Persuasive Techniques Reference"
Cohesion: 0.04
Nodes (48): Analysing Argument: Persuasive Techniques (VCE Reference Table), Allusion, Attack / ad hominem, Bandwagon, Evidence and Support, Language and Word Choice, Reasoning, Logic and Logical Fallacies, Tone (+40 more)

### Community 4 - "Sunset Boulevard Film Techniques"
Cohesion: 0.10
Nodes (47): America in the 1950s, Artie Green, Betty Schaefer, Cecil B. deMille, Chiaroscuro (film technique), Close-up Shot (film technique), Fame and Obsession (theme), Film Noir (+39 more)

### Community 5 - "Exam Structure & Text List"
Cohesion: 0.07
Nodes (45): Assessment criteria (Sections A/B/C), Exam Template.docx — VCE Practice Examination Task Book (converted), Framework 3: Writing about personal journeys, Rainbow's End, by Jane Harrison (Text list), Section A - Analytical response to a text, Section B - Creating a text, Section C - Analysis of argument and language, South Oakleigh College (+37 more)

### Community 6 - "VCE Prescribed Text List"
Cohesion: 0.06
Nodes (42): Bad Dreams and Other Stories by Tessa Hadley, Born a Crime by Trevor Noah, Chronicle of a Death Foretold by Gabriel García Márquez, False Claims of Colonial Thieves by Charmaine Papertalk Greene and John Kinsella, Flames by Robbie Arnott, Go, Went, Gone by Jenny Erpenbeck, High Ground by Stephen Johnson, Much Ado About Nothing by William Shakespeare (+34 more)

### Community 7 - "site.js Utility Functions"
Cohesion: 0.11
Nodes (31): esc(), load(), pad(), run(), tick(), A(), c(), d() (+23 more)

### Community 8 - "2024 Sample Exam Stimuli"
Cohesion: 0.08
Nodes (24): 2024 VATE English Sample Exam, Carl Sagan, Ehsan Sehgal, Elie Wiesel, Framework: Every voice is important, Framework: Let the journey begin, Libba Bray, Michael Rosen (+16 more)

### Community 9 - "Rhetorical & Structural Devices"
Cohesion: 0.08
Nodes (24): Alliteration, Analogy, Anaphora, Anecdote, Antithesis, Call to action, Rhetorical and Structural Devices, Climactic ordering (+16 more)

### Community 10 - "Creating Texts Framework"
Cohesion: 0.18
Nodes (23): VCAA 2025 English Examination Report, Argument -> Evidence -> Technique -> Effect Paragraph Structure, Four VCE Prompt Types (Discuss / To What Extent / Do You Agree / How Does), Th.E.S.A.M.L. Paragraph Method, Audience (Creating Texts), Personal Journeys, Practice Stimuli, Purpose (Creating Texts) (+15 more)

### Community 11 - "Language & Word Choice Techniques"
Cohesion: 0.11
Nodes (18): Language and Word Choice, Cliche, Colloquial language, Connotation, Dysphemism, Euphemism, Exclusive language, Formal register and technical jargon (+10 more)

### Community 12 - "Appeals to Values (Persuasion)"
Cohesion: 0.11
Nodes (18): Appeal to authority / expert opinion, Appeal to common sense, Appeal to family values, Appeal to fear, Appeal to freedom and individual rights, Appeal to group loyalty / belonging, Appeal to guilt or shame, Appeal to hope / optimism (+10 more)

### Community 13 - "Rhetorical Devices (Practice Copy)"
Cohesion: 0.12
Nodes (17): Alliteration, Anaphora, Anecdote, Antithesis, Rhetorical and Structural Devices, Climactic ordering, Extended metaphor, Framing / defining the issue (+9 more)

### Community 14 - "Appeals to Values (Practice Copy)"
Cohesion: 0.12
Nodes (16): Appeal to authority / expert opinion, Appeal to common sense, Appeal to fear, Appeal to freedom and individual rights, Appeal to group loyalty / belonging, Appeal to guilt or shame, Appeal to hope / optimism, Appeal to justice and fairness (+8 more)

### Community 15 - "Visual Language Analysis"
Cohesion: 0.13
Nodes (15): Caption, Caricature and exaggeration, Visual Language, Colour, Facial expression and body language, Gaze and vectors, Graphs and infographics, Labelling in cartoons (+7 more)

### Community 16 - "Visual Language Analysis (Copy)"
Cohesion: 0.13
Nodes (15): Caption, Caricature and exaggeration, Visual Language, Colour, Facial expression and body language, Gaze and vectors, Graphs and infographics, Labelling in cartoons (+7 more)

### Community 17 - "Study Skills & Habits"
Cohesion: 0.25
Nodes (14): Assess your current study habits, SMART Goals, Collaborate with study groups, Create a personalised study schedule, Develop a healthy study-life balance, Pomodoro Method, Fine-tune your exam day strategy, Implement active recall and spaced repetition (+6 more)

### Community 18 - "build.py Site Generator"
Cohesion: 0.19
Nodes (5): _clean(), fix_quotes(), _heading_chain(), nav_html(), shell()

### Community 19 - "Section C Persuasive Text Analysis"
Cohesion: 0.15
Nodes (13): Allusion, Concession, Emotive language, High modality, Rebuttal, Ayla Adamu, Banksy, Colman Arts Society (+5 more)

### Community 20 - "Logical Fallacies"
Cohesion: 0.17
Nodes (12): Attack / ad hominem, Bandwagon, Reasoning, Logic and Logical Fallacies, Circular reasoning, False dichotomy (either-or), Generalisation, Logical reasoning / cause and effect, Post hoc reasoning (+4 more)

### Community 21 - "Persuasive Techniques (Practice Exam)"
Cohesion: 0.18
Nodes (11): Analogy, Appeal to family values, Appeal to the hip-pocket nerve, Call to action, Headline and opening hook, Repetition, Rhetorical question, Bill Davies (+3 more)

### Community 22 - "Site Infrastructure & AI Tools"
Cohesion: 0.22
Nodes (10): Ask Max (AI assistant), LaTeX/Python build pipeline, Cloudflare Worker API (jolly-waterfall-d01a.nicholas-morlin.workers.dev), assets/embeddings.json (Ask Max retrieval index), Exam Generator, GoatCounter (nmo.goatcounter.com) — anonymous page-view counts, fonts.googleapis.com / gstatic.com (typefaces), JSZip library (bundled locally in assets/vendor/) (+2 more)

### Community 23 - "Evidence & Support Techniques"
Cohesion: 0.22
Nodes (9): Evidence and Support, Comparison to other jurisdictions, Expert testimony, Eyewitness or vox pop quotation, Historical precedent, Official documentation, Personal experience and credentials, Research and studies (+1 more)

### Community 24 - "Tone Techniques"
Cohesion: 0.33
Nodes (6): Analysing Argument: Persuasive Techniques (VCE Reference Table), Tone, Outraged / indignant tone, Reasonable / conciliatory tone, Tone, Tone shift

## Knowledge Gaps
- **289 isolated node(s):** `Deploy site to GitHub Pages (workflow)`, `GitLab Pages job`, `JSZip library (bundled locally in assets/vendor/)`, `Cloudflare Worker API (jolly-waterfall-d01a.nicholas-morlin.workers.dev)`, `GoatCounter (nmo.goatcounter.com) — anonymous page-view counts` (+284 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Week-by-Week Revision Program` connect `Sunset Boulevard Themes & Prompt Types` to `VCE Study Design & Assessment Overview`, `Rainbow's End Historical Context`, `Sunset Boulevard Film Techniques`, `Creating Texts Framework`, `Study Skills & Habits`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `Rainbow's End (Part 03 hub)` connect `Rainbow's End Historical Context` to `VCE Study Design & Assessment Overview`, `Sunset Boulevard Themes & Prompt Types`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `Analysing Argument: Persuasive Techniques (VCE Reference Table)` connect `Tone Techniques` to `Language & Word Choice Techniques`, `Rhetorical Devices (Practice Copy)`, `Appeals to Values (Practice Copy)`, `Visual Language Analysis`, `Logical Fallacies`, `Evidence & Support Techniques`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **What connects `Deploy site to GitHub Pages (workflow)`, `GitLab Pages job`, `JSZip library (bundled locally in assets/vendor/)` to the rest of the system?**
  _289 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `VCE Study Design & Assessment Overview` be split into smaller, more focused modules?**
  _Cohesion score 0.06247086247086247 - nodes in this community are weakly interconnected._
- **Should `Sunset Boulevard Themes & Prompt Types` be split into smaller, more focused modules?**
  _Cohesion score 0.055191256830601096 - nodes in this community are weakly interconnected._
- **Should `Rainbow's End Historical Context` be split into smaller, more focused modules?**
  _Cohesion score 0.0672316384180791 - nodes in this community are weakly interconnected._