tutorial_tests = """
Let's try a simple generator:

    >>> def f():
    ...    yield 1
    ...    yield 2

    >>> for i in f():
    ...     print i
    1
    2
    >>> g = f()
    >>> g.next()
    1
    >>> g.next()
    2

"Falling off the end" stops the generator:

    >>> g.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "<stdin>", line 2, in g
    StopIteration

"return" also stops the generator:

    >>> def f():
    ...     yield 1
    ...     return
    ...     yield 2 # never reached
    ...
    >>> g = f()
    >>> g.next()
    1
    >>> g.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "<stdin>", line 3, in f
    StopIteration
    >>> g.next() # once stopped, can't be resumed
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    StopIteration

"raise StopIteration" stops the generator too:

    >>> def f():
    ...     yield 1
    ...     raise StopIteration
    ...     yield 2 # never reached
    ...
    >>> g = f()
    >>> g.next()
    1
    >>> g.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    StopIteration
    >>> g.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    StopIteration

However, they are not exactly equivalent:

    >>> def g1():
    ...     try:
    ...         return
    ...     except:
    ...         yield 1
    ...
    >>> list(g1())
    []

    >>> def g2():
    ...     try:
    ...         raise StopIteration
    ...     except:
    ...         yield 42
    >>> print list(g2())
    [42]

This may be surprising at first:

    >>> def g3():
    ...     try:
    ...         return
    ...     finally:
    ...         yield 1
    ...
    >>> list(g3())
    [1]

Let's create an alternate range() function implemented as a generator:

    >>> def yrange(n):
    ...     for i in range(n):
    ...         yield i
    ...
    >>> list(yrange(5))
    [0, 1, 2, 3, 4]

Generators always return to the most recent caller:

    >>> def creator():
    ...     r = yrange(5)
    ...     print "creator", r.next()
    ...     return r
    ...
    >>> def caller():
    ...     r = creator()
    ...     for i in r:
    ...             print "caller", i
    ...
    >>> caller()
    creator 0
    caller 1
    caller 2
    caller 3
    caller 4

Generators can call other generators:

    >>> def zrange(n):
    ...     for i in yrange(n):
    ...         yield i
    ...
    >>> list(zrange(5))
    [0, 1, 2, 3, 4]

"""

# The examples from PEP 255.

pep_tests = """

Specification:  Yield

    Restriction:  A generator cannot be resumed while it is actively
    running:

    >>> def g():
    ...     i = me.next()
    ...     yield i
    >>> me = g()
    >>> me.next()
    Traceback (most recent call last):
     ...
      File "<string>", line 2, in g
    ValueError: generator already executing

Specification: Return

    Note that return isn't always equivalent to raising StopIteration:  the
    difference lies in how enclosing try/except constructs are treated.
    For example,

        >>> def f1():
        ...     try:
        ...         return
        ...     except:
        ...        yield 1
        >>> print list(f1())
        []

    because, as in any function, return simply exits, but

        >>> def f2():
        ...     try:
        ...         raise StopIteration
        ...     except:
        ...         yield 42
        >>> print list(f2())
        [42]

    because StopIteration is captured by a bare "except", as is any
    exception.

Specification: Generators and Exception Propagation

    >>> def f():
    ...     return 1//0
    >>> def g():
    ...     yield f()  # the zero division exception propagates
    ...     yield 42   # and we'll never get here
    >>> k = g()
    >>> k.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "<stdin>", line 2, in g
      File "<stdin>", line 2, in f
    ZeroDivisionError: integer division or modulo by zero
    >>> k.next()  # and the generator cannot be resumed
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    StopIteration
    >>>

Specification: Try/Except/Finally

    >>> def f():
    ...     try:
    ...         yield 1
    ...         try:
    ...             yield 2
    ...             1//0
    ...             yield 3  # never get here
    ...         except ZeroDivisionError:
    ...             yield 4
    ...             yield 5
    ...             raise
    ...         except:
    ...             yield 6
    ...         yield 7     # the "raise" above stops this
    ...     except:
    ...         yield 8
    ...     yield 9
    ...     try:
    ...         x = 12
    ...     finally:
    ...         yield 10
    ...     yield 11
    >>> print list(f())
    [1, 2, 4, 5, 8, 9, 10, 11]
    >>>

Guido's binary tree example.

    >>> # A binary tree class.
    >>> class Tree:
    ...
    ...     def __init__(self, label, left=None, right=None):
    ...         self.label = label
    ...         self.left = left
    ...         self.right = right
    ...
    ...     def __repr__(self, level=0, indent="    "):
    ...         s = level*indent + repr(self.label)
    ...         if self.left:
    ...             s = s + "\\n" + self.left.__repr__(level+1, indent)
    ...         if self.right:
    ...             s = s + "\\n" + self.right.__repr__(level+1, indent)
    ...         return s
    ...
    ...     def __iter__(self):
    ...         return inorder(self)

    >>> # Create a Tree from a list.
    >>> def tree(list):
    ...     n = len(list)
    ...     if n == 0:
    ...         return []
    ...     i = n // 2
    ...     return Tree(list[i], tree(list[:i]), tree(list[i+1:]))

    >>> # Show it off: create a tree.
    >>> t = tree("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    >>> # A recursive generator that generates Tree labels in in-order.
    >>> def inorder(t):
    ...     if t:
    ...         for x in inorder(t.left):
    ...             yield x
    ...         yield t.label
    ...         for x in inorder(t.right):
    ...             yield x

    >>> # Show it off: create a tree.
    >>> t = tree("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    >>> # Print the nodes of the tree in in-order.
    >>> for x in t:
    ...     print x,
    A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

    >>> # A non-recursive generator.
    >>> def inorder(node):
    ...     stack = []
    ...     while node:
    ...         while node.left:
    ...             stack.append(node)
    ...             node = node.left
    ...         yield node.label
    ...         while not node.right:
    ...             try:
    ...                 node = stack.pop()
    ...             except IndexError:
    ...                 return
    ...             yield node.label
    ...         node = node.right

    >>> # Exercise the non-recursive generator.
    >>> for x in t:
    ...     print x,
    A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

"""

