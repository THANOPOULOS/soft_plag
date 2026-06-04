import os
import zipfile
import tempfile
import shutil
from dataclasses import dataclass, field

import numpy as np

from core.tokenizer import TokenizedFile, get_tokenizer, LANGUAGE_EXTENSIONS
from core import similarity as sim

#metablhtes
@dataclass
class PairResult:
    file_a: str
    file_b: str
    path_a: str
    path_b: str
    jaccard: float
    lcs: float
    winnowing: float
    combined: float
    source_a: str = ""
    source_b: str = ""


@dataclass
class AnalysisResult:
    language: str
    files: list
    pair_results: list
    similarity_matrix: object
    file_index: dict = field(default_factory=dict)

#diaheirisi zip arheion
def _peek_zips(folder: str, exts: set) -> int:
    """aparithmish zip arxeion"""
    count = 0
    for root, _dirs, files in os.walk(folder):
        for fname in files:
            if fname.lower().endswith(".zip"):
                try:
                    with zipfile.ZipFile(os.path.join(root, fname), "r") as zf:
                        for member in zf.namelist():
                            if any(member.lower().endswith(e) for e in exts):
                                count += 1
                except Exception:
                    pass
    return count

#
def scan_folder(folder: str, language: str) -> list:
    #epistrofh ton arheion kodika pou ehoun vrethei
    exts = set(LANGUAGE_EXTENSIONS.get(language, []))
    found = []
    for root, _dirs, files in os.walk(folder):
        for fname in files:
            if any(fname.lower().endswith(e) for e in exts):
                found.append(os.path.join(root, fname))
    return sorted(found)


def scan_folder_with_zips(folder: str, language: str) -> int:
    #epistrofh tou synolikou arithmou arxeion
    regular = len(scan_folder(folder, language))
    exts = set(LANGUAGE_EXTENSIONS.get(language, []))
    zipped = _peek_zips(folder, exts)
    return regular + zipped


