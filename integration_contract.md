# Integration Contract – Clinical Insight Engine

## Overview

This document defines the data exchange format between the **Semantic Retrieval Engine** and the **Insight Engine**. It ensures consistency, modularity, and seamless integration across components for Day 5 of the pipeline.

---

## 1. Input to Insight Engine

The Insight Engine receives the output from the Retrieval Engine in the form of a list of top-K similar historical cases.

### Data Structure

* **Type:** List of Dictionaries
* **Description:** Each dictionary represents one retrieved clinical case matching the patient query.

---

### Fields Description

| Field Name | Type   | Description                                                                 |
| ---------- | ------ | --------------------------------------------------------------------------- |
| case_id    | string | Unique identifier for the historical case                                   |
| similarity | float  | Cosine similarity score between input case and retrieved case (range: 0–1)  |
| diagnosis  | string | The established diagnosis of the historical case                            |
| treatment  | string | The treatment administered in the historical case                           |
| symptoms   | list   | List of text symptoms experienced by the historical patient                 |

---

### Example Input Payload

```json
[
  {
    "case_id": "CASE_045",
    "similarity": 0.92,
    "diagnosis": "Atopic Dermatitis",
    "treatment": "Topical Corticosteroids",
    "symptoms": ["pruritus", "erythema", "dry scaling skin"]
  },
  {
    "case_id": "CASE_012",
    "similarity": 0.88,
    "diagnosis": "Atopic Dermatitis",
    "treatment": "Emollients and Antihistamines",
    "symptoms": ["itchy rash", "redness", "dry skin"]
  }
]