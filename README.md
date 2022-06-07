Nationally Determined Contributions (NDCs) as provided in the UNFCCC
secreteriat's
[NDC registry](https://unfccc.int/NDCREG).

[![Daily Update](https://github.com/openclimatedata/ndcs/workflows/Daily%20Update/badge.svg)](https://github.com/openclimatedata/ndcs/actions)

## Data

NDCs are available in the [NDC registry](https://unfccc.int/NDCREG).
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

See also the UNFCCC's [NDC page](https://unfccc.int/process-and-meetings/the-paris-agreement/nationally-determined-contributions-ndcs/nationally-determined-contributions-ndcs)
for background information and information on updates of the dataset.

## License

The Python files in `scripts` are released under an
[CC0 Public Dedication License](https://creativecommons.org/publicdomain/zero/1.0/).
