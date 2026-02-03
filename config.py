from typing import *

MHS,HST,RCT = 'MHS','HST','RCT'
QXP,MXP = 'QXP','MXP'

# CONSTANT ALGORITHM GROUPS
INCOMPLETE_ALGS = (QXP, MXP)
BASE_ALGS = (MHS, HST, RCT)
HYBRID_ALGS = tuple((f'{alg}-{MXP}' for alg in BASE_ALGS))
COMPLETE_ALGS = (*BASE_ALGS, *HYBRID_ALGS)
USEFUL_ALGS = COMPLETE_ALGS + (MXP,)
ALL_ALGS = USEFUL_ALGS + (QXP,)
COMPARE_ALGS = (MHS, 'MHS-MXP', 'original MHS', 'original MHS-MXP')
MHS_OPT = ('MHS-MXP', *(f'MHS-MXP opt{i}' for i in range(1,5)))
HST_OPT = ('HST-MXP', *(f'HST-MXP opt{i}' for i in range(1,5)))
RCT_OPT = ('RCT-MXP', *(f'RCT-MXP opt{i}' for i in range(1,5)))
OPT1 = tuple(f'{alg}-MXP opt1' for alg in BASE_ALGS)
OPT2 = tuple(f'{alg}-MXP opt2' for alg in BASE_ALGS)
OPT3 = tuple(f'{alg}-MXP opt3' for alg in BASE_ALGS)
OPT4 = tuple(f'{alg}-MXP opt4' for alg in BASE_ALGS)
OPT1_12_BASE = (f'{alg}-MXP{opt}' for alg in BASE_ALGS for opt in ('', ' opt1',' opt12'))
OPT1_12 = (f'{alg}-MXP{opt}' for alg in BASE_ALGS for opt in (' opt1',' opt12'))
OPT14_124_BASE = (f'{alg}-MXP{opt}' for alg in BASE_ALGS for opt in ('', ' opt14',' opt124'))
OPT14_124 = (f'{alg}-MXP{opt}' for alg in BASE_ALGS for opt in (' opt14',' opt124'))
MHS_OPT_neg_combi = ('MHS-MXP', *(f'MHS-MXP opt{i}' for i in (1,2,4,14,124)))
HST_OPT_neg_combi = ('HST-MXP', *(f'HST-MXP opt{i}' for i in (1,4,14)))
RCT_OPT_neg_combi = ('RCT-MXP', *(f'RCT-MXP opt{i}' for i in (1,2,4,14,124)))
MHS_OPT_noneg_combi = ('MHS-MXP', *(f'MHS-MXP opt{i}' for i in (1,2,12,)))
HST_OPT_noneg_combi = ('HST-MXP', *(f'HST-MXP opt{i}' for i in (2,12,)))
RCT_OPT_noneg_combi = ('RCT-MXP', *(f'RCT-MXP opt{i}' for i in (1,2,12,)))

class Config:

    def __init__(self):

        # LOGS FILEPATHS
        self.logs_dir = "*"  # e.g. logs, ., ...
        self.ontology_dir = "*"  # e.g. *, lubm-0, family, ...
        self.input_dir = "*"  # e.g. *_noneg, lubm-0_1*, lubm-0_5*_neg, ...
        self.filename = "*"
        self.ignore_default_path_structure = False

        # PROCESSED LOG DATA FILEPATHS
        self.output_dir = '.'
        self.output_filename_prefix = ''
        self.output_filename_postfix = ''

        # LOG PROCESSING
        self.algs = []

        # PLOT FILEPATHS
        self.data_dir = '.'
        self.export_dir = '.'

        # PLOT VISUALS
        self.plot_line_width = 3
        self.plot_mark_size = 10
        self.plot_visuals = {
            MHS : ('o','red'),
            'original MHS': ('h', 'mediumturquoise'),
            'MHS-MXP': ('s', 'maroon'),
            'original MHS-MXP': ('D', 'teal'),
            HST: ('o','royalblue'),
            'HST-MXP': ('s', 'mediumblue'),
            RCT: ('o','lime'),
            'RCT-MXP': ('s', 'forestgreen'),
            QXP: ('v', 'darkorange'),
            MXP: ('^','magenta'),

            'MHS-MXP opt1': ('$C$', 'firebrick'),
            'MHS-MXP opt2': ('$S$', 'chocolate'),
            'MHS-MXP opt3': ('$P$', 'orangered'),
            'MHS-MXP opt4': ('$T$', 'tomato'),

            'MHS-MXP opt12': ('$CS$', 'peru'),
            'MHS-MXP-opt': ('*', 'crimson'),
            'MHS-MXP opt14': ('$CT$', 'saddlebrown'),
            'MHS-MXP opt124': ('$CST$', 'coral'),

            'HST-MXP opt1': ('$C$', 'navy'),
            'HST-MXP opt2': ('$S$', 'dodgerblue'),
            'HST-MXP opt3': ('$P$', 'darkorchid'),
            'HST-MXP opt4': ('$T$', 'slateblue'),

            'HST-MXP opt12': ('$CS$', 'hotpink'),
            'HST-MXP-opt': ('*', 'dodgerblue'),
            'HST-MXP opt14': ('$CT$', 'fuchsia'),
            'HST-MXP opt124': ('$CST$', 'mediumpurple'),

            'RCT-MXP opt1': ('$C$', 'chartreuse'),
            'RCT-MXP opt2': ('$S$', 'yellowgreen'),
            'RCT-MXP opt3': ('$P$', 'seagreen'),
            'RCT-MXP opt4': ('$T$', 'springgreen'),

            'RCT-MXP opt12': ('$CS$', 'lightseagreen'),
            'RCT-MXP-opt': ('*', 'lawngreen'),
            'RCT-MXP opt14': ('$CT$', 'mediumaquamarine'),
            'RCT-MXP opt124': ('$CST$', 'olivedrab'),
        }

        # PLOT EXPORT
        self.x_label = ''
        self.y_label = ''
        self.title = ''
        self.export_width = 9
        self.export_height = 7
        self.export_extensions = {'png', 'pdf'}

    def update(self, updated_values : dict[str,Any] ):
        for variable, value in updated_values.items():
            if value is not None:
                setattr(self, variable, value)

    def get_plot_marker(self, alg : str) -> str:
        return self.plot_visuals[alg][0]

    def get_plot_color(self, alg : str) -> str:
        return self.plot_visuals[alg][1]

def alg_uses_filtering(alg_name : str) -> bool:
    return alg_name not in BASE_ALGS

config = Config()

