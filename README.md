# JLDiff

Character by character diff script written in Python producing HTML output.

This uses the [Longest common subsequence algorithm](https://en.wikipedia.org/wiki/Longest_common_subsequence_problem) to do a true character-by-character comparison — no line-by-line preprocessing. The result is HTML with red and green coloring showing exactly what changed.

> **Note:** Larger files take exponentially longer to process due to the nature of the algorithm.

## Installation

### As a library in another project

```bash
# With uv
uv pip install git+https://github.com/JEdward7777/JLDiff.git

# With pip
pip install git+https://github.com/JEdward7777/JLDiff.git
```

### Run as a one-off CLI without installing

```bash
uv run --from git+https://github.com/JEdward7777/JLDiff.git jldiff file1.txt file2.txt out.html
```

## Usage

### Command line

```bash
jldiff file1.txt file2.txt out.html [--same_size]
```

The `--same_size` flag keeps diff text the same size as surrounding text (by default, changed text is rendered larger for visibility).

### As a library

```python
from JLDiff import compute_diff, printDiffs

result = compute_diff("hello world", "hallo world", talk=False)
```

The `compute_diff` function takes two strings and returns a list of diff nodes. Each node has a `.state` (`STATE_MATCH`, `STATE_PASSING_1ST`, or `STATE_PASSING_2ND`) and a `.content` character. Set `talk=False` to suppress progress output to stdout.

Use `printDiffs(result, output_file)` to write the diff as HTML spans to a file-like object.

## License

BSD 2-Clause — see [LICENSE](LICENSE) for details.
