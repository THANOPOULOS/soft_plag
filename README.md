# SoftPlag — Software Plagiarism Detector

A desktop application for detecting source code plagiarism across multiple programming languages. SoftPlag uses a multi-algorithm approach combining tokenization, Jaccard similarity, Longest Common Subsequence (LCS), and Winnowing fingerprinting to reliably detect copied code — even when variables have been renamed, functions reordered, comments added, or code partially copied.

---

## Features

- **Multi-language support** — C, C++, C#, Java, Python, JavaScript
- **Zip file support** — automatically extracts and compares files inside `.zip` archives
- **Robust plagiarism detection** — defeats variable renaming, function reordering, comment injection, and partial copying
- **Interactive visualizations** — similarity heatmap, score distribution chart, file clustering graph, and detailed comparison table
- **Side-by-side diff viewer** — double-click any pair to view both source files next to each other
- **No internet required** — runs fully offline on your machine

---

## Supported Languages

| Language | File Extensions |
|---|---|
| C | `.c`, `.h` |
| C++ | `.cpp`, `.cxx`, `.cc`, `.hpp`, `.hxx` |
| C# | `.cs` |
| Java | `.java` |
| Python | `.py` |
| JavaScript | `.js`, `.mjs`, `.cjs` |

---

## How to Run

### Option A — Run the executable (no installation needed)

1. Download the latest release from the [Releases](../../releases) page
2. Extract the `SoftPlag.zip` file anywhere on your PC
3. Open the `SoftPlag` folder
4. Double-click **SoftPlag.exe**

> The `SoftPlag.exe` and the `_internal` folder must always stay together in the same folder.

---

### Option B — Run from source code

**Requirements:**
- Python 3.10 or higher
- pip

**Steps:**

1. Clone the repository
```
git clone https://github.com/THANOPOULOS/soft_plag.git
cd soft_plag
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the app
```
python main.py
```

---

## How to Use

### Step 1 — Select a folder
Click the **📁 Select Folder** button and choose a directory containing source code files. The app will scan the folder (including any `.zip` files) and show how many files were found.

### Step 2 — Choose a language
Click the **🔤 Language** button to open the language selector. Pick the programming language you want to compare. The default is **C**.

### Step 3 — Compare
Click the **▶ Compare** button to start the analysis. A progress bar will appear while the files are being processed.

### Step 4 — View results
Once complete, four result tabs appear:

| Tab | Description |
|---|---|
| 📊 Distribution | Histogram of all similarity scores, color-coded by risk level |
| 🌡 Heatmap | Matrix showing similarity between every pair of files |
| 🔗 Clustering | Network graph and scatter plot grouping similar files together |
| 📋 Details | Sortable table of all file pairs with individual algorithm scores |

> Double-click any row in the Details tab to open a side-by-side source code viewer for that pair.

---

## Risk Levels

| Score | Risk Level | Meaning |
|---|---|---|
| 0.70 or above | 🔴 High | Very likely plagiarism |
| 0.40 – 0.69 | 🟡 Medium | Suspicious — manual review recommended |
| Below 0.40 | 🟢 Low | Likely original work |

---

## How Detection Works

SoftPlag uses a three-stage pipeline:

### 1. Tokenization
Each source file is transformed into a normalized sequence of tokens:
- All comments are stripped
- Import/package statements and preprocessor directives are removed
- Every user-defined identifier (variable names, function names) is replaced with `ID`
- All numbers become `NUM`, all strings become `STR`
- Only language keywords and operators are preserved

This means two files that are logically identical but have renamed variables will produce the same token sequence.

### 2. Similarity Measurement (3 algorithms)

| Algorithm | Weight | Strength |
|---|---|---|
| Jaccard similarity on 5-grams | 35% | Handles function reordering |
| LCS ratio (Longest Common Subsequence) | 40% | Catches partial copying |
| Winnowing fingerprinting (MOSS algorithm) | 25% | Robust against inserted code |

**Combined score** = `(Jaccard × 0.35) + (LCS × 0.40) + (Winnowing × 0.25)`

### 3. Risk Classification
The combined score is compared against fixed thresholds to assign a risk label of High, Medium, or Low.

---

## Plagiarism Techniques Detected

| Technique | How SoftPlag defeats it |
|---|---|
| Renaming variables and functions | Identifier normalization — all names become `ID` |
| Adding or modifying comments | Comment stripping before any comparison |
| Rearranging functions | Jaccard similarity is set-based and order-independent |
| Copying only part of the code | LCS ratio detects shared subsequences |
| Inserting extra code between copied sections | Winnowing fingerprints survive insertions |

---

## Project Structure

```
SoftPlag/
├── main.py                        # Entry point
├── requirements.txt               # Python dependencies
├── core/
│   ├── tokenizer.py               # Language-specific tokenizers
│   ├── similarity.py              # Jaccard, LCS, Winnowing algorithms
│   └── analyzer.py                # Orchestrates analysis pipeline
├── gui/
│   ├── main_window.py             # Main application window
│   ├── language_dialog.py         # Language selection dialog
│   ├── results_panel.py           # Results tabs and diff viewer
│   └── worker_thread.py           # Background analysis thread
└── visualizations/
    ├── heatmap.py                 # Similarity heatmap
    ├── distribution.py            # Score distribution chart
    └── clustering.py              # Network graph and MDS scatter
```

---

## Dependencies

| Library | Purpose |
|---|---|
| PySide6 | Desktop GUI framework |
| matplotlib | Chart and graph rendering |
| seaborn | Heatmap visualization |
| networkx | File similarity network graph |
| scikit-learn | MDS clustering and AgglomerativeClustering |
| numpy | Similarity matrix operations |

Install all dependencies with:
```
pip install -r requirements.txt
```

---

## Building the Executable

To build a standalone `.exe` file using PyInstaller:

```
pip install pyinstaller
pyinstaller SoftPlag.spec --noconfirm
```

The output will be in `dist\SoftPlag\`. Share the entire `SoftPlag` folder — the `.exe` and `_internal` folder must stay together.

---

## License

This project was built for academic and educational purposes.
