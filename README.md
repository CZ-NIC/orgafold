# Orgafold

[![Build Status](https://github.com/CZ-NIC/orgafold/actions/workflows/run-unittest.yml/badge.svg)](https://github.com/CZ-NIC/orgafold/actions)

Quickly navigate through a high number of files, perhaps obtained after a disk recovery.

Have you ever found yourself in a situation where there were 100,000 files in a folder, and you needed to make sense of them? Orgafold can help you determine how much space files with a specific extension, mimetype, or date take up. Alternatively, it can assist you in organizing them into folders if the existing directory structure lacks meaning. Never overwrites a file, appending a counter.

```
SOURCE '/src', TARGET '/target'
/src/blah1/file1 -> /target/2019/file1
/src/blah1/file2 -> /target/2019/file2
/src/blah2/file1 -> /target/2019/file1 (2)
/src/blah2/foo/file3 -> /target/2019/foo/file3
```

See `orgafold --help` for complete help.

# Installation
Install with a single command from [PyPi](https://pypi.org/project/orgafold/)

```bash
pip3 install orgafold
```

# Examples

Aggregate by file suffixes.

```
$ orgafold . --suffix
Analysis: suffix
351× .arw 7.7 GB
6× .indd 1.9 GB
136× .jpg 1.0 GB
4× .tif 525.5 MB
27× .pages 71.2 MB
33× .numbers 23.7 MB
10× .pdf 17.8 MB
2× .png 11.2 MB
2× .doc 1.5 MB
1× .docx 499.5 kB
4× .xlsx 122.9 kB
1× .xml 3.0 kB
```

Aggregate by the mime type.

```
$ orgafold . --mime
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 597/597 [00:26<00:00, 22.60it/s]
Analysis: mime
493× image 9.3 GB
83× application 2.0 GB
4× text 4.5 kB
```

Aggregate by file suffixes and their modification year.

```
$ orgafold . --suffix --year
Analysis: suffix year
276× .arw 2016 6.2 GB
1× .indd 2015 1.9 GB
54× .arw 2014 1.1 GB
34× .jpg 2015 678.7 MB
4× .tif 2015 525.5 MB
16× .arw 2012 332.6 MB
39× .jpg 2014 212.3 MB
57× .jpg 2016 136.3 MB
20× .pages 2016 67.3 MB
```

Dry-run, copying into folder structure, given by the year and suffix.

```
$ orgafold . --suffix --year --copy --output ~/tidy --dry --recursive
Dry run only
Would copy Untitled-1.pdf → ~/tidy/2016-pdf/Untitled-1.pdf
Would copy Untitled-2.pdf → ~/tidy/2016-pdf/Untitled-2.pdf
Would copy log2.pages → ~/tidy/2016-pages/log2.pages
Would copy log3.pages → ~/tidy/2016-pages/log3.pages
Would copy memories.indd → ~/tidy/2015-indd/memories.indd
Would copy log1.pages → ~/tidy/2016-pages/log1.pages
Would copy ymca.doc → ~/tidy/2014-doc/ymca.doc
Would copy Untitled-3.pdf → ~/tidy/2016-pdf/Untitled-3.pdf
Would copy other papers/cool.xlsx → ~/tidy/2016-xlsx/cool.xlsx
Would copy other papers/workload (2).numbers → ~/tidy/2016-numbers/workload (2).numbers
Would copy other papers/jnh-lo.jpg → ~/tidy/2016-jpg/jnh-lo.jpg
```