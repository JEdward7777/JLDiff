# JLDiff

Character by character diff script written in Python producing HTML output — with optional word-level diffing.

This uses the [Longest common subsequence algorithm](https://en.wikipedia.org/wiki/Longest_common_subsequence_problem) to do a true character-by-character comparison — no line-by-line preprocessing. The result is HTML with red and green coloring showing exactly what changed.

A `--word_level` mode tokenizes input into words, whitespace, and punctuation, then diffs at the token level for cleaner, faster results on natural language text.

> **Note:** Larger files take exponentially longer to process due to the nature of the algorithm. Word-level mode significantly reduces processing time by operating on tokens instead of individual characters.

## Installation

### From PyPI

```bash
pip install JLDiff
```

### From GitHub (development version)

```bash
# With uv
uv pip install git+https://github.com/JEdward7777/JLDiff.git

# With pip
pip install git+https://github.com/JEdward7777/JLDiff.git
```

### Run as a one-off CLI without installing

```bash
# From PyPI
uvx jldiff file1.txt file2.txt out.html

# From GitHub
uv run --from git+https://github.com/JEdward7777/JLDiff.git jldiff file1.txt file2.txt out.html
```

## Usage

### Command line

```bash
jldiff file1.txt file2.txt out.html [--same_size] [--word_level]
```

| Flag | Description |
|------|-------------|
| `--same_size` | Keep diff text the same size as surrounding text (by default, changed text is rendered larger for visibility). |
| `--word_level` | Diff at the token level instead of character level. Tokens are groups of alphabetical characters, whitespace, or other characters. Produces cleaner whole-word diffs and runs significantly faster on large files. |

### As a library

#### Character-level diff (default)

```python
from JLDiff import compute_diff, printDiffs

result = compute_diff("hello world", "hallo world", talk=False)
```

The `compute_diff` function takes two strings and returns a list of diff nodes. Each node has a `.state` (`STATE_MATCH`, `STATE_PASSING_1ST`, or `STATE_PASSING_2ND`) and a `.content` character. Set `talk=False` to suppress progress output to stdout.

Use `printDiffs(result, output_file)` to write the diff as HTML spans to a file-like object. `printDiffs` accepts both character-level and token-level diff output — it automatically flattens token-level nodes to characters via `flatten_diff`.

#### Word-level diff

```python
from JLDiff import compute_diff_by_words, printDiffs

# Token-level diff — each node's .content is a whole token (e.g. "hello", " ", "world")
result = compute_diff_by_words("The quick brown fox", "The slow brown cat", talk=False)

# printDiffs handles flattening automatically
with open("out.html", "w") as f:
    printDiffs(result, f)
```

`compute_diff_by_words` returns the **unflattened** token-level diff, so you can inspect which tokens changed:

```python
for node in result:
    if node.state != STATE_MATCH and node.content:
        print(f"Changed token: {node.content!r}")
```

#### Custom character classes

By default, tokenization uses three character classes: alphabetical (`str.isalpha`), whitespace (`str.isspace`), and everything else. You can provide a custom classifier function:

```python
from JLDiff import compute_diff_by_words, tokenize

# Classifier that treats digits as their own class
def my_classifier(ch):
    if ch.isalpha():
        return 'alpha'
    elif ch.isdigit():
        return 'digit'
    elif ch.isspace():
        return 'space'
    else:
        return 'other'

result = compute_diff_by_words(text1, text2, talk=False, classifier=my_classifier)

# Or use tokenize directly for full control
tokens = tokenize("hello123 world", classifier=my_classifier)
# ['hello', '123', ' ', 'world']
```

#### Building blocks

For maximum control, use the individual functions:

```python
from JLDiff import tokenize, compute_diff, flatten_diff, printDiffs

# 1. Tokenize
tokens1 = tokenize(text1)
tokens2 = tokenize(text2)

# 2. Diff on tokens (compute_diff works on any sequence of comparable elements)
token_diff = compute_diff(tokens1, tokens2, talk=False)

# 3. Inspect token-level results directly
for node in token_diff:
    print(node.state, repr(node.content))

# 4. Or flatten to character-level for HTML output
char_nodes = list(flatten_diff(token_diff))
```

`flatten_diff` is a generator that expands multi-character content nodes into single-character nodes. It's a transparent passthrough for character-level diffs (zero overhead).

## License

BSD 2-Clause — see [LICENSE](LICENSE) for details.