# Examples from Iterator-List and Python-Dev and c.l.py.

email_tests = """

The difference between yielding None and returning it.

>>> def g():
...     for i in range(3):
...         yield None
...     yield None
...     return
>>> list(g())
[None, None, None, None]

Ensure that explicitly raising StopIteration acts like any other exception
in try/except, not like a return.

>>> def g():
...     yield 1
...     try:
...         raise StopIteration
...     except:
...         yield 2
...     yield 3
>>> list(g())
[1, 2, 3]

Next one was posted to c.l.py.

>>> def gcomb(x, k):
...     "Generate all combinations of k elements from list x."
...
...     if k > len(x):
...         return
...     if k == 0:
...         yield []
...     else:
...         first, rest = x[0], x[1:]
...         # A combination does or doesn't contain first.
...         # If it does, the remainder is a k-1 comb of rest.
...         for c in gcomb(rest, k-1):
...             c.insert(0, first)
...             yield c
...         # If it doesn't contain first, it's a k comb of rest.
...         for c in gcomb(rest, k):
...             yield c

>>> seq = range(1, 5)
>>> for k in range(len(seq) + 2):
...     print "%d-combs of %s:" % (k, seq)
...     for c in gcomb(seq, k):
...         print "   ", c
0-combs of [1, 2, 3, 4]:
    []
1-combs of [1, 2, 3, 4]:
    [1]
    [2]
    [3]
    [4]
2-combs of [1, 2, 3, 4]:
    [1, 2]
    [1, 3]
    [1, 4]
    [2, 3]
    [2, 4]
    [3, 4]
3-combs of [1, 2, 3, 4]:
    [1, 2, 3]
    [1, 2, 4]
    [1, 3, 4]
    [2, 3, 4]
4-combs of [1, 2, 3, 4]:
    [1, 2, 3, 4]
5-combs of [1, 2, 3, 4]:

From the Iterators list, about the types of these things.

>>> def g():
...     yield 1
...
>>> type(g)
<type 'function'>
>>> i = g()
>>> type(i)
<type 'generator'>
>>> [s for s in dir(i) if not s.startswith('_')]
['gi_frame', 'gi_running', 'next']
>>> print i.next.__doc__
x.next() -> the next value, or raise StopIteration
>>> iter(i) is i
True
>>> import types
>>> isinstance(i, types.GeneratorType)
True

And more, added later.

>>> i.gi_running
0
>>> type(i.gi_frame)
<type 'frame'>
>>> i.gi_running = 42
Traceback (most recent call last):
  ...
TypeError: readonly attribute
>>> def g():
...     yield me.gi_running
>>> me = g()
>>> me.gi_running
0
>>> me.next()
1
>>> me.gi_running
0

A clever union-find implementation from c.l.py, due to David Eppstein.
Sent: Friday, June 29, 2001 12:16 PM
To: python-list@python.org
Subject: Re: PEP 255: Simple Generators

>>> class disjointSet:
...     def __init__(self, name):
...         self.name = name
...         self.parent = None
...         self.generator = self.generate()
...
...     def generate(self):
...         while not self.parent:
...             yield self
...         for x in self.parent.generator:
...             yield x
...
...     def find(self):
...         return self.generator.next()
...
...     def union(self, parent):
...         if self.parent:
...             raise ValueError("Sorry, I'm not a root!")
...         self.parent = parent
...
...     def __str__(self):
...         return self.name

>>> names = "ABCDEFGHIJKLM"
>>> sets = [disjointSet(name) for name in names]
>>> roots = sets[:]

>>> import random
>>> gen = random.WichmannHill(42)
>>> while 1:
...     for s in sets:
...         print "%s->%s" % (s, s.find()),
...     print
...     if len(roots) > 1:
...         s1 = gen.choice(roots)
...         roots.remove(s1)
...         s2 = gen.choice(roots)
...         s1.union(s2)
...         print "merged", s1, "into", s2
...     else:
...         break
A->A B->B C->C D->D E->E F->F G->G H->H I->I J->J K->K L->L M->M
merged D into G
A->A B->B C->C D->G E->E F->F G->G H->H I->I J->J K->K L->L M->M
merged C into F
A->A B->B C->F D->G E->E F->F G->G H->H I->I J->J K->K L->L M->M
merged L into A
A->A B->B C->F D->G E->E F->F G->G H->H I->I J->J K->K L->A M->M
merged H into E
A->A B->B C->F D->G E->E F->F G->G H->E I->I J->J K->K L->A M->M
merged B into E
A->A B->E C->F D->G E->E F->F G->G H->E I->I J->J K->K L->A M->M
merged J into G
A->A B->E C->F D->G E->E F->F G->G H->E I->I J->G K->K L->A M->M
merged E into G
A->A B->G C->F D->G E->G F->F G->G H->G I->I J->G K->K L->A M->M
merged M into G
A->A B->G C->F D->G E->G F->F G->G H->G I->I J->G K->K L->A M->G
merged I into K
A->A B->G C->F D->G E->G F->F G->G H->G I->K J->G K->K L->A M->G
merged K into A
A->A B->G C->F D->G E->G F->F G->G H->G I->A J->G K->A L->A M->G
merged F into A
A->A B->G C->A D->G E->G F->A G->G H->G I->A J->G K->A L->A M->G
merged A into G
A->G B->G C->G D->G E->G F->G G->G H->G I->G J->G K->G L->G M->G
"""
# Emacs turd '

