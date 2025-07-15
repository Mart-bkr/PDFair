# Installation guide (WSL)

## Sudo installs
```console
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
sudo apt install tesseract-ocr-nld
sudo apt-get install poppler-utils
```

## Create conda environment
```console
conda env create --name YourEnvName --file=environment.yml
python -m spacy download nl_core_news_sm
```

## Update environment (only needed when updating `environment.yml`)
```console
conda env update --name YourEnvName --file environment.yml --prune
```

## Activate environment
```console
conda activate YourEnvName
```