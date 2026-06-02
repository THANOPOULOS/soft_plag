import re
import io
import keyword
import tokenize as _tokenize
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TokenizedFile:
    path: str
    tokens: list
    raw_source: str

#dymiourgia ton token (C, C++, C#, Java, JavaScript)
_C_KEYWORDS = frozenset({
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if",
    "inline", "int", "long", "register", "restrict", "return", "short",
    "signed", "sizeof", "static", "struct", "switch", "typedef", "union",
    "unsigned", "void", "volatile", "while",
    "NULL", "true", "false",
})

_CPP_KEYWORDS = _C_KEYWORDS | frozenset({
    "alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand", "bitor",
    "bool", "catch", "class", "compl", "concept", "consteval", "constexpr",
    "constinit", "co_await", "co_return", "co_yield", "decltype", "delete",
    "explicit", "export", "friend", "mutable", "namespace", "new", "noexcept",
    "not", "not_eq", "nullptr", "operator", "or", "or_eq", "override",
    "private", "protected", "public", "reinterpret_cast", "requires",
    "static_assert", "static_cast", "template", "this", "throw", "try",
    "typeid", "typename", "using", "virtual", "wchar_t", "xor", "xor_eq",
    "string", "vector", "map", "set", "list", "pair", "cout", "cin",
    "endl", "std",
})

_CSHARP_KEYWORDS = frozenset({
    "abstract", "as", "base", "bool", "break", "byte", "case", "catch",
    "char", "checked", "class", "const", "continue", "decimal", "default",
    "delegate", "do", "double", "else", "enum", "event", "explicit",
    "extern", "false", "finally", "fixed", "float", "for", "foreach",
    "goto", "if", "implicit", "in", "int", "interface", "internal", "is",
    "lock", "long", "namespace", "new", "null", "object", "operator", "out",
    "override", "params", "private", "protected", "public", "readonly",
    "ref", "return", "sbyte", "sealed", "short", "sizeof", "stackalloc",
    "static", "string", "struct", "switch", "this", "throw", "true", "try",
    "typeof", "uint", "ulong", "unchecked", "unsafe", "ushort", "using",
    "virtual", "void", "volatile", "while", "async", "await", "dynamic",
    "get", "set", "value", "var", "where", "yield", "partial", "record",
    "init", "with", "nint", "nuint",
})

_JAVA_KEYWORDS = frozenset({
    "abstract", "assert", "boolean", "break", "byte", "case", "catch",
    "char", "class", "const", "continue", "default", "do", "double",
    "else", "enum", "extends", "final", "finally", "float", "for", "goto",
    "if", "implements", "import", "instanceof", "int", "interface", "long",
    "native", "new", "null", "package", "private", "protected", "public",
    "return", "short", "static", "strictfp", "super", "switch",
    "synchronized", "this", "throw", "throws", "transient", "true", "try",
    "void", "volatile", "while", "var", "record", "sealed", "permits",
    "yield", "String", "Object", "System", "out", "println", "Integer",
    "Double", "Boolean", "List", "Map", "Set", "ArrayList", "HashMap",
})

_JS_KEYWORDS = frozenset({
    "break", "case", "catch", "class", "const", "continue", "debugger",
    "default", "delete", "do", "else", "export", "extends", "false",
    "finally", "for", "function", "if", "import", "in", "instanceof",
    "let", "new", "null", "of", "return", "static", "super", "switch",
    "this", "throw", "true", "try", "typeof", "undefined", "var", "void",
    "while", "with", "yield", "async", "await", "from", "get", "set",
    "target", "prototype", "constructor", "arguments", "console", "log",
    "Math", "Array", "Object", "String", "Number", "Boolean", "Promise",
    "then", "catch", "resolve", "reject",
})
#dymiourgia lexer ton tokens
_TOKEN_PATTERN = re.compile(
    r'[A-Za-z_]\w*|0[xX][0-9A-Fa-f]+|[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?'
    r'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''
    r'|<<=|>>=|>>>|<<|>>|->|::|&&|\|\||[+\-*/%&|^~]=?|[=!<>]=?'
    r'|[;,.()\[\]{}?:@]'
)


class BaseTokenizer(ABC):

    @property
    @abstractmethod
    def keywords(self):
        pass
#katharismos ton comments kai noise
    def tokenize(self, source: str) -> list:
        cleaned = self.strip_comments(source)
        cleaned = self.strip_structural_noise(cleaned)
        raw_tokens = _TOKEN_PATTERN.findall(cleaned)
        return self._normalize(raw_tokens)
#kathgoropoihsh ton tokens se id,num,string,operators kai keywords
    def _normalize(self, raw_tokens: list) -> list:
        result = []
        for tok in raw_tokens:
            if tok in self.keywords:
                result.append(tok)
            elif re.fullmatch(r'[A-Za-z_]\w*', tok):
                result.append("ID")
            elif re.fullmatch(r'0[xX][0-9A-Fa-f]+|[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?', tok):
                result.append("NUM")
            elif (tok.startswith('"') or tok.startswith("'")):
                result.append("STR")
            else:
                result.append(tok)
        return [t for t in result if t.strip()]

    @abstractmethod
    def strip_comments(self, source: str) -> str:
        pass

    def strip_structural_noise(self, source: str) -> str:
        return source