# Fun tests (for sufficiently warped notions of "fun").

fun_tests = """

Build up to a recursive Sieve of Eratosthenes generator.

>>> def firstn(g, n):
...     return [g.next() for i in range(n)]

>>> def intsfrom(i):
...     while 1:
...         yield i
...         i += 1

>>> firstn(intsfrom(5), 7)
[5, 6, 7, 8, 9, 10, 11]

>>> def exclude_multiples(n, ints):
...     for i in ints:
...         if i % n:
...             yield i

>>> firstn(exclude_multiples(3, intsfrom(1)), 6)
[1, 2, 4, 5, 7, 8]

>>> def sieve(ints):
...     prime = ints.next()
...     yield prime
...     not_divisible_by_prime = exclude_multiples(prime, ints)
...     for p in sieve(not_divisible_by_prime):
...         yield p

>>> primes = sieve(intsfrom(2))
>>> firstn(primes, 20)
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]


Another famous problem:  generate all integers of the form
    2**i * 3**j  * 5**k
in increasing order, where i,j,k >= 0.  Trickier than it may look at first!
Try writing it without generators, and correctly, and without generating
3 internal results for each result output.

>>> def times(n, g):
...     for i in g:
...         yield n * i
>>> firstn(times(10, intsfrom(1)), 10)
[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

>>> def merge(g, h):
...     ng = g.next()
...     nh = h.next()
...     while 1:
...         if ng < nh:
...             yield ng
...             ng = g.next()
...         elif ng > nh:
...             yield nh
...             nh = h.next()
...         else:
...             yield ng
...             ng = g.next()
...             nh = h.next()

The following works, but is doing a whale of a lot of redundant work --
it's not clear how to get the internal uses of m235 to share a single
generator.  Note that me_times2 (etc) each need to see every element in the
result sequence.  So this is an example where lazy lists are more natural
(you can look at the head of a lazy list any number of times).

>>> def m235():
...     yield 1
...     me_times2 = times(2, m235())
...     me_times3 = times(3, m235())
...     me_times5 = times(5, m235())
...     for i in merge(merge(me_times2,
...                          me_times3),
...                    me_times5):
...         yield i

Don't print "too many" of these -- the implementation above is extremely
inefficient:  each call of m235() leads to 3 recursive calls, and in
turn each of those 3 more, and so on, and so on, until we've descended
enough levels to satisfy the print stmts.  Very odd:  when I printed 5
lines of results below, this managed to screw up Win98's malloc in "the
usual" way, i.e. the heap grew over 4Mb so Win98 started fragmenting
address space, and it *looked* like a very slow leak.

>>> result = m235()
>>> for i in range(3):
...     print firstn(result, 15)
[1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24]
[25, 27, 30, 32, 36, 40, 45, 48, 50, 54, 60, 64, 72, 75, 80]
[81, 90, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 162, 180, 192]

Heh.  Here's one way to get a shared list, complete with an excruciating
namespace renaming trick.  The *pretty* part is that the times() and merge()
functions can be reused as-is, because they only assume their stream
arguments are iterable -- a LazyList is the same as a generator to times().

>>> class LazyList:
...     def __init__(self, g):
...         self.sofar = []
...         self.fetch = g.next
...
...     def __getitem__(self, i):
...         sofar, fetch = self.sofar, self.fetch
...         while i >= len(sofar):
...             sofar.append(fetch())
...         return sofar[i]

>>> def m235():
...     yield 1
...     # Gack:  m235 below actually refers to a LazyList.
...     me_times2 = times(2, m235)
...     me_times3 = times(3, m235)
...     me_times5 = times(5, m235)
...     for i in merge(merge(me_times2,
...                          me_times3),
...                    me_times5):
...         yield i

Print as many of these as you like -- *this* implementation is memory-
efficient.

>>> m235 = LazyList(m235())
>>> for i in range(5):
...     print [m235[j] for j in range(15*i, 15*(i+1))]
[1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24]
[25, 27, 30, 32, 36, 40, 45, 48, 50, 54, 60, 64, 72, 75, 80]
[81, 90, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 162, 180, 192]
[200, 216, 225, 240, 243, 250, 256, 270, 288, 300, 320, 324, 360, 375, 384]
[400, 405, 432, 450, 480, 486, 500, 512, 540, 576, 600, 625, 640, 648, 675]


Ye olde Fibonacci generator, LazyList style.

>>> def fibgen(a, b):
...
...     def sum(g, h):
...         while 1:
...             yield g.next() + h.next()
...
...     def tail(g):
...         g.next()    # throw first away
...         for x in g:
...             yield x
...
...     yield a
...     yield b
...     for s in sum(iter(fib),
...                  tail(iter(fib))):
...         yield s

>>> fib = LazyList(fibgen(1, 2))
>>> firstn(iter(fib), 17)
[1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584]
"""

