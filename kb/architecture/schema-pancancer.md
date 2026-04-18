# Schema: PANCANCER_ATLAS

- **DAB folder:** `query_PANCANCER_ATLAS`
- **Domain:** Healthcare / cancer genomics
- **DB systems:** PostgreSQL (clinical data) + SQLite (molecular profiling)
- **Cross-DB join key:** `ParticipantBarcode` (TCGA barcode format, e.g. `TCGA-XX-XXXX`)

---

## DB 1 — clinical_database (PostgreSQL)

### clinical_info

| Column | Type | Notes |
|---|---|---|
| ParticipantBarcode | str | Patient identifier — cross-DB join key |
| (100+ additional fields) | various | Not individually documented — must call schema discovery |

**Critical:** `clinical_info` has over 100 columns. Always call `list_db` or `PRAGMA table_info` equivalent first to inspect available fields before writing queries.

Fields typically include: cancer type acronym (e.g. `acronym` or `type`), demographics (age, gender, race), diagnosis details, treatment info, survival status (`vital_status`, `days_to_death`, `days_to_last_followup`), and staging data.

**Gotcha:** Column names vary across cancer atlas datasets. Do not hardcode field names — discover them first.

---

## DB 2 — molecular_database (SQLite)

### Mutation_Data

| Column | Type | Notes |
|---|---|---|
| ParticipantBarcode | str | Patient identifier — join key |
| Tumor_SampleBarcode | str | Tumor sample identifier |
| Tumor_AliquotBarcode | str | Tumor aliquot identifier |
| Normal_SampleBarcode | str | Normal control sample identifier |
| Normal_AliquotBarcode | str | Normal control aliquot identifier |
| Normal_SampleTypeLetterCode | str | Sample type abbreviation for normal sample |
| Hugo_Symbol | str | Gene symbol (e.g. `TP53`, `CDH1`, `BRCA1`) |
| HGVSp_Short | str | Protein-level mutation annotation (e.g. `p.R175H`) |
| Variant_Classification | str | e.g. `Missense_Mutation`, `Nonsense_Mutation`, `Silent` |
| HGVSc | str | Coding DNA mutation annotation |
| CENTERS | str | Contributing sequencing center |
| FILTER | str | Mutation filter status — `PASS` indicates a reliable call |

**Gotcha:** Always filter `FILTER = 'PASS'` unless the query explicitly asks for all variants. Non-PASS variants are lower-confidence calls.

### RNASeq_Expression

| Column | Type | Notes |
|---|---|---|
| ParticipantBarcode | str | Patient identifier — join key |
| SampleBarcode | str | Sample identifier |
| AliquotBarcode | str | Aliquot identifier |
| SampleTypeLetterCode | str | Sample type abbreviation |
| SampleType | str | Sample type description (e.g. `Primary Tumor`, `Solid Tissue Normal`) |
| Symbol | str | Gene symbol |
| Entrez | str | Entrez gene ID — stored as string |
| normalized_count | float | Normalized RNA expression value |

**Gotcha:** One patient (`ParticipantBarcode`) can have multiple samples and aliquots. Aggregating expression values requires deciding which sample type to use — typically `Primary Tumor`.

---

## Cross-Database Join

| From | Key | To |
|---|---|---|
| clinical_database.clinical_info.ParticipantBarcode | TCGA barcode string (exact match) | molecular_database.Mutation_Data.ParticipantBarcode |
| clinical_database.clinical_info.ParticipantBarcode | TCGA barcode string (exact match) | molecular_database.RNASeq_Expression.ParticipantBarcode |

**Merge in Python.** Query each database separately, then join on `ParticipantBarcode`.

```python
import pandas as pd
df = pd.merge(clinical_df, mutation_df, on="ParticipantBarcode", how="inner")
```

---

## Valid Intra-Database Joins

**SQLite — molecular_database:**

| Join | Key | Type |
|---|---|---|
| Mutation_Data → RNASeq_Expression | ParticipantBarcode | INNER/LEFT |

---

## Known Failure Patterns

- Hardcoding clinical field names without schema discovery → KeyError (100+ undocumented columns).
- Not filtering `FILTER = 'PASS'` in Mutation_Data → inflated mutation counts from low-confidence calls.
- Aggregating `normalized_count` across all sample types → mixing tumor and normal tissue expression values.
- Treating `Entrez` as integer without casting → type mismatch in comparisons.
- Assuming a single row per patient in RNASeq_Expression → multiple rows per patient per gene.