#dymiourgia ton tokenizers gia kathe glossa
class CTokenizer(BaseTokenizer):

    @property
    def keywords(self):
        return _C_KEYWORDS

    def strip_comments(self, source: str) -> str:
        source = re.sub(r'/\*.*?\*/', ' ', source, flags=re.DOTALL)
        source = re.sub(r'//.*?$', ' ', source, flags=re.MULTILINE)
        return source

    def strip_structural_noise(self, source: str) -> str:
        source = re.sub(r'^\s*#.*?$', ' ', source, flags=re.MULTILINE)
        return source


class CppTokenizer(CTokenizer):

    @property
    def keywords(self):
        return _CPP_KEYWORDS


class CSharpTokenizer(BaseTokenizer):

    @property
    def keywords(self):
        return _CSHARP_KEYWORDS

    def strip_comments(self, source: str) -> str:
        source = re.sub(r'/\*.*?\*/', ' ', source, flags=re.DOTALL)
        source = re.sub(r'//.*?$', ' ', source, flags=re.MULTILINE)
        return source

    def strip_structural_noise(self, source: str) -> str:
        source = re.sub(r'^\s*using\s+[^;]+;', ' ', source, flags=re.MULTILINE)
        source = re.sub(r'\[.*?\]', ' ', source, flags=re.DOTALL)
        return source


class JavaTokenizer(BaseTokenizer):

    @property
    def keywords(self):
        return _JAVA_KEYWORDS

    def strip_comments(self, source: str) -> str:
        source = re.sub(r'/\*.*?\*/', ' ', source, flags=re.DOTALL)
        source = re.sub(r'//.*?$', ' ', source, flags=re.MULTILINE)
        return source

    def strip_structural_noise(self, source: str) -> str:
        source = re.sub(r'^\s*import\s+[^;]+;', ' ', source, flags=re.MULTILINE)
        source = re.sub(r'^\s*package\s+[^;]+;', ' ', source, flags=re.MULTILINE)
        source = re.sub(r'@\w+(?:\([^)]*\))?', ' ', source)
        return source


class PythonTokenizer(BaseTokenizer):

    @property
    def keywords(self):
        return frozenset(keyword.kwlist) | frozenset(["True", "False", "None"])

    def strip_comments(self, source: str) -> str:
        return source

    def tokenize(self, source: str) -> list:
        result = []
        kws = self.keywords
        try:
            gen = _tokenize.generate_tokens(io.StringIO(source).readline)
            for tok_type, tok_str, *_ in gen:
                if tok_type in (_tokenize.COMMENT, _tokenize.NEWLINE,
                                _tokenize.NL, _tokenize.INDENT,
                                _tokenize.DEDENT, _tokenize.ENCODING,
                                _tokenize.ENDMARKER):
                    continue
                elif tok_type == _tokenize.NAME:
                    result.append(tok_str if tok_str in kws else "ID")
                elif tok_type == _tokenize.NUMBER:
                    result.append("NUM")
                elif tok_type == _tokenize.STRING:
                    result.append("STR")
                elif tok_type == _tokenize.OP:
                    result.append(tok_str)
        except _tokenize.TokenError:
            pass
        return result


class JavaScriptTokenizer(BaseTokenizer):

    @property
    def keywords(self):
        return _JS_KEYWORDS

    def strip_comments(self, source: str) -> str:
        source = re.sub(r'/\*.*?\*/', ' ', source, flags=re.DOTALL)
        source = re.sub(r'//.*?$', ' ', source, flags=re.MULTILINE)
        return source

    def _normalize(self, raw_tokens: list) -> list:
        result = []
        prev_meaningful = None
        _regex_triggers = {
            'return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete',
            'throw', 'case', 'void', '=', '(', '[', '{', ',', ';',
            '!', '&', '|', '?', ':', '+', '-', '*', '/', '%',
        }
        i = 0
        while i < len(raw_tokens):
            tok = raw_tokens[i]
            if tok == '/' and (prev_meaningful is None or prev_meaningful in _regex_triggers):
                result.append("REGEX")
                i += 1
                while i < len(raw_tokens) and raw_tokens[i] != '/':
                    i += 1
                i += 1
                prev_meaningful = "REGEX"
                continue

            if tok in self.keywords:
                result.append(tok)
                prev_meaningful = tok
            elif re.fullmatch(r'[A-Za-z_$]\w*', tok):
                result.append("ID")
                prev_meaningful = "ID"
            elif re.fullmatch(r'0[xX][0-9A-Fa-f]+|[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?', tok):
                result.append("NUM")
                prev_meaningful = "NUM"
            elif tok.startswith('"') or tok.startswith("'") or tok.startswith('`'):
                result.append("STR")
                prev_meaningful = "STR"
            elif tok.strip():
                result.append(tok)
                prev_meaningful = tok
            i += 1
        return result


_TOKENIZER_MAP = {
    "C":          CTokenizer,
    "C++":        CppTokenizer,
    "C#":         CSharpTokenizer,
    "Java":       JavaTokenizer,
    "Python":     PythonTokenizer,
    "JavaScript": JavaScriptTokenizer,
}

LANGUAGE_EXTENSIONS = {
    "C":          [".c", ".h"],
    "C++":        [".cpp", ".cxx", ".cc", ".hpp", ".hxx"],
    "C#":         [".cs"],
    "Java":       [".java"],
    "Python":     [".py"],
    "JavaScript": [".js", ".mjs", ".cjs"],
}
#factory method
#epistrefei enan working tokenizer h kanei catch error gia na xrisimopoihthei sto analyze.py 
def get_tokenizer(language: str) -> BaseTokenizer:
    cls = _TOKENIZER_MAP.get(language)
    if cls is None:
        raise ValueError(f"Unsupported language: {language}")
    return cls()
