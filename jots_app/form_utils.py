"""
form utilities
"""
""" validation functions """
from unicodedata import normalize

def standarize_titles(s):
    s = normalize('NFKD', s.upper().lower().title())
    for old, new in [(" The ", " the "), (" And ", " and "),
                        (" Of ", " of "), (" For ", " for "),
                        (" To ", " to "), (" In ", " in "),
                        (" At ", " at "), (" From ", " from "),
                        (" A ", " a "), (" An ", " an "),
                        (" As ", " as "), (" But ", " but "),
                        (" By ", " by "), (" If ", " if "),
                        (" Or ", " or "), ("'S ", "'s "),]:
        s = s.replace(old, new)
    return s

def escape(s):
    """
    Escape special characters.

    https://github.com/jacebrowning/memegen#special-characters
    """
    s.strip()
    for old, new in [("-", "--"), ("_", "__"), ("?", "~q"),
                    ("%", "~p"), ("#", "~h"), ("/", " AKA "), 
                    ("\"", "''"), ("<", " is less than "),
                    (">", " is greater than "), ("=", " equals "),
                    ("s =", "s equal "), ("s =", "s equal "),
                    (".", " ")]:
        s = s.replace(old, new)
    return s

fanc_pants_border = 'border-color:darkgoldenrod; border-radius: 15px;'

example_markdown = """ # Largest heading
###### smallest heading

Separate paragraphs with blank lines. This is one paragraph.

This is a second paragraph.

### Advanced Formatting:

*italicize text like this*
**make text bold like this** 

* Item 1 of a list.
* Item 2 of a list. Note the space after the *.

Want a meme, or an image?
![alt text](imageurl)

A working example: 
![octo cat, the mighty](https://myoctocat.com/assets/images/base-octocat.svg)
"""
