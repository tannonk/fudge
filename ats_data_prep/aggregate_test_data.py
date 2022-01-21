#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gathers simplification test data for experiments

The following datasets are used

    - TURK test (Xu et al. 2016) 
        - https://cocoxu.github.io/publications/tacl2016-smt-simplification.pdf)
        - https://huggingface.co/datasets/turk
    
    - Newsela (Xu et al. 2015)
        - https://aclanthology.org/Q15-1021.pdf
        - aligned sentences collected from
          newsela_articles_*.aligned.sents.txt and
          aggregated by tgt level

"""

import random
from pathlib import Path
import argparse
from datasets import load_dataset
import pandas as pd
# from nltk.tokenize.moses import MosesDetokenizer
from sacremoses import MosesDetokenizer

SEED = 23

def set_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', '--outpath', type=str, required=True, help='path to directory to save validation and test sets')
    ap.add_argument('--datasets', type=str, nargs='+', required=False, default=['turk', 'newsela'])
    ap.add_argument('--newsela_path', default='/srv/scratch6/kew/ats/data/en/newsela_article_corpus_2016-01-29/newsela_data_share-20150302/', help='path to newsela_data_share directory containing newsela_articles_*.aligned.sents.txt.')
    return ap.parse_args()

def save_turk_to_disk(out_dir):
    """
    Downloads the TURK corpus (crowdsourced simplifications for
    sentences taken from Simple Wikipedia) from huggingface
    datasets library and saves the validation (2000)
    and test (359) items to tsv files.

    Each item in TURK has 8 manually written,
    crowdsourced simplifications.
    All simplifications are separated by tab char

    """
    turk = load_dataset("turk")
    
    for split in turk.keys():
        # initialise outfile
        outfile = Path(out_dir) / f'turk_{split}.tsv'
        with open(outfile, 'w', encoding='utf8') as f:
            for item in turk[split]:
                src = item['original']
                tgts = '\t'.join(item['simplifications'])
                f.write(f'{src}\t{tgts}\n')
    
        print(f'TURK {split} saved to disk ({outfile})')

    return
    
def save_newsela_to_disk(newsela_path, outpath, detok=True, tgt_levels=['V1', 'V2', 'V3', 'V4']):
    """
    aligned sentences from Newsela are expected to be 
    """
    
    md = None
    if detok: 
        md = MosesDetokenizer(lang='en')
    
    aligned_sents = Path(newsela_path) / 'newsela_articles_20150302.aligned.sents.txt'

    for tgt_level in tgt_levels:
        c = 0
        outfile = Path(outpath) / f'newsela_v0_{tgt_level}.tsv'
        with open(aligned_sents, 'r', encoding='utf8') as inf:
            with open(outfile, 'w', encoding='utf8') as outf:
                for line in inf:
                    doc_id, src_v, tgt_v, src_text, tgt_text = line.strip().split('\t')
                    if src_v == 'V0' and tgt_v == tgt_level:
                        if md is not None:
                            src_text = md.detokenize(src_text.split())
                            tgt_text = md.detokenize(tgt_text.split())
                        outf.write(f'{src_text.strip()}\t{tgt_text.strip()}\n')
                        c += 1
        print(f'NEWSELA V0-{tgt_level} ({c} items) saved to disk ({outfile})')

if __name__ == '__main__':
    args = set_args()

    Path(args.outpath).mkdir(parents=True, exist_ok=True)
    # breakpoint()
    if 'turk' in args.datasets:
        save_turk_to_disk(args.outpath)

    if 'newsela' in args.datasets:
        save_newsela_to_disk(args.newsela_path, args.outpath)