# syntax_tests mostly provokes SyntaxErrors.  Also fiddling with #if 0
# hackery.

syntax_tests = """

>>> def f():
...     return 22
...     yield 1
Traceback (most recent call last):
  ..
SyntaxError: 'return' with argument inside generator (<doctest test.test_generators.syntax[0]>, line 2)

>>> def f():
...     yield 1
...     return 22
Traceback (most recent call last):
  ..
SyntaxError: 'return' with argument inside generator (<doctest test.test_generators.syntax[1]>, line 3)

"return None" is not the same as "return" in a generator:

>>> def f():
...     yield 1
...     return None
Traceback (most recent call last):
  ..
SyntaxError: 'return' with argument inside generator (<doctest test.test_generators.syntax[2]>, line 3)

This one is fine:

>>> def f():
...     yield 1
...     return

>>> def f():
...     try:
...         yield 1
...     finally:
...         pass
Traceback (most recent call last):
  ..
SyntaxError: 'yield' not allowed in a 'try' block with a 'finally' clause (<doctest test.test_generators.syntax[4]>, line 3)

>>> def f():
...     try:
...         try:
...             1//0
...         except ZeroDivisionError:
...             yield 666  # bad because *outer* try has finally
...         except:
...             pass
...     finally:
...         pass
Traceback (most recent call last):
  ...
SyntaxError: 'yield' not allowed in a 'try' block with a 'finally' clause (<doctest test.test_generators.syntax[5]>, line 6)

But this is fine:

>>> def f():
...     try:
...         try:
...             yield 12
...             1//0
...         except ZeroDivisionError:
...             yield 666
...         except:
...             try:
...                 x = 12
...             finally:
...                 yield 12
...     except:
...         return
>>> list(f())
[12, 666]

>>> def f():
...    yield
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> def f():
...    if 0:
...        yield
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> def f():
...     if 0:
...         yield 1
>>> type(f())
<type 'generator'>

>>> def f():
...    if "":
...        yield None
>>> type(f())
<type 'generator'>

>>> def f():
...     return
...     try:
...         if x==4:
...             pass
...         elif 0:
...             try:
...                 1//0
...             except SyntaxError:
...                 pass
...             else:
...                 if 0:
...                     while 12:
...                         x += 1
...                         yield 2 # don't blink
...                         f(a, b, c, d, e)
...         else:
...             pass
...     except:
...         x = 1
...     return
>>> type(f())
<type 'generator'>

>>> def f():
...     if 0:
...         def g():
...             yield 1
...
>>> type(f())
<type 'NoneType'>

>>> def f():
...     if 0:
...         class C:
...             def __init__(self):
...                 yield 1
...             def f(self):
...                 yield 2
>>> type(f())
<type 'NoneType'>

>>> def f():
...     if 0:
...         return
...     if 0:
...         yield 2
>>> type(f())
<type 'generator'>


>>> def f():
...     if 0:
...         lambda x:  x        # shouldn't trigger here
...         return              # or here
...         def f(i):
...             return 2*i      # or here
...         if 0:
...             return 3        # but *this* sucks (line 8)
...     if 0:
...         yield 2             # because it's a generator
Traceback (most recent call last):
SyntaxError: 'return' with argument inside generator (<doctest test.test_generators.syntax[22]>, line 8)

This one caused a crash (see SF bug 567538):

>>> def f():
...     for i in range(3):
...         try:
...             continue
...         finally:
...             yield i
...
>>> g = f()
>>> print g.next()
0
>>> print g.next()
1
>>> print g.next()
2
>>> print g.next()
Traceback (most recent call last):
StopIteration
"""

