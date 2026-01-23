from collections.abc import Iterable, Mapping


class TrialCriteriaToGenes:
    """
    Extract official gene symbols from free-text trial criteria.

    Accepts a pre-loaded synonym mapping:
    - synonym_to_symbol: maps any synonym (including addendum entries) -> official symbol
    """

    def __init__(
        self,
        trial_criteria: str,
        synonym_to_symbol: Mapping[str, str | Iterable[str]],
    ):
        self.trial_criteria = trial_criteria or ""
        self.synonym_to_symbol = synonym_to_symbol

    @staticmethod
    def _normalize_token(s: str) -> str:
        s = (s or "").strip()
        s = s.strip('"\',;:.()[]{}')
        return s

    @staticmethod
    def _as_list(v: str | Iterable[str] | None) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return [x for x in v if x is not None]

    @classmethod
    def _generate_candidates(cls, words: list[str], max_ngram: int = 4) -> list[str]:
        """
        Build candidate phrases (n-grams) from normalized tokens.
        Longest n-grams are generated first so multi-word addendum keys can match early.
        """
        candidates: list[str] = []
        n_max = max(1, int(max_ngram))
        for n in range(min(n_max, len(words)), 0, -1):
            for i in range(0, len(words) - n + 1):
                candidates.append(" ".join(words[i : i + n]))

        # De-dupe while preserving order.
        seen: set[str] = set()
        out: list[str] = []
        for c in candidates:
            if c in seen:
                continue
            seen.add(c)
            out.append(c)
        return out

    def tokenize_trial_criteria(self, max_ngram: int = 4) -> list[str]:
        """
        tokenization of the trial criteria
        """
        tokens_raw = (self.trial_criteria or "").split()
        words = [w for w in (self._normalize_token(t) for t in tokens_raw) if w]

        #words = self._generate_candidates(words, max_ngram=max_ngram)
        return words

    def _lookup_official_symbols(self, token: str) -> list[str]:
        """
        Lookup a token in the synonym mapping.
        """
        if token in self.synonym_to_symbol:
            print(f"Found mapping for token: {token} : {self.synonym_to_symbol[token]}")
            return self._as_list(self.synonym_to_symbol[token])
        return []

    def extract_official_gene_symbols(self) -> list[str]:
        """
        Returns a de-duplicated list of official gene symbols found in the criteria.
        """
        tokens = self.tokenize_trial_criteria()

        found: set[str] = set[str]()
        for tok in tokens:
            official_symbols = self._lookup_official_symbols(tok)
            if len(official_symbols) > 0:
                # Each value can itself be a comma-separated list of symbols,
                # e.g. "KRAS,NRAS,HRAS". Split, normalize, and add individually.
                for val in official_symbols:
                    for part in val.split(","):
                        norm = self._normalize_token(part)
                        if norm:
                            found.add(norm)

        return list[str](found)