class Analyzer:

    def __init__(self, folder: str, language: str):
        self.folder = folder
        self.language = language
        self._tokenizer = get_tokenizer(language)
        self._temp_dir = None

    def _extract_all_zips(self, progress_cb):
        #epistrofh ton extracted arxeion.
        exts = set(LANGUAGE_EXTENSIONS.get(self.language, []))
        extracted = []

        zip_files = []
        for root, _, files in os.walk(self.folder):
            for fname in files:
                if fname.lower().endswith(".zip"):
                    zip_files.append(os.path.join(root, fname))

        for zip_path in zip_files:
            zip_stem = os.path.splitext(os.path.basename(zip_path))[0]
            if progress_cb:
                progress_cb(1, f"Extracting {os.path.basename(zip_path)}...")
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    for member in zf.namelist():
                        if not any(member.lower().endswith(e) for e in exts):
                            continue
                        # Extract into temp_dir/zipname/member preserving inner structure
                        dest = os.path.join(self._temp_dir, zip_stem, member)
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        with zf.open(member) as src, open(dest, "wb") as dst:
                            dst.write(src.read())
                        extracted.append(dest)
            except zipfile.BadZipFile:
                pass
            except Exception:
                pass

        return extracted

    def _display_name(self, path: str) -> str:
        #dimiourgia label gia ta arxeia.
        #Regular files  → filename.c
        #Extracted files → zipname/filename.c  (oste o hristis na katalavei oti to arxeio proerxetai apo zip)
        
        if self._temp_dir and path.startswith(self._temp_dir):
            rel = os.path.relpath(path, self._temp_dir)
            parts = rel.split(os.sep)
            if len(parts) >= 2:
                zip_name = parts[0]
                file_name = parts[-1]
                return f"{zip_name}/{file_name}"
        return os.path.basename(path)

    def scan(self) -> list:
        return scan_folder(self.folder, self.language)

    def _read_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()

    def _tokenize_file(self, path: str) -> TokenizedFile:
        source = self._read_file(path)
        tokens = self._tokenizer.tokenize(source)
        return TokenizedFile(path=path, tokens=tokens, raw_source=source)

    def run(self, progress_cb=None) -> AnalysisResult:
        def _progress(pct: int, msg: str):
            if progress_cb:
                progress_cb(pct, msg)

        self._temp_dir = tempfile.mkdtemp(prefix="softplag_")
        try:
            return self._run_internal(_progress)
        finally:
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            self._temp_dir = None

    def _run_internal(self, _progress) -> AnalysisResult:
        # --- stadio 1:sylogh kanonikon arheion ---
        regular_paths = self.scan()
        _progress(1, "Scanning for zip archives...")

        # --- stadio 2: extract zips ---
        extracted_paths = self._extract_all_zips(_progress)

        all_paths = sorted(regular_paths + extracted_paths)
        n = len(all_paths)

        if n == 0:
            return AnalysisResult(
                language=self.language,
                files=[],
                pair_results=[],
                similarity_matrix=np.zeros((0, 0)),
                file_index={},
            )

        zip_count = len(extracted_paths)
        msg = f"Found {n} files"
        if zip_count:
            msg += f" ({zip_count} from zip archives)"
        _progress(2, msg + " — tokenizing...")

        # --- stadio 3: tokenize ola ta arxeia ---
        tokenized = []
        for i, path in enumerate(all_paths):
            pct = 2 + int((i / n) * 28)
            _progress(pct, f"Tokenizing: {self._display_name(path)}")
            tokenized.append(self._tokenize_file(path))

        _progress(30, "Computing pairwise similarity...")

        # --- stadio 4: dymiourgeia display names kai matrix ---
        display_names = [self._display_name(p) for p in all_paths]

        # diaheirish panomoiotipon display names (2 zips me idio onoma arxeiou)
        seen = {}
        unique_names = []
        for name in display_names:
            if name in seen:
                seen[name] += 1
                unique_names.append(f"{name} ({seen[name]})")
            else:
                seen[name] = 0
                unique_names.append(name)

        file_index = {b: i for i, b in enumerate(unique_names)}
        matrix = np.zeros((n, n), dtype=float)
        np.fill_diagonal(matrix, 1.0)

        pair_results = []
        total_pairs = n * (n - 1) // 2
        pair_count = 0

        # --- stadio 5: sygrish ton zeugarion ---
        for i in range(n):
            tf_a = tokenized[i]
            ngrams_a = sim.build_ngrams(tf_a.tokens)
            for j in range(i + 1, n):
                tf_b = tokenized[j]
                ngrams_b = sim.build_ngrams(tf_b.tokens)

                j_score = sim.jaccard_similarity(ngrams_a, ngrams_b)
                l_score = sim.lcs_similarity(tf_a.tokens, tf_b.tokens)
                w_score = sim.winnowing_similarity(tf_a.tokens, tf_b.tokens)
                c_score = sim.combined_score(j_score, l_score, w_score)

                matrix[i][j] = c_score
                matrix[j][i] = c_score

                pair_results.append(PairResult(
                    file_a=unique_names[i],
                    file_b=unique_names[j],
                    path_a=all_paths[i],
                    path_b=all_paths[j],
                    jaccard=j_score,
                    lcs=l_score,
                    winnowing=w_score,
                    combined=c_score,
                    source_a=tokenized[i].raw_source,
                    source_b=tokenized[j].raw_source,
                ))

                pair_count += 1
                if total_pairs > 0:
                    pct = 30 + int((pair_count / total_pairs) * 65)
                    _progress(pct, f"Comparing {unique_names[i]} ↔ {unique_names[j]}")

        pair_results.sort(key=lambda r: r.combined, reverse=True)
        _progress(97, "Building result...")
        #epistrofh apotelesmaton
        return AnalysisResult(
            language=self.language,
            files=unique_names,
            pair_results=pair_results,
            similarity_matrix=matrix,
            file_index=file_index,
        )
