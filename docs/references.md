# Project References

This file is a working reference register for sources used during COMP1884 planning, implementation, evaluation, and final report preparation.

The final academic report must convert relevant entries into the University-required citation/reference style and verify all bibliographic details before submission.

## How this register is used

This register supplies background sources, not recorded performance or automatic method approval. [Literature review](literature/literature-review.md) owns synthesis; [research design](research-design.md) owns rationale/hypotheses; [features](forecasting-feature-engineering.md) and [protocol](protocol.md) own exact implemented definitions; [final evaluation](forecasting-final-evaluation.md) cites retained validation/final numerical evidence and limitations. This cleanup preserves bibliographic entries without claiming a new external source verification.

## Dataset sources

### Selected dataset

**High-Dimensional Supply Chain Inventory Dataset**  
Publisher: Ziya  
Platform: Kaggle  
URL: https://www.kaggle.com/datasets/ziya07/high-dimensional-supply-chain-inventory-dataset

Why it is relevant:

- daily SKU-level supply-chain data;
- historical units sold;
- inventory levels;
- supplier lead times;
- reorder points and quantities;
- warehouse, supplier, and regional dimensions;
- promotional indicators;
- stockout indicators;
- cost and price fields;
- source-provided demand forecast.

Important limitation:

- the dataset downloaded from Kaggle is simulated by its publisher, not observed from a real operating retailer.

### Dataset source context

