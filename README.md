Nationally Determined Contributions (NDCs) as provided in the UNFCCC
secreteriat's interim
[NDC registry](http://www4.unfccc.int/ndcregistry/Pages/Home.aspx).

[![Daily Update](https://github.com/openclimatedata/ndcs/workflows/Daily%20Update/badge.svg)](https://github.com/openclimatedata/ndcs/actions)

## Data

NDCs are available on the interim [NDC registry](http://www4.unfccc.int/ndcregistry/Pages/Home.aspx).
A [CSV file](data/ndcs.csv) is created with title, kind of document, URL of the
original document etc. For convenience all documents are downloaded and saved with
unified filenames in the `pdfs` directory.

## Preparation

Run

    make

to fetch the latest list of NDCs,

    make download

to download the documents into `pdfs`.

## Requirements

Python3 is used, all dependencies are installed automatically into a Virtualenv
when using the `Makefile`.

## Notes

See the UNFCCC's [NDC page](http://unfccc.int/focus/ndc_registry/items/9433.php)
for background information and updates of the dataset.

## License

The Python files in `scripts` are released under an
[CC0 Public Dedication License](https://creativecommons.org/publicdomain/zero/1.0/).
