#!/usr/bin/env python

# ----------------------
# Copyright 2023 PMG Lab
# Author: Lin Miao
# Licence: MIT
# Version: 20230825
# ----------------------

import argparse
import pandas as pd
from settings import *

parser = argparse.ArgumentParser(description='Plot results of 2.repeat_quantitative_gcta.sh')
parser.add_argument('--prefix', type=str, required=True, help='Prefix of the inputs and outputs')
parser.add_argument('--h2g', type=str, required=True, help='Target h2g for the simulation')
parser.add_argument('--neg-alpha', type=str, required=True, help='Power value in the LDAK-Thin Model')
parser.add_argument('--pqtl-vals', type=str, required=True, help='Proprotion values of SNPs to be qtlal')

args = parser.parse_args()
h2f = float(args.h2g)
pqtl_list = args.pqtl_vals.split(',')
programs = ['GCTA'] + programs

results = dict()
for pq in pqtl_list:
    df = pd.read_csv(f'{args.prefix}.pqtl{pq}_alpha-{args.neg_alpha}_h2g{args.h2g}.one32th.tsv',
                     sep='\t', header=[0, 1, 2], index_col=0)
    df.loc[:, ('SumHer', slice(None), ['se_mean', 'se_mrb'])] = np.nan
    results[pq] = df

ncol = len(pqtl_list)
nrow = len(est_ylabel)
abc = np.array(list('ABCDEFGHIJKL')).reshape(nrow, ncol)

figsize = (12, 9)
fig, ax = plt.subplots(nrow, ncol, figsize=figsize, sharex=True, sharey=False)
fig.subplots_adjust(left=0.07, bottom=0.03, right=0.99, top=0.99, wspace=0, hspace=0.1)

x = np.arange(len(programs), dtype=float)
bp = dict()
for i, (est, ylabel) in enumerate(est_ylabel.items()):
    print(f'Plotting h2={args.h2g}, {est} ...')

    for j, pq in enumerate(pqtl_list):
        for u in [0, 1, 2]:
            xs = x + s[u]
            bp[u] = ax[i, j].boxplot(results[pq].loc[:, (programs, R[u], est)], positions=xs,
                                     boxprops=dict(facecolor=C[u], lw=lw), **bp_style)
            if results[pq].loc[:, ('LDER', R[u], est)].isnull().sum() > 0:
                ax[i, j].boxplot(results[pq].loc[:, ('LDER', R[u], est)].dropna(), positions=xs[-1:],
                                 boxprops=dict(facecolor=C[u], lw=lw), **bp_style)

        if i == 0:
            ax[i, j].text(s=f'{abc[i, j]}. Pr(QTL)$={pq}, α=-{args.neg_alpha}$',
                          transform=ax[i, j].transAxes, **text_bbox)
        else:
            ax[i, j].text(s=f'{abc[i, j]}', transform=ax[i, j].transAxes, **text_bbox)

        if i == nrow - 1:
            ax[i, j].set_xticks(x)
            ax[i, j].set_xticklabels(programs)
        else:
            ax[i, j].tick_params(
                axis='x',  # changes apply to the x-axis
                which='both',  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                labelbottom=False
            )  # labels along the bottom edge are off

        if j == 0:
            ax[i, j].set_ylabel(ylabel)
            if est == 'h2_mean' or est == 'h2_sd':
                if est == 'h2_mean':
                    ax[i, j].set_ylim(-h2f / 4, h2f * 3.3)
                elif est == 'h2_sd':
                    ax[i, j].set_ylim(0, h2f * 2.4)
                yticks = ax[i, j].get_yticks()
                yticklabels = [f'{a * 100:.2f}%' for a in yticks]
                ax[i, j].set_yticks(yticks)
                ax[i, j].set_yticklabels(yticklabels)
        else:
            ax[i, j].set_yticklabels([])

        if est == 'h2_mean':
            ax[i, j].set_ylim(-h2f / 3, h2f * 2.9)
            ax[i, j].hlines(h2f, xmin=x[0] - 0.5, xmax=x[-1] + .5, colors='gray', linestyles='dashed', lw=1)
        elif est == 'h2_sd':
            ax[i, j].set_ylim(0, h2f * 1.99)
        elif est == 'h2_mrb':
            ax[i, j].set_ylim(-1.4, 1.9)
            ax[i, j].hlines(0, xmin=x[0] - 0.5, xmax=x[-1] + .5, colors='gray', linestyles='dashed', lw=1)
        elif est == 'se_mrb':
            ax[i, j].set_ylim(-1.2, 2.7)
            ax[i, j].hlines(0, xmin=x[0] - 0.5, xmax=x[-1] + .5, colors='gray', linestyles='dashed', lw=1)

ax[0, 2].legend([bp[0]['boxes'][0], bp[1]['boxes'][0], bp[2]['boxes'][0]], legend_label,
                title=legend_title, loc='upper right', labelspacing=0.2)
fig.savefig(f'{args.prefix}.alpha-{args.neg_alpha}_h2g{args.h2g}.png')
plt.close()
