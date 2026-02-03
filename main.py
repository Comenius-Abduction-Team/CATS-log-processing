import config as cfg
import process_logs as log
import plot_logs as plot
import generic_funcs as generic

if __name__ == '__main__':

    NEG_VALS_LIST = [
        ( False, 'noneg', 'no negations'), # negacie
        ( True, 'neg', 'negations'), # bez negacii
        ( None, '*', 'all') #vsetky vstupy
    ]
    'pomocna struktura, pouzivam na nastavovanie ake typy logov chceme spracovat'

    NEG_VALS = NEG_VALS_LIST[1:2]
    '''
        - opat len pomocna konstanta, ktora sa neskor pouziva na zadavanie parametrov, co sa casto opakuju v metodach
        - v tomto pripade chceme prejst vsetky druhy, takze zoberiem cely zoznam
        - ak by sme chceli napr. len negacie, dame sem [0:1]
    '''

    log.set_algs(generic.zip_seq(cfg.HYBRID_ALGS, cfg.OPT4))
    '''
    - nastavenie, ktor algoritmy chceme mat v tabulke/grafe... v subore config.py su ako konstanty rozne zoznamy algoritmov
    - v tomto pripade - HYBRID_ALGS su vsetky 3 hybridne algoritmy, OPT1 su tie iste ale s optimalazicaiou 1
    - JE TO POSTAVENE NA NAZVOCH PRIECINKOV, KTORE SA POTOM POUZIJU AJ AKO NAZVY STLPCOV V TABULKE
    '''

    log.ignore_default_path_structure(True)
    '''
    - defaultne sa rata s rovnakou hierarchiou suborov, ako maju logy v CATS...
        cize root-log-suborov/'algoritmus'/'bk onto'/'input subor'/tu uz su tie logy samotne
    - subory z evalvacie optimalizacii som si supol inam, tak treba povedat, aby sa nepouzila default cesta
    
        - ak by sa pouzila default struktura cesty, pomocou funkcie log.set_logs_path() sa daju nastavit jednotlive casti cesty
        - napr:
            
            # log.set_logs_path(alg='MHS-MXP', ontology='onto_priecinok')
                - nastavi algoritmus a nazov ontologie
                - ak sa nejaka cast cesty nenastavi, defaultne sa zoberu vsetky priecinky
                - nazvy mozu byt regexy
                - root logov je by default 'logs', ale aj ten sa da nastavit
                
            # log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=False, level=1))
                - funkcia generate_lubm_input_folder_string vygeneruje string, ktory sa pouziva v LUBM datasete
                - napr. toto volanie vygeneruje regex "lubm-0_1*_noneg"
    '''

    #log.set_output_path(outputs_dir="results/cc_over_time_opt", file_postfix='noneg')
    #log.interpolate_level_stats_over_time('consistency checks')

    for neg_bool, input_neg_postfix, output_neg_postfix in NEG_VALS:

        log.set_logs_path(logs=f'optim_logs/{input_neg_postfix}')
        log.set_output_path(outputs_dir="results/explanations_over_time_opt/opt4", file_prefix=output_neg_postfix)
        #log.avg_exps_over_time()
        '''
        log.set_logs_path(logs=f'optim_logs/{input_neg_postfix}')
        log.set_output_path(outputs_dir="results/edges_over_time_opt/cumsum/",file_prefix=output_neg_postfix)
        log.set_output_path(file_postfix=f'all_algs')
        log.interpolate_level_stats_over_time('created edges', cumulative=True)

        log.set_output_path(outputs_dir="results/cc_over_time_opt/cumsum/", file_prefix=output_neg_postfix)
        log.set_output_path(file_postfix=f'all_algs')
        log.interpolate_level_stats_over_time('consistency checks', cumulative=True)
        
        for i in ('', *range(1, 6)):
            log.set_logs_path(filename=f'*lubm-0_{i}*')
            log.set_output_path(file_postfix=f'{f"group G{i}" if i else "all groups"}')
            log.interpolate_level_stats_over_time('created edges', cumulative=True)

        
        log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=neg_bool))
        log.set_output_path(outputs_dir="results/scatter_nodes_by_time", file_postfix=output_neg_postfix)
        log.scatter_level_stat('finish time',  'created nodes')

        

        log.set_output_path(outputs_dir="results/explanations_over_time_new")

        for i in ('', *range(1, 6)):
            log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=neg_bool, level=i))
            log.set_output_path(file_prefix= output_neg_postfix, file_postfix=f'{f"group G{i}" if i else "all groups"}')
            log.avg_exps_over_time_cut2()

        
        log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=neg_bool))
        log.set_output_path(outputs_dir="results/hst_indices_in_time", file_prefix=f'indices', file_postfix=output_neg_postfix)
        log.scatter_level_stat('(HST) largest unassigned index')
        
        log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=neg_bool))
        log.set_output_path(outputs_dir="results/scatter_memory_by_time2", file_postfix=output_neg_postfix)
        log.scatter_level_stat('finish time','memory')

        log.set_output_path(outputs_dir="results/total_count_by_size", file_postfix=output_neg_postfix)
        log.count_by_size(negations=neg_bool)

        log.set_output_path(outputs_dir="results/average_count_by_size", file_postfix=output_neg_postfix)
        log.count_by_size(negations=neg_bool, average=True)
        
        for alg in cfg.ALL_ALGS:
            
            log.set_algs([alg])
            log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=neg_bool))
            log.set_output_path(outputs_dir=f"results/scatter_memory_by_time", file_prefix=alg,
                                file_postfix=f'_{output_neg_postfix}')
            log.scatter_level_stat('memory')
                
            log.set_algs([alg])
            log.set_output_path(outputs_dir=f"results/scatter_time_by_size/{alg}", file_prefix=alg, file_postfix=f'_{output_neg_postfix}')
            log.scatter_time_by_size(negations=neg_bool)
        
        
        log.set_output_path(outputs_dir="results/memory_over_time_new", file_prefix=f'')

        for i in ('',*range(1,6)):
            log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=neg_bool, level=i))
            log.set_output_path(file_postfix=f'{f"G{i}" if i else "All"}')
            log.memory_over_time()
        

        log.set_output_path(outputs_dir="results/memory_over_time_newer")

        for i in ('', *range(1, 6)):
            log.set_output_path(file_postfix=output_neg_postfix)
            log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=neg_bool, level=i))
            log.set_output_path(file_prefix= output_neg_postfix, file_postfix=f'{f"group G{i}" if i else "all groups"}')
            log.memory_over_time()

        
        log.set_output_path(outputs_dir="results/explanations_over_time_new")
    
        for i in ('',*range(1,6)):
            log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=neg_bool, level=i))
            log.set_output_path(file_postfix=f'{f"G{i}" if i else "All"}')
            log.avg_exps_over_time()

        log.set_output_path(outputs_dir="results/avg_time_by_size", file_postfix=output_neg_postfix)

        log.set_output_path(file_prefix="avg_time_by_size_all_expl")
        log.avg_time_by_size(negations=neg_bool)

        log.set_output_path(file_prefix="avg_time_by_size_first_expl")
        log.avg_time_by_size(negations=neg_bool, mode=log.Mode.FIRST)

        log.set_output_path(outputs_dir="results/time_out_count",file_postfix=output_neg_postfix)
        log.check_timeout(negations=neg_bool)

        log.set_output_path(outputs_dir="results/memory_over_time", file_prefix=f'{output_neg_postfix}')

        for i in ('',):
            log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=neg_bool))
            log.set_output_path(file_postfix=f'_{i if i else "all"}')
            log.memory_over_time()
            
    plot.set_export_image_extensions({'png', 'pdf'})

    plot.set_data_path("results/explanations_over_time")
    plot.set_export_path("figs/explanations_over_time")
    plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found', title='Average explanations found over time')
    plot.plot_line_graphs('time', False)

    plot.set_data_path("results/memory_over_time")
    plot.set_export_path("figs/memory_over_time")
    plot.set_plot_labels(x='Time (sec)', y='Memory used by JVM (MB)',
                         title='Average memory usage over time')
    plot.plot_line_graphs('time', False)

    plot.set_data_path("results/avg_time_by_size")
    plot.set_export_path("figs/avg_time_by_size")
    plot.set_plot_labels(x='Size of explanations', y='Average time (sec)', title='Average explanation time per size')
    plot.plot_line_graphs('size', True)

    plot.set_data_path("results/scatter_time_by_size_alg")
    plot.set_export_path("figs/scatter_time_by_size_alg")
    plot.set_plot_labels(x='Size of explanations', y='Time (sec)',
                         title='Explanation time per size')
    plot.scatter_line_graphs('size', 'time',True)
    
    plot.set_data_path('results/scatter_memory_by_time')
    plot.set_export_path("figs/scatter_memory_by_time")
    plot.set_plot_labels(x='Time (sec)', y='Memory used by JVM (MB)',
                         title='Memory usage over time')
    plot.scatter_line_graphs('finish time', 'memory', False)

    plot.set_data_path("results/total_count_by_size")
    plot.set_export_path("figs/total_count_by_size")
    plot.set_plot_labels(x='Size of explanations', y='Explanations count', title='Total explanations found per size')
    plot.plot_line_graphs('size', True)

    plot.set_data_path("results/average_count_by_size")
    plot.set_export_path("figs/average_count_by_size")
    plot.set_plot_labels(x='Size of explanations', y='Explanations count', title='Average explanations found per size')
    plot.plot_line_graphs('size', True)
    

    for alg in cfg.COMPARE_ALGS:

        log.set_algs([alg])
        log.set_output_path(outputs_dir=f"results/scatter_time_by_size_compare/", file_prefix=alg,
                            file_postfix=f'_{output_neg_postfix}')
        log.scatter_time_by_size(negations=neg_bool)
            

    plot.set_data_path("results/explanations_over_time_compare")
    plot.set_export_path("figs/explanations_over_time_compare")
    plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found', title='Average explanations found over time')
    plot.plot_line_graphs('time', False)

    plot.set_data_path("results/time_out_count")
    plot.set_export_path("figs/time_out_count")
    plot.set_plot_labels(x='Input group', y='Number of runs', title='Number of runs resulting in time-out')
    plot.plot_line_graphs('size', True)

    log.set_algs(cfg.HYBRID_ALGS)
    log.set_output_path(outputs_dir="results/time_without_timeout", file_postfix="noneg")
    log.avg_time_without_timeout(negations=False)

    plot.set_data_path("results/time_without_timeout")
    plot.set_export_path("figs/time_without_timeout")
    plot.set_plot_labels(x='Input group', y='Time (sec)', title='Average finish time of runs not resulting in time-out')
    plot.plot_line_graphs('size', True)

    log.set_algs(cfg.HYBRID_ALGS)
    log.set_logs_path(input=generic_funcs.generate_lubm_input_folder_string(negations=False))
    log.set_output_path(outputs_dir="results/scatter_finish_time_without_time_out", file_postfix="noneg")
    log.scatter_finish_time_by_size()

    plot.set_data_path('results/scatter_finish_time_without_time_out')
    plot.set_export_path("figs/scatter_finish_time_without_time_out")
    plot.set_plot_labels(x='Input group', y='Time (sec)',
                         title='Finish time of inputs')
    plot.scatter_line_graphs('size', 'time', True)

    plot.set_export_image_extensions({'png', 'pdf'})
    plot.set_export_path("figs/memory_error_compare")

    plot.compare_memory_error('results/memory_error_compare/compare.csv', 'compare')'''

    '''plot.set_data_path('results/scatter_memory_by_time2')
    plot.set_export_path("figs/scatter_memory_by_time2")
    plot.set_plot_labels(x='Time (sec)', y='Memory used by JVM (MB)',
                         title='Memory usage over time')
    plot.scatter_line_graphs('finish time', 'memory', False)

    plot.set_export_image_extensions({'png', 'pdf'})

    plot.set_data_path("results/memory_over_time_new")
    plot.set_export_path("figs/memory_over_time_new")
    plot.set_plot_labels(x='', y='', title='')
    plot.plot_line_graphs('time', False)

    plot.set_data_path("results/explanations_over_time_new")
    plot.set_export_path("figs/memory_over_time_new")
    plot.set_plot_labels(x='', y='', title='')
    plot.plot_line_graphs('time', False)

    plot.set_data_path('results/hst_indices_in_time')
    plot.set_export_path("figs/hst_indices_in_time")
    plot.set_plot_labels(x='Time (sec)', y='Largest unassigned index',
                         title='HST indices in time')
    plot.scatter_line_graphs('finish time', '(HST) largest unassigned index', False)
    
    plot.set_data_path("results/explanations_over_time_new")
    plot.set_export_path("figs/explanations_over_time_new_dashed")
    plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found', title='Average explanations found over time')
    plot.plot_line_graphs('time', False)
   
   plot.set_data_path("results/explanations_over_time_new/neg")
    plot.set_export_path("figs/explanations_over_time_new_newestesterest")
    plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found', title='Avg. explanations over time')
    #plot.plot_line_graphs('time', False)
    plot.plot_line_graphs_grid('time', False)

    plot.set_data_path("results/memory_over_time_newer")
    plot.set_export_path("figs/memory_over_time_new")
    plot.set_plot_labels(x='Time (sec)', y='Memory used by JVM (MB)',
                         title='Average memory usage over time')
    plot.plot_line_graphs('time', False)
     

    plot.set_data_path("results/memory_over_time_newer")
    plot.set_export_path("figs/memory_over_time_newer")
    plot.set_plot_labels(x='Time (sec)', y='Memory used by JVM (MB)',
                         title='Average memory usage over time')
    plot.plot_line_graphs_grid('time', False)
    
    results/scatter_nodes_by_time
    

    plot.set_data_path('results/scatter_nodes_by_time')
    plot.set_export_path("figs/scatter_nodes_by_time")
    plot.set_plot_labels(x='Time (sec)', y='Nodes created',
                         title='Nodes created per level over time')
    plot.scatter_line_graphs('finish time', 'created nodes', False)

plot.set_data_path("results/memory_over_time_newer")
plot.set_export_path("figs/memory_over_time_newer")
plot.set_plot_labels(x='Time (sec)', y='Memory used by JVM (MB)',
                         title='Average memory usage over time')
plot.plot_line_graphs_grid('time', False, rows=1, cols=2)

plot.set_data_path("results/explanations_over_time_new/neg")
plot.set_export_path("figs/explanations_over_time_final_neg")
plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found', title='Avg. explanations over time')
plot.plot_line_graphs_grid('time', False, 3, 2)

plot.set_data_path("results/explanations_over_time_new/noneg")
plot.set_export_path("figs/explanations_over_time_new_final_noneg")
plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found', title='Avg. explanations over time')
plot.plot_line_graphs_grid('time', False, 3, 2)

plot.set_export_image_extensions({'png', 'pdf'})

    plot.set_export_image_extensions({'png'})

    for alg_group in 'mhs','hst','rct':
        for neg in ('neg', 'negations'),('noneg', 'no negations'),('all','all'):

            plot.set_data_path(f"results/explanations_over_time_opt/{alg_group}/{neg[0]}")
            plot.set_export_path(f"figs/explanations_over_time_opt/{alg_group}")
            plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found', title=f'Avg. explanations over time ({neg[1]})')
            plot.plot_line_graphs_grid('time', False, 3, 2)


    plot.set_export_image_extensions({'png'})

    for alg_group in 'opt12', 'opt14':
        for neg in ('neg', 'negations'), ('noneg', 'no negations'), ('all', 'all'):
            plot.set_data_path(f"results/explanations_over_time_opt/{alg_group}")
            plot.set_export_path(f"figs/explanations_over_time_opt/{alg_group}")
            plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found',
                                 title=f'Avg. explanations over time ({neg[1]})')
            plot.plot_line_graphs_grid('time', False, 3, 2)


    plot.set_export_image_extensions({'png'})

    plot.set_data_path("results/memory_over_time_opt")
    plot.set_export_path("figs/memory_over_time_opt")
    plot.set_plot_labels(x='Time (sec)', y='Memory used by JVM (MB)',
                         title='Average memory usage over time')
    plot.plot_line_graphs_grid('time', False, 2, 2, logarithmic=False)
    
    


    for neg in ('noneg', 'no negations'),:
        for alg in f'top_{neg[0]}_pure',:
            plot.set_data_path(f"results/explanations_over_time_opt/opt+/{alg}/")
            plot.set_export_path(f"figs/explanations_over_time_opt+/{alg}")
            plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found',
                             title=f'Avg. explanations over time ({neg[1]})')
            plot.plot_line_graphs_grid('time', False, 3, 2)

    
 '''

    plot.set_data_path(f"results/explanations_over_time_opt/opt4")
    plot.set_export_path(f"figs/explanations_over_time_opt/opt4")
    plot.set_plot_labels(x='Time (sec)', y='Sum of explanations found',
                         title=f'Avg. explanations over time (with negations)')
    #plot.plot_line_graphs_grid('time', False, 2, 1)
    plot.plot_line_graph('negations.csv', 'time',False)

