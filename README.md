# PoS-visualization
A textual visualization of Proof-of-Stake (PoS) blockchains.

We present an adversarial strategy which attacks 
the consistency property of PoS blockchain protocols 
under the longest-chain rule 
in the eventual consensus paradigm, such as 
Ouroboros, Ouroboros Praos, and Snow White. 
This adversarial strategy is described and analyzed in 
https://eprint.iacr.org/2017/241.pdf.

## Background
Rounds in a blockchain protocol execution can be labeled 
as either adversarial or honest. 
Thus we can think of a blockchain execution of ``n`` rounds on 
an ``n``-bit Boolean string ``w``; 
this string is called a _characteristic string_.

In a Proof-of-Stake blockchain execution, 
an honest round can yield a single block whereas 
an adversarial round can yield zero, one, or more blocks. 
Each block builds upon a previous block; hence the entire 
execution looks like a rooted tree. 
This tree is called the _fork_ and each root-to-leaf path 
(i.e., each blockchain) is called a _tine_. 
A tine is _honest_ if it ends at a block generated at an honest round; 
otherwise, it is _adversarial_.
A tine is _competitive_ if it is at least as long as 
the longest honest tine. 
The honest tines follow the _longest-chain rule_, i.e., 
they always build on a competitive tine.

In this repository, 
we build an adversarial strategy which attacks 
the consistency property of the blockchain protocol. 
That is, it creates forks with 
competitive tines that diverge long ago. 
This adversarial strategy is described and analyzed in 
https://eprint.iacr.org/2017/241.pdf.



## Example code
Please refer to ``test.py`` for detailed examples.

```
$ ./optfork.py -w 1101100110110110 -a branching
Using adv: branching
Using w: 1101100110110110 n: 16

===== Fork on w = 1101100110110110 (16 bits) =====
----Tines (3)----
tine (*)------(3)------(6)(7)
tine (*)------(3)------(6)---[8]---(10)
tine (*)------(3)------(6)---[8][9]------------(13)--------(16)
```
Here, the node `(*)` is the root node and it is considered honest. 
The `0`-bits in `w` correspond to honest rounds; 
the `1`-bits correspond to adversarial rounds. 
There are three tines. In each tine, 
blocks from an honest round `h` are marked as `(h)` and the 
blocks from an adversarial round `a` are marked as `[a]`. 

Below are the full specification of the file ``optfork.py``.

```
$ ./optfork.py --help

Options:
  -h, --help            show this help message and exit
  -a ADV, --adversary=ADV
                        adversary type, one of ['opt', 'branching',
                        'revealing', 'toofluffy']
  -w W, --w=W           characteristic string, should end with a 0
  -r, --random          use a random string of N bits
  -n N, --n=N           use a random string of N bits
  -x D, --max-delete-blocks=D
                        delete X blocks from the end of non-longest tines
  -p SPLIT_PROB, --split-prob=SPLIT_PROB
                        splitting probability
  -d, --diagnostics     show diagnostics
  -s, --stats           show stats
  -m, --matrix          show matrix
  -t, --tines           show tines
  -v, --verbose         verbose
  -e, --diag-verbose    verbose
  -l, --double          verbose
  -b BREAK_TIE, --break-tie=BREAK_TIE
                        tie-breaking basis, one of [None, 'slot', 'reach']

```

