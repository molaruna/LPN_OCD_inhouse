# OCDtimeseries.py
# Generate 3 column CSV of timestamps for lobster game
#
# Column 1: For N-1 unveiling moment
# Column 2: N-1(P) reward unevailing to N choice
# Column 3: Filler
#
# python OCDtimeseries.py IBN001_game_1
#
# Author: maria.olaru@

import os
import sys
import pandas as pd
import numpy as np

DIR = os.getcwd()
CSV_IN = sys.argv[1]
CSV_OUT = (CSV_IN + '_mod')

def import_csv(dir, file):
    """ Import CSV with the directory & filename of the game """
    path = (dir + '/' + file + '.csv')
    data = pd.read_csv(path)

    return data   

def modify_csv():
    """ Modify units of time, add subtrial lengths & trial N & N-1 events  """

    datam = import_csv(DIR, CSV_IN)
    
    #Add timestamps with seconds unit
    datam[['trialStart_s',
           'goCueTime_s',
           'choiceTime_s',
           'postChoiceTimeMin_s',
           'trialEnd_s']] = datam[['trialStart',
                                 'goCueTime',
                                 'choiceTime',
                                 'postChoiceTimeMin',
                                 'trialEnd']]/1000
    
    #Add subtrial lengths
    datam['rewardCue_s'] = datam['choiceTime_s'] + 2.7
    
    datam['len_begin_choice_s'] = datam['choiceTime_s'] - datam['trialStart_s']
    datam['len_choice_reward_s'] = datam['rewardCue_s'] - datam['choiceTime_s']
    datam['len_reward_end_s'] = datam['trialEnd_s'] - datam['rewardCue_s']
                                                             
    #Add trial subtypes                             
    datam['stay_hit'] = 0
    datam['stay_miss'] = 0
    datam['switch'] = datam['bridge']  
 
    datam.loc[np.logical_and(datam.bridge == 0, datam.reward != 0), 
              'stay_hit'] = 1
    datam.loc[np.logical_and(datam.bridge == 0, datam.reward == 0), 
             'stay_miss'] = 1
    
    #Add trials N w/ trial N-1 choice outcomes  
    stay_hit_c = datam.loc[0:len(datam)-2, 'stay_hit']
    datam['stay_hit_prior'] = np.concatenate((0, stay_hit_c.to_numpy()), 
                                             axis = None)
    
    stay_miss_c = datam.loc[0:len(datam)-2, 'stay_miss']
    datam['stay_miss_prior'] = np.concatenate((0, stay_miss_c.to_numpy()), 
                                              axis = None)
        
    switch_c = datam.loc[0:len(datam)-2, 'switch']
    datam['switch_prior'] = np.concatenate((0, switch_c.to_numpy()), 
                                              axis = None)
    return datam

def create_timing_files(trial_type):
    """ Create timing files for length N-1(P) reward unevailing to N choice  """
    datam = modify_csv()
    
    #Subset & Filter
    datam_N = datam[datam[trial_type] == 1]
    
    #remove first trial if present after filtering 
    if(datam_N.index[len(datam_N)-1] == len(datam)-1):
        datam_N = datam_N[:len(datam_N)-1]
    
    datam_P = datam[datam[(trial_type + '_prior')] == 1]

    #Array of length of time
    len_reward_choice = datam_N['len_reward_end_s'].to_numpy() + datam_P['len_begin_choice_s'].to_numpy() + datam_P['len_choice_reward_s'].to_numpy()
    
    timing_hit = {'time': datam_N['rewardCue_s'].to_numpy(), 
                  'length': len_reward_choice, 
                  'filler': np.ones(len(datam_P))}
    
    timing_hit = pd.DataFrame(timing_hit)
    
    return timing_hit

def main():
    datam = modify_csv()
    datam.to_csv((DIR + '/' + CSV_OUT + '.csv'))
    
    timing_hit = create_timing_files('stay_hit')
    timing_hit.to_csv((DIR + '/' + CSV_IN + '_stay_hit.txt'), 
                      header=None, index=None, sep=' ')
    
    timing_miss = create_timing_files('stay_miss')
    timing_miss.to_csv((DIR + '/' + CSV_IN + '_stay_miss.txt'), 
                      header=None, index=None, sep=' ')
    
    timing_switch = create_timing_files('switch')
    timing_switch.to_csv((DIR + '/' + CSV_IN + '_switch.txt'), 
                      header=None, index=None, sep=' ')    
  
if __name__ == '__main__': 
    main()