- Ziya (n.d.) *High-Dimensional Supply Chain Inventory Dataset*. Kaggle. [Dataset page](https://www.kaggle.com/datasets/ziya07/high-dimensional-supply-chain-inventory-dataset) (Accessed: 8 October 2026). The page reports Usability **8.82/10** and describes its intended applications in demand forecasting and inventory research.
- Ziya (n.d.) *Ziya (ziya07) profile*. Kaggle. [Profile](https://www.kaggle.com/ziya07) and [dataset rankings](https://www.kaggle.com/rankings/datasets) (Accessed: 8 October 2026). Lists the publisher as a Datasets Expert.
- Pancini, M., Camilli, M., Quattrocchi, G. and Tamburri, D.A. (2025) 'Engineering MLOps Pipelines With Data Quality: A Case Study on Tabular Datasets in Kaggle', *Journal of Software: Evolution and Process*, 37(9), e70044. [https://doi.org/10.1002/smr.70044](https://doi.org/10.1002/smr.70044) (Accessed: 8 October 2026). Section 4.3 explains the documentation, public-content, file-type and metadata basis of Kaggle Usability.

The [dataset suitability note](dataset.md#11-suitability-for-the-project-research-purpose) connects this source context with the project's verified profiling evidence and documented research scope.

### Original dataset from the COMP1889 proposal

**Online Retail**  
Publisher: UCI Machine Learning Repository  
URL: https://archive.ics.uci.edu/dataset/352/online+retail

Status in COMP1884:

- retained as part of the project decision history;
- superseded as the primary implementation dataset by DR-001 because it does not contain the inventory-state and replenishment variables required by the integrated framework.

## University / project guidance

University of Greenwich COMP1884 group-project guidance and relevant project materials should be cited or referenced in the final report only where academically appropriate.

The [university AI-use evidence note](university-ai-guidance.md) records source provenance, local file identities, confirmed Tier 2/AIR instructions and actual attribution requirements. Chathuranga confirmed Tier 2 on 5 November; the supplied student guidance requires an AIR before references. These sources do not grant blanket permission to present generated work as original.

- University of Greenwich (2026) '[New AI guidance to support learning and assessments in 2026/27](https://www.gre.ac.uk/articles/public-relations/new-ai-guidance-to-support-learning-and-assessments-in-202627)', 9 September (Accessed: 8 October 2026). Public article inspected; detailed linked guidance was not accessible during the review.
- University of Greenwich (2025/26) *UoG Student Handbook*. Academic-year edition supplied to Chathuranga; local original: `research-materials/university/student-handbook-2025-26.docx`. Relevant academic-integrity text inspected on 8 October 2026; academic year is an edition label, not a verified publication date.
- *Declaration of AI Use* (n.d.). University-supplied form according to Chathuranga; author/date/version not stated in the inspected text. Local original: `research-materials/university/declaration-of-ai-use.docx`. Inspected on 8 October 2026; first-semester receipt does not establish second-semester assessment permission.

**Current COMP1884 assessment sources — inspected 5 November 2026:** Original PDFs remain local under `research-materials/university/COMP1884_Group_Project/`. Academic-year labels below describe the supplied editions, not independently established publication dates. The [criteria checklist](greenwich-criteria-checklist.md#sources) records file identities, requirements and remaining deadline/upload questions.

- University of Greenwich (n.d.) *COMP1884 Coursework Specifications: Report*. Academic year 2026/27. Local file: `COMP 1884 Report specifications PIBT 26-27.docx.pdf`. Group report, code ZIP and meeting-minutes requirements; report rubric; AI support/acknowledgement instructions.
- University of Greenwich (n.d.) *COMP1884 Coursework Specifications: Presentation*. Academic year 2026/27. Local file: `COMP 1884 Presentation_specifications_PIBT26-27 (1).docx.pdf`. Individual live presentation, slides/recording and reflective-essay requirements; component rubric; AI support/acknowledgement instructions.
- University of Greenwich (n.d.) *Group project report template*. Supplied 2026/27 edition. Local file: `COMP 1884 Report template-final report 2026-27.docx.pdf`. Required report sections, formatting, references, contribution statement and appendices.
- University of Greenwich (n.d.) *COMP1884 Group Project: individual essay*. Supplied 2026/27 template. Local file: `COMP 1884 Report template-individual essay 2026-27.docx.pdf`. Reflection framework, actual examples, two improvement actions and referencing/declaration guidance.
- University of Greenwich (n.d.) *Record of Group Meeting*. Supplied 2026/27 template. Local file: `COMP 1884 Report template-meeting minutes 2026-27.docx.pdf`. Meeting updates/actions, attributed participation and agreed asynchronous coordination.
- University of Greenwich (n.d.) *MSc project guidance: Group (COMP1884) and individual (COMP1885) projects*. Academic year 2026/27. Local file: `COMP 1884 Report - Group-individual-project-guidance_PIBT26-27.docx.pdf`. General project integration, coding-contribution, demonstration and process guidance; exact assessment specifications take precedence for deliverables. COMP1885 requirements remain outside this repository’s scope.
- University of Greenwich (n.d.) *COMP1884 Group Project: group work escalation procedure*. Supplied 2026/27 file: `COMP 1884 Report Group work-escalation procedure PIBT26-27.docx.pdf`. Conditional escalation and exceptional submission arrangements; receipt is not evidence that a stage was reached or an exception granted.

**Student AI guidance — inspected 5 November 2026:** Originals remain under `research-materials/university/Artificial Intelligence (AI) guidance for students/`; local SHA-256 identities are recorded in the [AI-use note](university-ai-guidance.md#file-identities) and checklist G12/G13.

- University of Greenwich (n.d.) *AI at the University of Greenwich*. Local file: `ai-guidance.pdf`. Defines the three tiers and requires an AI Reflection for permitted Tier 2/3 use, before references, with CRITIC as a suggested framework. Chathuranga confirmed continued Tier 2 application on 5 November; the document does not name this project’s tier by itself.
- University of Greenwich (n.d.) *Citing and referencing generative artificial intelligence (GenAI)*. Supplied filename: `referencing-for-generative-ai-sept-2026.pdf` (September 2026 source label). Covers generated text, images, code and ideas and provides citation structures; do not treat example chat dates as project facts.

Use the current AIR and referencing guidance with accurate accounts of actual assistance. Keep earlier declaration materials as history; the repository no longer records the Tier 2/AIR baseline as awaiting a decision.

The [COMP1884 criteria checklist](greenwich-criteria-checklist.md) records the following additional sources and their applicability limits (inspected 14 October 2026):

- University of Greenwich (n.d.) *Programme Specifications*, academic session 2026/27, programme P14555, Banner Self Service. Supplied screenshot `programme-specification-2026-27.png`; displayed title `MSc DATA SCI & ITS APPS (PIBT)`. The visible table identifies COMP1884 Group Project (30 credits), COMP1885 Individual Project (30 credits) and COMP1889 Research Project Management (10 credits) as compulsory modules. Capture/publication date is unknown. Local original: `research-materials/university/programme-specification-2026-27.png`; image and matching SHA-256 rechecked on 15 October 2026. The original remains outside Git; this snapshot does not establish assessment criteria or policy applicability.
- *COMP1884 Group Project Instructions* (n.d.). University-supplied guidance retained locally as `research-materials/university/COMP1884_Group Project_Instructions.docx`. Describes group organisation, a shared-mark group report, individual reflective essays and a group presentation with individual performance marking. Undated background guidance: its general presentation description and absent marking sheet are superseded for detailed submission planning by the supplied 2026/27 specifications and rubrics above.
- University of Greenwich (n.d.) [*Assessment and Feedback Policy and Guidance*](https://www.gre.ac.uk/docs/rep/vco/assessment-and-feedback-policy). Policy index last updated 23 October 2025 (Accessed: 14 October 2026). Public applicability guidance inspected: 2019 and 2025 policies remain active during the curriculum transition; the applicable version for P14555 is unconfirmed. Detailed policy provisions are not verified by this index review.

**Human planning context (H2), separate from university guidance:** In his latest clarification in the project working conversation on 15 October 2026, Chathuranga stated that he aims to finish the work with the team by **5 November 2026**. This is his internal completion target, not a confirmed university submission deadline or evidence of team agreement. He tentatively expects submission in the first or second week of November, but does not know the exact date. The official deadline, submission time/timezone, separate deliverable deadlines and presentation date remain unconfirmed. The clarification is publicly recorded in the [Issue #165 scope comment](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/165#issuecomment-6189673295). See the [checklist source register](greenwich-criteria-checklist.md#sources).

The 9 September 2026 AI-guidance article above was rechecked on 14 October 2026 for the checklist. This does not verify the full linked guidance or resolve assessment-specific permissions.

## Literature references

The literature-review baseline is maintained in:

```text
docs/literature/literature-review.md
```

The following peer-reviewed sources are currently used to support the research design, methodology, research gap, or responsible decision-support framing. Bibliographic details must be re-checked against the University-required reference style before final submission.

- Bergmeir, C. and Benítez, J.M. (2012) 'On the use of cross-validation for time series predictor evaluation', *Information Sciences*, 191, pp. 192-213. https://doi.org/10.1016/j.ins.2011.12.028
- Bergsma, R., de Ruijt, C. and Bhulai, S. (2025) 'A systematic review of machine learning approaches in inventory control optimization', *Operations Research Perspectives*, 15, 100367. https://doi.org/10.1016/j.orp.2025.100367
- Feizabadi, J. (2022) 'Machine learning demand forecasting and supply chain performance', *International Journal of Logistics Research and Applications*, 25(2), pp. 119-142. https://doi.org/10.1080/13675567.2020.1803246
- Fildes, R., Kolassa, S. and Ma, S. (2022) 'Post-script—Retail forecasting: Research and practice', *International Journal of Forecasting*, 38(4), pp. 1319-1324. https://doi.org/10.1016/j.ijforecast.2021.09.012
- Fildes, R., Ma, S. and Kolassa, S. (2022) 'Retail forecasting: Research and practice', *International Journal of Forecasting*, 38(4), pp. 1283-1318. https://doi.org/10.1016/j.ijforecast.2019.06.004
- Goltsos, T.E., Syntetos, A.A., Glock, C.H. and Ioannou, G. (2022) 'Inventory–forecasting: Mind the gap', *European Journal of Operational Research*, 299(2), pp. 397-419. https://doi.org/10.1016/j.ejor.2021.07.040
- Hewage, H.C., Perera, H.N. and Bandara, K. (2026) 'Enhancing Demand Forecasting in Retail: A Comprehensive Analysis of Sales Promotional Effects on the Entire Demand Life Cycle', *Journal of Forecasting*, 45(1), pp. 293-315. https://doi.org/10.1002/for.70039
- Hyndman, R.J. and Koehler, A.B. (2006) 'Another look at measures of forecast accuracy', *International Journal of Forecasting*, 22(4), pp. 679-688. https://doi.org/10.1016/j.ijforecast.2006.03.001
- Kosasih, E.E., Papadakis, E., Baryannis, G. and Brintrup, A. (2024) 'A review of explainable artificial intelligence in supply chain management using neurosymbolic approaches', *International Journal of Production Research*, 62(4), pp. 1510-1540. https://doi.org/10.1080/00207543.2023.2281663
- Nasseri, M., Falatouri, T., Brandtner, P. and Darbanian, F. (2023) 'Applying Machine Learning in Retail Demand Prediction—A Comparison of Tree-Based Ensembles and Long Short-Term Memory-Based Deep Learning', *Applied Sciences*, 13(19), 11112. https://doi.org/10.3390/app131911112
- Olan, F., Spanaki, K., Ahmed, W. and Zhao, G. (2024) 'Enabling explainable artificial intelligence capabilities in supply chain decision support making', *Production Planning & Control*. https://doi.org/10.1080/09537287.2024.2313514
- Reis, M.I., Gonçalves, J.N.C., Cortez, P., Carvalho, M.S. and Fernandes, J.M. (2025) 'A context-aware decision support system for selecting explainable artificial intelligence methods in business organizations', *Computers in Industry*, 165, 104233. https://doi.org/10.1016/j.compind.2024.104233
- Silver, E.A. and Robb, D.J. (2008) 'Some insights regarding the optimal reorder period in periodic review inventory systems', *International Journal of Production Economics*, 112(1), pp. 354-366. https://doi.org/10.1016/j.ijpe.2007.03.014
- Lee, J.-Y. and Schwarz, L.B. (2009) 'Leadtime management in a periodic-review inventory system: A state-dependent base-stock policy', *European Journal of Operational Research*, 199(1), pp. 122-129. https://doi.org/10.1016/j.ejor.2008.10.024
- Tashman, L.J. (2000) 'Out-of-sample tests of forecasting accuracy: an analysis and review', *International Journal of Forecasting*, 16(4), pp. 437-450. https://doi.org/10.1016/S0169-2070(00)00065-0
- Theodorou, E., Spiliotis, E. and Assimakopoulos, V. (2025) 'Forecast accuracy and inventory performance: Insights on their relationship from the M5 competition data', *European Journal of Operational Research*, 322(2), pp. 414-426. https://doi.org/10.1016/j.ejor.2024.12.033

Do not add a paper only because it was found during search. Add it when the group has verified that it materially supports the research design, methodology, interpretation, or final report.
