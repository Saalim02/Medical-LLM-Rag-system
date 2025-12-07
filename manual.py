import re
from collections import namedtuple

# ---- Improved heading patterns ----
HEADING_PATTERNS = [
    r'^\s*CHAPTER\s+([IVXLC]+|\d+)\b.*$',           # CHAPTER I or CHAPTER 1
    r'^\s*Chapter\s+\d+\b.*$',                     # Chapter 1 ...
    r'^\s*[A-Z0-9][A-Z0-9\s\-\:\,]{10,}$',         # Long ALL CAPS lines (likely heading)
    r'^\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,6}\s*$',  # Short Title Case lines (standalone)
    r'^\s*\d+\s+[A-Z][A-Za-z\-\s]{4,}$',            # "2 General Pathology ..." (numeric prefix)
    r'^\s*[IVXLCDM]+\s+[A-Z][A-Za-z\-\s]{4,}$',     # "I INTRODUCTION" roman numerals + text
]

# ---- Exclude patterns (to avoid figure captions, table notes) ----
EXCLUDE_PATTERNS = [
    r'^\s*Figure\s*\d+(\.\d+)?\b',    # Figure 1 or Figure 1.2 at line start
    r'^\s*Fig\.\s*\d+',               # Fig. 1
    r'^\s*Table\s*\d+',               # Table 1
    r'^\s*Page\s*\d+',                # Page numbers
]

Heading = namedtuple("Heading", ["line_no", "text", "pattern_idx"])

def is_probable_heading(line):
    s = line.strip()
    # quick skip: empty or very short
    if not s or len(s) < 4:
        return False, None, None
    # exclude figure/table/page-like lines
    for pat in EXCLUDE_PATTERNS:
        if re.match(pat, s, flags=re.IGNORECASE):
            return False, None, None
    for i, pat in enumerate(HEADING_PATTERNS):
        if re.match(pat, s):
            return True, i, s
    return False, None, None

def find_headings_from_text(text):
    lines = text.splitlines()
    headings = []
    for idx, ln in enumerate(lines):
        matched, pat_idx, txt = is_probable_heading(ln)
        if matched:
            headings.append(Heading(idx+1, txt, pat_idx))
    return headings

# ---- Sample text (use your pasted sample here) ----
sample_text = """of pathology” (Fig. 1.1).
HEALTH AND DISEASE
Before there were humans on earth, there was disease, albeit in
early animals. Since pathology is the study of disease, then what
is disease? In simple language, disease is opposite of health
i.e. what is not healthy is disease. Health may be defined as a
condition when the individual is in complete accord with the
surroundings, while disease is loss of ease (or comfort) to the
body (i.e. dis+ease). However, it must be borne in mind that in
health there is a wide range of ‘normality’ e.g. in height, weight,
blood and tissue chemical composition etc. It also needs to be
appreciated that at cellular level, the cells display wide range
of activities within the broad area of health similar to what is
seen in diseased cells. Thus, a disease or an illness means a
condition marked by pronounced deviation from the normal
healthy state. The term syndrome (meaning running together)
is used for a combination of several clinical features caused by
altered physiologic processes.

COMMON TERMS IN PATHOLOGY
It is important for a beginner in pathology to be familiar with
the language used in pathology (Fig.1.2):
 Patient is the person affected by disease.
 Lesions are the characteristic changes in tissues and cells
produced by disease in an individual or experimental animal.
 Pathologic changes or morphology consist of examination
of diseased tissues. These can be recognised with the naked
eye (gross or macroscopic changes) or studied by microscopic
examination of tissues
.
2 General Pathology SECTION I
Figure 1.2 Diagrammatic depiction of disease and various terms used in pathology.
 Causal factors responsible for the lesions are included in
etiology of disease (i.e. ‘why’ of disease).
 Mechanism by which the lesions are produced is termed
pathogenesis of disease (i.e. ‘how’ of disease).
 Functional implications of the lesion felt by the patient
are symptoms and those discovered by the clinician are the
physical signs.
 Clinical significance of the morphologic and functional
changes together with results of other investigations help to
arrive at an answer to what is wrong (diagnosis), what is going
to happen (prognosis), what can  ( see it is like this whole book will the code recongnize the headings)"""

# ---- Run detection and print results ----
found = find_headings_from_text(sample_text)
print("Detected headings (line_no : text):\n" + "-"*40)
for h in found:
    print(f"{h.line_no:3d} : {h.text}")