# conjoin is a simple backtracking generator, named in honor of Icon's
# "conjunction" control structure.  Pass a list of no-argument functions
# that return iterable objects.  Easiest to explain by example:  assume the
# function list [x, y, z] is passed.  Then conjoin acts like:
#
# def g():
#     values = [None] * 3
#     for values[0] in x():
#         for values[1] in y():
#             for values[2] in z():
#                 yield values
#
# So some 3-lists of values *may* be generated, each time we successfully
# get into the innermost loop.  If an iterator fails (is exhausted) before
# then, it "backtracks" to get the next value from the nearest enclosing
# iterator (the one "to the left"), and starts all over again at the next
# slot (pumps a fresh iterator).  Of course this is most useful when the
# iterators have side-effects, so that which values *can* be generated at
# each slot depend on the values iterated at previous slots.

def conjoin(gs):

    values = [None] * len(gs)

    def gen(i, values=values):
        if i >= len(gs):
            yield values
        else:
            for values[i] in gs[i]():
                for x in gen(i+1):
                    yield x

    for x in gen(0):
        yield x

# That works fine, but recursing a level and checking i against len(gs) for
# each item produced is inefficient.  By doing manual loop unrolling across
# generator boundaries, it's possible to eliminate most of that overhead.
# This isn't worth the bother *in general* for generators, but conjoin() is
# a core building block for some CPU-intensive generator applications.

def conjoin(gs):

    n = len(gs)
    values = [None] * n

    # Do one loop nest at time recursively, until the # of loop nests
    # remaining is divisible by 3.

    def gen(i, values=values):
        if i >= n:
            yield values

        elif (n-i) % 3:
            ip1 = i+1
            for values[i] in gs[i]():
                for x in gen(ip1):
                    yield x

        else:
            for x in _gen3(i):
                yield x

    # Do three loop nests at a time, recursing only if at least three more
    # remain.  Don't call directly:  this is an internal optimization for
    # gen's use.

    def _gen3(i, values=values):
        assert i < n and (n-i) % 3 == 0
        ip1, ip2, ip3 = i+1, i+2, i+3
        g, g1, g2 = gs[i : ip3]

        if ip3 >= n:
            # These are the last three, so we can yield values directly.
            for values[i] in g():
                for values[ip1] in g1():
                    for values[ip2] in g2():
                        yield values

        else:
            # At least 6 loop nests remain; peel off 3 and recurse for the
            # rest.
            for values[i] in g():
                for values[ip1] in g1():
                    for values[ip2] in g2():
                        for x in _gen3(ip3):
                            yield x

    for x in gen(0):
        yield x

# And one more approach:  For backtracking apps like the Knight's Tour
# solver below, the number of backtracking levels can be enormous (one
# level per square, for the Knight's Tour, so that e.g. a 100x100 board
# needs 10,000 levels).  In such cases Python is likely to run out of
# stack space due to recursion.  So here's a recursion-free version of
# conjoin too.
# NOTE WELL:  This allows large problems to be solved with only trivial
# demands on stack space.  Without explicitly resumable generators, this is
# much harder to achieve.  OTOH, this is much slower (up to a factor of 2)
# than the fancy unrolled recursive conjoin.

def flat_conjoin(gs):  # rename to conjoin to run tests with this instead
    n = len(gs)
    values = [None] * n
    iters  = [None] * n
    _StopIteration = StopIteration  # make local because caught a *lot*
    i = 0
    while 1:
        # Descend.
        try:
            while i < n:
                it = iters[i] = gs[i]().next
                values[i] = it()
                i += 1
        except _StopIteration:
            pass
        else:
            assert i == n
            yield values

        # Backtrack until an older iterator can be resumed.
        i -= 1
        while i >= 0:
            try:
                values[i] = iters[i]()
                # Success!  Start fresh at next level.
                i += 1
                break
            except _StopIteration:
                # Continue backtracking.
                i -= 1
        else:
            assert i < 0
            break

# A conjoin-based N-Queens solver.

