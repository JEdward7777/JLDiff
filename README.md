# JLDiff
Character by character diff script written in python producing html output.

This uses the [Longest common subsequence algorithm](https://en.wikipedia.org/wiki/Longest_common_subsequence_problem)

It is executed as such

`JLDiff.py a.txt b.txt out.html`

The result is in html with red and green coloring.  Larger files do exponentually take a longer amount of time to process but this does a true character by character comparison without checking line by line first.
