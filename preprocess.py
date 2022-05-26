import librosa
import numpy as np
import os, sys
import argparse
import pyworld
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from utils import *
from tqdm import tqdm
from collections import defaultdict
from collections import namedtuple
from sklearn.model_selection import train_test_split
import glob
from os.path import join, basename
import subprocess

# 这里是XHZGenius。为了方便大家阅读，
# 我给代码里我读过并且花了一番心思才读懂的地方都加了中文注释。
# 请叫我雷锋~
# 要改参数的话请直接移步最下方的if __name__ == '__main__'部分。

def i_vector(wavpath):
    # cqy负责这个，到时候改掉，现在先填个0填充一下
    return np.zeros(512)

def save_i_vector(spk_fold_path, i_vector_dir):
    # 我自己写的，把每个音频预计算一个i-vector
    paths = glob.glob(join(spk_fold_path, '*.wav'))
    spk_name = basename(spk_fold_path)
    os.makedirs(join(i_vector_dir, spk_name), exist_ok=True) # 新建speaker名字的文件夹
    for wav_file in tqdm(paths):
        # wav_nam = basename(wav_file)
        wav_nam = spk_name+"_"+basename(wav_file) #
        result = i_vector(wav_nam)
        np.save(join(i_vector_dir, spk_name, wav_nam.replace('.wav', '.npy')), result, allow_pickle=False)
    
    return 0

def resample(spk, origin_wavpath, target_wavpath):
    '''预处理数据第一步：把一个文件夹内的所有wav转化为采样率16k的wav。
    
        存到origin_wavpath这个路径下。
    
        默认存到./data/source文件夹下面。
    '''
    wavfiles = [i for i in os.listdir(join(origin_wavpath, spk)) if i.endswith(".wav")]
    for wav in wavfiles:
        folder_to = join(target_wavpath, spk)
        os.makedirs(folder_to, exist_ok=True)
        wav_to = join(folder_to, wav).replace("\\", "/")
        wav_from = join(origin_wavpath, spk, wav).replace("\\", "/")
        # print("wav_from:", wav_from, "wav_to:", wav_to) #
        subprocess.call(['sox', wav_from, "-r", "16000", wav_to])
    return 0

def resample_to_16k(origin_wavpath, target_wavpath, num_workers=1):
    '''对根目录下的多个speaker子文件夹，分别调用上面的resample函数。
    
    例：
    
    我的迷你数据集文件夹如下：
    
    -source
        -SEF1
        -SEF2
        -SEM1
        -SEM2
        
    那origin_wavepath参数直接填source文件夹。
    
    target_wavepath就是存放新的wav文件的目标路径。默认是./data/source文件夹。
    '''
    # print("origin_wavepath:", origin_wavpath, ", target_wavpath:", target_wavpath) #
    os.makedirs(target_wavpath, exist_ok=True)
    spk_folders = os.listdir(origin_wavpath)
    print(f"> Using {num_workers} workers!")
    executor = ProcessPoolExecutor(max_workers=num_workers)
    futures = []
    for spk in spk_folders:
        print("spk =", spk) #
        futures.append(executor.submit(partial(resample, spk, origin_wavpath, target_wavpath)))
    result_list = [future.result() for future in tqdm(futures)]
    print(result_list)

def split_data(paths):
    '''把一个列表里的元素分成两个列表
        0.9: 0.1。
    '''
    indices = np.arange(len(paths))
    test_size = 0.1
    try:
        train_indices, test_indices = train_test_split(indices, test_size=test_size, random_state=1234)
        train_paths = list(np.array(paths)[train_indices])
        test_paths = list(np.array(paths)[test_indices])
    except:
        train_paths = paths
        test_paths = []
    return train_paths, test_paths

def get_spk_world_feats(spk_fold_path, mc_dir_train, mc_dir_test, sample_rate=16000):
    '''预处理数据第二步：把wav文件转化成numpy一维数组。
    
        默认存到./data/mc文件夹下面。
        
        （顺便给每个speaker生成一个我不知道是干啥用的.npz文件。
        
        生成的.npz文件好像对于训练本身没用，只是在训练到中间的时候输出几个中间结果到samples文件夹，给你看看训练成果。）
    '''
    paths = glob.glob(join(spk_fold_path, '*.wav'))
    if len(paths)==0:
        return
    spk_name = basename(spk_fold_path)
    train_paths, test_paths = split_data(paths)
    f0s = []
    coded_sps = []
    for wav_file in train_paths:
        f0, _, _, _, coded_sp = world_encode_wav(wav_file, fs=sample_rate)
        f0s.append(f0)
        coded_sps.append(coded_sp)
    log_f0s_mean, log_f0s_std = logf0_statistics(f0s)
    coded_sps_mean, coded_sps_std = coded_sp_statistics(coded_sps)
    np.savez(join(mc_dir_train, spk_name+'_stats.npz'), 
            log_f0s_mean=log_f0s_mean,
            log_f0s_std=log_f0s_std,
            coded_sps_mean=coded_sps_mean,
            coded_sps_std=coded_sps_std)
    # 上面生成的这个.npz文件，好像对于训练本身没用，只是在训练到中间的时候输出几个中间结果到samples文件夹。
    
    # 下面两行，是真的在预处理数据，就是把wav文件转化成numpy一维数组，存到（默认为./data/mc）文件夹下面。
    for wav_file in tqdm(train_paths):
        # wav_nam = basename(wav_file)
        wav_nam = spk_name+"_"+basename(wav_file) #
        f0, timeaxis, sp, ap, coded_sp = world_encode_wav(wav_file, fs=sample_rate)
        normed_coded_sp = normalize_coded_sp(coded_sp, coded_sps_mean, coded_sps_std)
        np.save(join(mc_dir_train, wav_nam.replace('.wav', '.npy')), normed_coded_sp, allow_pickle=False)
    
    for wav_file in tqdm(test_paths):
        # wav_nam = basename(wav_file)
        wav_nam = spk_name+"_"+basename(wav_file) #
        f0, timeaxis, sp, ap, coded_sp = world_encode_wav(wav_file, fs=sample_rate)
        normed_coded_sp = normalize_coded_sp(coded_sp, coded_sps_mean, coded_sps_std)
        np.save(join(mc_dir_test, wav_nam.replace('.wav', '.npy')), normed_coded_sp, allow_pickle=False)
    return 0


