### To Test

Locally:
```sh
python3 -m unittest
```

Docker:
```sh
docker run -it --rm -v "$PWD":/tmp/app -w /tmp/app python:3 python3 -m unittest
```

### To Run(Problem 1)

Locally:
```sh
./problem_1.py --spec tests/test_data/spec.json tests/test_data/input.file
# Or
cat tests/test_data/input.file | ./problem_1.py --spec tests/test_data/spec.json
```

Docker:
```sh
docker run -it --rm -v "$PWD":/tmp/app -w /tmp/app python:3 ./problem_1.py --spec tests/test_data/spec.json tests/test_data/input.file
# Or
docker run -it --rm -v "$PWD":/tmp/app -w /tmp/app python:3 cat tests/test_data/input.file | ./problem_1.py --spec tests/test_data/spec.json
```

### To Run(Problem 2)
Locally:
```sh
./problem_2.py
```

Docker:
```sh
docker run -it --rm -v "$PWD":/tmp/app -w /tmp/app python:3 ./problem_2.py
```

At Scale(~2g)
```sh
/usr/bin/time -l ./problem_2.py 500000
```

Running across a few different sized datasets we can see that the ram usage stays constant
at ~12mb, ie our memory usage is O(1), basically just the python interpreter
and a few buffers used for file IO, so for larger datasets we're not limited by
ram just disk space in which to store the results and time.

To minimise the run time we can scale out by using many processes either on a single machine
or across many (using a distributed processing framework).
Either way the underlying approach is the same. The input dataset is divided into many "splits"
and each split is processed independantly by a copy of the code.

However....

The cost(in terms of extra code or managing distributed compute frameworks) has to be weighed up
against the "cost" of using a faster language/runtime. Python and Ruby standout as being particularly slow,
in my experience it's not unusual to see a speedup of 100x by switching to a faster language
which may sidestep the need to distribute the workloads.  My personal favourite here is rust
but the jvm(java/kotlin), go or even node.js might be better options given a particular
organisation. 