class Queens:
    def __init__(self, n):
        self.n = n
        rangen = range(n)

        # Assign a unique int to each column and diagonal.
        # columns:  n of those, range(n).
        # NW-SE diagonals: 2n-1 of these, i-j unique and invariant along
        # each, smallest i-j is 0-(n-1) = 1-n, so add n-1 to shift to 0-
        # based.
        # NE-SW diagonals: 2n-1 of these, i+j unique and invariant along
        # each, smallest i+j is 0, largest is 2n-2.

        # For each square, compute a bit vector of the columns and
        # diagonals it covers, and for each row compute a function that
        # generates the possiblities for the columns in that row.
        self.rowgenerators = []
        for i in rangen:
            rowuses = [(1L << j) |                  # column ordinal
                       (1L << (n + i-j + n-1)) |    # NW-SE ordinal
                       (1L << (n + 2*n-1 + i+j))    # NE-SW ordinal
                            for j in rangen]

            def rowgen(rowuses=rowuses):
                for j in rangen:
                    uses = rowuses[j]
                    if uses & self.used == 0:
                        self.used |= uses
                        yield j
                        self.used &= ~uses

            self.rowgenerators.append(rowgen)

    # Generate solutions.
    def solve(self):
        self.used = 0
        for row2col in conjoin(self.rowgenerators):
            yield row2col

    def printsolution(self, row2col):
        n = self.n
        assert n == len(row2col)
        sep = "+" + "-+" * n
        print sep
        for i in range(n):
            squares = [" " for j in range(n)]
            squares[row2col[i]] = "Q"
            print "|" + "|".join(squares) + "|"
            print sep

# A conjoin-based Knight's Tour solver.  This is pretty sophisticated
# (e.g., when used with flat_conjoin above, and passing hard=1 to the
# constructor, a 200x200 Knight's Tour was found quickly -- note that we're
# creating 10s of thousands of generators then!), and is lengthy.

class Knights:
    def __init__(self, m, n, hard=0):
        self.m, self.n = m, n

        # solve() will set up succs[i] to be a list of square #i's
        # successors.
        succs = self.succs = []

        # Remove i0 from each of its successor's successor lists, i.e.
        # successors can't go back to i0 again.  Return 0 if we can
        # detect this makes a solution impossible, else return 1.

        def remove_from_successors(i0, len=len):
            # If we remove all exits from a free square, we're dead:
            # even if we move to it next, we can't leave it again.
            # If we create a square with one exit, we must visit it next;
            # else somebody else will have to visit it, and since there's
            # only one adjacent, there won't be a way to leave it again.
            # Finelly, if we create more than one free square with a
            # single exit, we can only move to one of them next, leaving
            # the other one a dead end.
            ne0 = ne1 = 0
            for i in succs[i0]:
                s = succs[i]
                s.remove(i0)
                e = len(s)
                if e == 0:
                    ne0 += 1
                elif e == 1:
                    ne1 += 1
            return ne0 == 0 and ne1 < 2

        # Put i0 back in each of its successor's successor lists.

        def add_to_successors(i0):
            for i in succs[i0]:
                succs[i].append(i0)

        # Generate the first move.
        def first():
            if m < 1 or n < 1:
                return

            # Since we're looking for a cycle, it doesn't matter where we
            # start.  Starting in a corner makes the 2nd move easy.
            corner = self.coords2index(0, 0)
            remove_from_successors(corner)
            self.lastij = corner
            yield corner
            add_to_successors(corner)

        # Generate the second moves.
        def second():
            corner = self.coords2index(0, 0)
            assert self.lastij == corner  # i.e., we started in the corner
            if m < 3 or n < 3:
                return
            assert len(succs[corner]) == 2
            assert self.coords2index(1, 2) in succs[corner]
            assert self.coords2index(2, 1) in succs[corner]
            # Only two choices.  Whichever we pick, the other must be the
            # square picked on move m*n, as it's the only way to get back
            # to (0, 0).  Save its index in self.final so that moves before
            # the last know it must be kept free.
            for i, j in (1, 2), (2, 1):
                this  = self.coords2index(i, j)
                final = self.coords2index(3-i, 3-j)
                self.final = final

                remove_from_successors(this)
                succs[final].append(corner)
                self.lastij = this
                yield this
                succs[final].remove(corner)
                add_to_successors(this)

        # Generate moves 3 thru m*n-1.
        def advance(len=len):
            # If some successor has only one exit, must take it.
            # Else favor successors with fewer exits.
            candidates = []
            for i in succs[self.lastij]:
                e = len(succs[i])
                assert e > 0, "else remove_from_successors() pruning flawed"
                if e == 1:
                    candidates = [(e, i)]
                    break
                candidates.append((e, i))
            else:
                candidates.sort()

            for e, i in candidates:
                if i != self.final:
                    if remove_from_successors(i):
                        self.lastij = i
                        yield i
                    add_to_successors(i)

        # Generate moves 3 thru m*n-1.  Alternative version using a
        # stronger (but more expensive) heuristic to order successors.
        # Since the # of backtracking levels is m*n, a poor move early on
        # can take eons to undo.  Smallest square board for which this
        # matters a lot is 52x52.
        def advance_hard(vmid=(m-1)/2.0, hmid=(n-1)/2.0, len=len):
            # If some successor has only one exit, must take it.
            # Else favor successors with fewer exits.
            # Break ties via max distance from board centerpoint (favor
            # corners and edges whenever possible).
            candidates = []
            for i in succs[self.lastij]:
                e = len(succs[i])
                assert e > 0, "else remove_from_successors() pruning flawed"
                if e == 1:
                    candidates = [(e, 0, i)]
                    break
                i1, j1 = self.index2coords(i)
                d = (i1 - vmid)**2 + (j1 - hmid)**2
                candidates.append((e, -d, i))
            else:
                candidates.sort()

            for e, d, i in candidates:
                if i != self.final:
                    if remove_from_successors(i):
                        self.lastij = i
                        yield i
                    add_to_successors(i)

        # Generate the last move.
        def last():
            assert self.final in succs[self.lastij]
            yield self.final

        if m*n < 4:
            self.squaregenerators = [first]
        else:
            self.squaregenerators = [first, second] + \
                [hard and advance_hard or advance] * (m*n - 3) + \
                [last]

    def coords2index(self, i, j):
        assert 0 <= i < self.m
        assert 0 <= j < self.n
        return i * self.n + j

    def index2coords(self, index):
        assert 0 <= index < self.m * self.n
        return divmod(index, self.n)

    def _init_board(self):
        succs = self.succs
        del succs[:]
        m, n = self.m, self.n
        c2i = self.coords2index

        offsets = [( 1,  2), ( 2,  1), ( 2, -1), ( 1, -2),
                   (-1, -2), (-2, -1), (-2,  1), (-1,  2)]
        rangen = range(n)
        for i in range(m):
            for j in rangen:
                s = [c2i(i+io, j+jo) for io, jo in offsets
                                     if 0 <= i+io < m and
                                        0 <= j+jo < n]
                succs.append(s)

    # Generate solutions.
    def solve(self):
        self._init_board()
        for x in conjoin(self.squaregenerators):
            yield x

    def printsolution(self, x):
        m, n = self.m, self.n
        assert len(x) == m*n
        w = len(str(m*n))
        format = "%" + str(w) + "d"

        squares = [[None] * n for i in range(m)]
        k = 1
        for i in x:
            i1, j1 = self.index2coords(i)
            squares[i1][j1] = format % k
            k += 1

        sep = "+" + ("-" * w + "+") * n
        print sep
        for i in range(m):
            row = squares[i]
            print "|" + "|".join(row) + "|"
            print sep