if __name__ == '__main__':
    # 这里是主函数。
    # 下面这部分是解析命令行。（怕不熟悉python的人看不懂这坨，还是说下）
    parser = argparse.ArgumentParser()

    # ############### 以下是命令行参数的默认值。在这里改的话就不用在命令行手动输入了。##################
    # 采样率：
    sample_rate_default = 16000
    # 原始音频位置目录：
    # origin_wavpath_default = "./data/VCTK-Corpus/wav48"
    origin_wavpath_default = "./VCC2020-database-master/source" #
    # 降采样生成的16kwav的目录：
    # target_wavpath_default = "./data/VCTK-Corpus/wav16"
    target_wavpath_default = "./processed_data/source/wav16" #
    # 处理完成的numpy一维数组的目录：（分别是训练集和测试集）
    mc_dir_train_default = './processed_data/mc/train'
    mc_dir_test_default = './processed_data/mc/test'
    i_vector_dir_default = "./processed_data/i_vector"
    # #############################################################################################

    parser.add_argument("--sample_rate", type = int, default = 16000, help = "Sample rate.")
    parser.add_argument("--origin_wavpath", type = str, default = origin_wavpath_default, help = "The original wav path to resample.")
    parser.add_argument("--target_wavpath", type = str, default = target_wavpath_default, help = "The original wav path to resample.")
    parser.add_argument("--mc_dir_train", type = str, default = mc_dir_train_default, help = "The directory to store the training features.")
    parser.add_argument("--mc_dir_test", type = str, default = mc_dir_test_default, help = "The directory to store the testing features.")
    parser.add_argument("--i_vector_dir", type = str, default = i_vector_dir_default, help = "The directory to store the training i-vectors.")
    parser.add_argument("--num_workers", type = int, default = None, help = "The number of cpus to use.")

    argv = parser.parse_args()

    sample_rate = argv.sample_rate
    origin_wavpath = argv.origin_wavpath
    target_wavpath = argv.target_wavpath
    mc_dir_train = argv.mc_dir_train
    mc_dir_test = argv.mc_dir_test
    i_vector_dir = argv.i_vector_dir
    num_workers = argv.num_workers if argv.num_workers is not None else cpu_count()
    # 上面都是在解析命令行，不用管他

    # The original wav in VCTK is 48K, first we want to resample to 16K
    # 第一步：把所有原来的wav音频降采样到16k，存在新的目录里。
    resample_to_16k(origin_wavpath, target_wavpath, num_workers=num_workers)

    # WE only use 10 speakers listed below for this experiment.
    # speaker_used = ['262', '272', '229', '232', '292', '293', '360', '361', '248', '251']
    # speaker_used = ['p'+i for i in speaker_used]
    speaker_used = ["SEF1", "SEF2", "SEM1", "SEM2"]

    ## Next we are to extract the acoustic features (MCEPs, lf0) and compute the corresponding stats (means, stds). 
    # Make dirs to contain the MCEPs
    os.makedirs(mc_dir_train, exist_ok=True)
    os.makedirs(mc_dir_test, exist_ok=True)
    os.makedirs(i_vector_dir, exist_ok=True)

    # 这个num_workers大概是要用的子进程数量orz
    num_workers = len(speaker_used) #cpu_count()
    print("number of workers: ", num_workers)
    executor = ProcessPoolExecutor(max_workers=num_workers)

    work_dir = target_wavpath
    # spk_folders = os.listdir(work_dir)
    # print("processing {} speaker folders".format(len(spk_folders)))
    # print(spk_folders)

    # 第二步：开多个进程，将采样过的16k的wav转化为numpy一维数组，存到新的目录。
    futures = []
    for spk in speaker_used:
        spk_path = os.path.join(work_dir, spk)
        futures.append(executor.submit(partial(get_spk_world_feats, spk_path, mc_dir_train, mc_dir_test, sample_rate)))
    result_list = [future.result() for future in tqdm(futures)]
    print("====== Preprocess step 2 complete. ", result_list)
    
    # 第三步：对每个wav，生成一个i-vector，存到新的目录
    futures = []
    for spk in speaker_used:
        spk_path = os.path.join(work_dir, spk)
        futures.append(executor.submit(partial(save_i_vector, spk_path, i_vector_dir)))
    result_list = [future.result() for future in tqdm(futures)]
    print("====== Preprocess step 3 complete. ", result_list)
    sys.exit(0)

