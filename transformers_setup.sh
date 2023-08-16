#!/bin/bash

echo y | conda create -n bertopic_gpu python=3.7 anaconda
conda init bash
eval "$(conda shell.bash hook)"
conda activate bertopic_gpu
pip install torch==1.2.0 torchvision==0.4.0
pip install transformers
pip install -U sentence-transformers
pip install bertopic
pip install simpletransformers
pip install bertviz
pip install datasets
pip install scikit-multilearn --upgrade
pip install nlpaug
pip install sacrebleu
pip install rouge_score
pip install py7zr
pip install tner
pip install mysql-connector
pip install spacy-language-detection
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0.tar.gz
echo y | conda install -c anaconda ipykernel
python -m ipykernel install --user --name=bertopic_gpu
apt update
apt install git-lfs -y