conjoin_tests = """

Generate the 3-bit binary numbers in order.  This illustrates dumbest-
possible use of conjoin, just to generate the full cross-product.

>>> for c in conjoin([lambda: iter((0, 1))] * 3):
...     print c
[0, 0, 0]
[0, 0, 1]
[0, 1, 0]
[0, 1, 1]
[1, 0, 0]
[1, 0, 1]
[1, 1, 0]
[1, 1, 1]

For efficiency in typical backtracking apps, conjoin() yields the same list
object each time.  So if you want to save away a full account of its
generated sequence, you need to copy its results.

>>> def gencopy(iterator):
...     for x in iterator:
...         yield x[:]

>>> for n in range(10):
...     all = list(gencopy(conjoin([lambda: iter((0, 1))] * n)))
...     print n, len(all), all[0] == [0] * n, all[-1] == [1] * n
0 1 True True
1 2 True True
2 4 True True
3 8 True True
4 16 True True
5 32 True True
6 64 True True
7 128 True True
8 256 True True
9 512 True True

And run an 8-queens solver.

>>> q = Queens(8)
>>> LIMIT = 2
>>> count = 0
>>> for row2col in q.solve():
...     count += 1
...     if count <= LIMIT:
...         print "Solution", count
...         q.printsolution(row2col)
Solution 1
+-+-+-+-+-+-+-+-+
|Q| | | | | | | |
+-+-+-+-+-+-+-+-+
| | | | |Q| | | |
+-+-+-+-+-+-+-+-+
| | | | | | | |Q|
+-+-+-+-+-+-+-+-+
| | | | | |Q| | |
+-+-+-+-+-+-+-+-+
| | |Q| | | | | |
+-+-+-+-+-+-+-+-+
| | | | | | |Q| |
+-+-+-+-+-+-+-+-+
| |Q| | | | | | |
+-+-+-+-+-+-+-+-+
| | | |Q| | | | |
+-+-+-+-+-+-+-+-+
Solution 2
+-+-+-+-+-+-+-+-+
|Q| | | | | | | |
+-+-+-+-+-+-+-+-+
| | | | | |Q| | |
+-+-+-+-+-+-+-+-+
| | | | | | | |Q|
+-+-+-+-+-+-+-+-+
| | |Q| | | | | |
+-+-+-+-+-+-+-+-+
| | | | | | |Q| |
+-+-+-+-+-+-+-+-+
| | | |Q| | | | |
+-+-+-+-+-+-+-+-+
| |Q| | | | | | |
+-+-+-+-+-+-+-+-+
| | | | |Q| | | |
+-+-+-+-+-+-+-+-+

>>> print count, "solutions in all."
92 solutions in all.

And run a Knight's Tour on a 10x10 board.  Note that there are about
20,000 solutions even on a 6x6 board, so don't dare run this to exhaustion.

>>> k = Knights(10, 10)
>>> LIMIT = 2
>>> count = 0
>>> for x in k.solve():
...     count += 1
...     if count <= LIMIT:
...         print "Solution", count
...         k.printsolution(x)
...     else:
...         break
Solution 1
+---+---+---+---+---+---+---+---+---+---+
|  1| 58| 27| 34|  3| 40| 29| 10|  5|  8|
+---+---+---+---+---+---+---+---+---+---+
| 26| 35|  2| 57| 28| 33|  4|  7| 30| 11|
+---+---+---+---+---+---+---+---+---+---+
| 59|100| 73| 36| 41| 56| 39| 32|  9|  6|
+---+---+---+---+---+---+---+---+---+---+
| 74| 25| 60| 55| 72| 37| 42| 49| 12| 31|
+---+---+---+---+---+---+---+---+---+---+
| 61| 86| 99| 76| 63| 52| 47| 38| 43| 50|
+---+---+---+---+---+---+---+---+---+---+
| 24| 75| 62| 85| 54| 71| 64| 51| 48| 13|
+---+---+---+---+---+---+---+---+---+---+
| 87| 98| 91| 80| 77| 84| 53| 46| 65| 44|
+---+---+---+---+---+---+---+---+---+---+
| 90| 23| 88| 95| 70| 79| 68| 83| 14| 17|
+---+---+---+---+---+---+---+---+---+---+
| 97| 92| 21| 78| 81| 94| 19| 16| 45| 66|
+---+---+---+---+---+---+---+---+---+---+
| 22| 89| 96| 93| 20| 69| 82| 67| 18| 15|
+---+---+---+---+---+---+---+---+---+---+
Solution 2
+---+---+---+---+---+---+---+---+---+---+
|  1| 58| 27| 34|  3| 40| 29| 10|  5|  8|
+---+---+---+---+---+---+---+---+---+---+
| 26| 35|  2| 57| 28| 33|  4|  7| 30| 11|
+---+---+---+---+---+---+---+---+---+---+
| 59|100| 73| 36| 41| 56| 39| 32|  9|  6|
+---+---+---+---+---+---+---+---+---+---+
| 74| 25| 60| 55| 72| 37| 42| 49| 12| 31|
+---+---+---+---+---+---+---+---+---+---+
| 61| 86| 99| 76| 63| 52| 47| 38| 43| 50|
+---+---+---+---+---+---+---+---+---+---+
| 24| 75| 62| 85| 54| 71| 64| 51| 48| 13|
+---+---+---+---+---+---+---+---+---+---+
| 87| 98| 89| 80| 77| 84| 53| 46| 65| 44|
+---+---+---+---+---+---+---+---+---+---+
| 90| 23| 92| 95| 70| 79| 68| 83| 14| 17|
+---+---+---+---+---+---+---+---+---+---+
| 97| 88| 21| 78| 81| 94| 19| 16| 45| 66|
+---+---+---+---+---+---+---+---+---+---+
| 22| 91| 96| 93| 20| 69| 82| 67| 18| 15|
+---+---+---+---+---+---+---+---+---+---+
"""

weakref_tests = """\
Generators are weakly referencable:

>>> import weakref
>>> def gen():
...     yield 'foo!'
...
>>> wr = weakref.ref(gen)
>>> wr() is gen
True
>>> p = weakref.proxy(gen)

Generator-iterators are weakly referencable as well:

>>> gi = gen()
>>> wr = weakref.ref(gi)
>>> wr() is gi
True
>>> p = weakref.proxy(gi)
>>> list(p)
['foo!']

"""

__test__ = {"tut":      tutorial_tests,
            "pep":      pep_tests,
            "email":    email_tests,
            "fun":      fun_tests,
            "syntax":   syntax_tests,
            "conjoin":  conjoin_tests,
            "weakref":  weakref_tests,
            }

# Magic test name that regrtest.py invokes *after* importing this module.
# This worms around a bootstrap problem.
# Note that doctest and regrtest both look in sys.argv for a "-v" argument,
# so this works as expected in both ways of running regrtest.
def test_main(verbose=None):
    from test import test_support, test_generators
    test_support.run_doctest(test_generators, verbose)

# This part isn't needed for regrtest, but for running the test directly.
if __name__ == "__main__":
    test_main(1)
