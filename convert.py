import argparse
from model import Generator
from torch.autograd import Variable
import torch
import torch.nn.functional as F
import numpy as np
import os
from os.path import join, basename, dirname, split
import time
import datetime
from data_loader import to_categorical
import librosa
from utils import *
import glob

VERBOSE = False

def MyPrint(*args):
    if VERBOSE:
        print(*args)

# Below is the accent info for the used 10 speakers.
# spk2acc = {'262': 'Edinburgh', #F
#            '272': 'Edinburgh', #M
#            '229': 'SouthEngland', #F 
#            '232': 'SouthEngland', #M
#            '292': 'NorthernIrishBelfast', #M 
#            '293': 'NorthernIrishBelfast', #F 
#            '360': 'AmericanNewJersey', #M
#            '361': 'AmericanNewJersey', #F
#            '248': 'India', #F
#            '251': 'India'} #M
# speakers = ['p262', 'p272', 'p229', 'p232', 'p292', 'p293', 'p360', 'p361', 'p248', 'p251']
# speakers = ["SEF1", "SEF2", "SEM1", "SEM2"] #
speakers = ["fucker1", "fucker2"]
spk2idx = dict(zip(speakers, range(len(speakers))))

class TestDataset(object):
    """Dataset for testing."""
    def __init__(self, config):
        assert config.trg_spk in speakers, f'The trg_spk should be chosen from {speakers}, but you choose {config.trg_spk}.'
        # Source speaker
        self.src_spk = config.src_spk
        self.trg_spk = config.trg_spk

        self.mc_files = sorted(glob.glob(join(config.test_data_dir, f'{config.src_spk}*.npy')))
        self.src_spk_stats = np.load(join(config.train_data_dir, f'{config.src_spk}_stats.npz'))
        self.src_wav_dir = f'{config.wav_dir}/{config.src_spk}'

        
        self.trg_spk_stats = np.load(join(config.train_data_dir, f'{config.trg_spk}_stats.npz'))

        self.logf0s_mean_src = self.src_spk_stats['log_f0s_mean']
        self.logf0s_std_src = self.src_spk_stats['log_f0s_std']
        self.logf0s_mean_trg = self.trg_spk_stats['log_f0s_mean']
        self.logf0s_std_trg = self.trg_spk_stats['log_f0s_std']
        self.mcep_mean_src = self.src_spk_stats['coded_sps_mean']
        self.mcep_std_src = self.src_spk_stats['coded_sps_std']
        self.mcep_mean_trg = self.trg_spk_stats['coded_sps_mean']
        self.mcep_std_trg = self.trg_spk_stats['coded_sps_std']
        
        self.spk_idx = spk2idx[config.trg_spk]
        spk_cat = to_categorical([self.spk_idx], num_classes=len(speakers))
        self.spk_c_trg = spk_cat


    def get_batch_test_data(self, batch_size=4):
        '''返回一个文件路径的列表
        '''
        batch_data = []
        for i in range(batch_size):
            mcfile = self.mc_files[i]
            # filename = basename(mcfile).split('-')[-1]
            filename = basename(mcfile).split('_')[-1] #
            wavfile_path = join(self.src_wav_dir, filename.replace('npy', 'wav'))
            batch_data.append(wavfile_path)
        return batch_data 


def load_wav(wavfile, sr=16000):
    wav, _ = librosa.load(wavfile, sr=sr, mono=True)
    return wav_padding(wav, sr=sr, frame_period=5, multiple = 4)  # TODO
    # return wav

def test(config):
    os.makedirs(join(config.convert_dir, str(config.resume_iters)), exist_ok=True)
    sampling_rate, num_mcep, frame_period=16000, 36, 5
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # G = Generator().to(device) # 奶奶滴，这写代码的人压根没测试过别的数据集，连参数都不传直接用默认值？？
    G = Generator(num_speakers=config.num_speakers).to(device) # 辛亏爷发现滴早，机智如我
    test_loader = TestDataset(config)
    
    # Restore model
    MyPrint(f'Loading the trained models from step {config.resume_iters}...')
    G_path = join(config.model_save_dir, f'{config.resume_iters}-G.ckpt')
    G.load_state_dict(torch.load(G_path, map_location=lambda storage, loc: storage))
    print("模型Generator加载完成。")
    MyPrint("模型：", G)

    # Read a batch of testdata
    test_wavfiles = test_loader.get_batch_test_data(batch_size=config.num_converted_wavs)
    test_wavs = [load_wav(wavfile, sampling_rate) for wavfile in test_wavfiles]
    print("源语音加载成功：", ", ".join(test_wavfiles))
    
    source2_path = join("./convertFolder/data/i_vector/fucker2", 
                            os.listdir("./convertFolder/data/i_vector/fucker2")[0])
    i_vector = np.load(source2_path)
    i_vector = torch.FloatTensor(np.array([i_vector])).to(device)
    print("目标说话人语音i-vector加载成功：", source2_path)

    with torch.no_grad():
        for idx, wav in enumerate(test_wavs):
            MyPrint("len(wav):", len(wav))
            wav_name = basename(test_wavfiles[idx])
            # MyPrint(wav_name)
            f0, timeaxis, sp, ap = world_decompose(wav=wav, fs=sampling_rate, frame_period=frame_period)
            f0_converted = pitch_conversion(f0=f0, 
                mean_log_src=test_loader.logf0s_mean_src, std_log_src=test_loader.logf0s_std_src, 
                mean_log_target=test_loader.logf0s_mean_trg, std_log_target=test_loader.logf0s_std_trg)
            coded_sp = world_encode_spectral_envelop(sp=sp, fs=sampling_rate, dim=num_mcep)
            print("源语音编码完成。")
            MyPrint("Before being fed into G: ", coded_sp.shape)
            coded_sp_norm = (coded_sp - test_loader.mcep_mean_src) / test_loader.mcep_std_src
            coded_sp_norm_tensor = torch.FloatTensor(coded_sp_norm.T).unsqueeze_(0).unsqueeze_(1).to(device)
            # spk_conds = torch.FloatTensor(test_loader.spk_c_trg).to(device)
            # MyPrint(spk_conds.size())
            
            # coded_sp_converted_norm = G(coded_sp_norm_tensor, spk_conds).data.cpu().numpy()
            MyPrint("音频输入:", coded_sp_norm_tensor.size(), coded_sp_norm_tensor)
            MyPrint("i-vector输入:", i_vector.size(), i_vector)
            print("正在通过模型Generator。")
            coded_sp_converted_norm = G(coded_sp_norm_tensor, i_vector).data.cpu().numpy()
            print("模型Generator生成完成！")
            
            coded_sp_converted = np.squeeze(coded_sp_converted_norm).T * test_loader.mcep_std_trg + test_loader.mcep_mean_trg
            coded_sp_converted = np.ascontiguousarray(coded_sp_converted)
            MyPrint("After being fed into G: ", coded_sp_converted.shape)
            wav_transformed = world_speech_synthesis(f0=f0_converted, coded_sp=coded_sp_converted, 
                                                    ap=ap, fs=sampling_rate, frame_period=frame_period)
            print("生成语音解码完成。")
            wav_id = wav_name.split('.')[0]
            save_path = join(config.convert_dir, str(config.resume_iters), f'{wav_id}-vcto-{test_loader.trg_spk}.wav')
            librosa.output.write_wav(save_path, wav_transformed, sampling_rate)
            print("写入文件完成，保存路径：", save_path)
            if [True, False][0]:
                wav_cpsyn = world_speech_synthesis(f0=f0, coded_sp=coded_sp, 
                                                ap=ap, fs=sampling_rate, frame_period=frame_period)
                save_path2 = join(config.convert_dir, str(config.resume_iters), f'cpsyn-{wav_name}')
                librosa.output.write_wav(save_path2, wav_cpsyn, sampling_rate)
                print("源语音一（对照语音）保存路径：", save_path2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Model configuration.
    # parser.add_argument('--num_speakers', type=int, default=10, help='dimension of speaker labels')
    parser.add_argument('--num_speakers', type=int, default=4, help='dimension of speaker labels') #
    parser.add_argument('--num_converted_wavs', type=int, default=1, help='number of wavs to convert.')
    parser.add_argument('--resume_iters', type=int, default=200000, help='step to resume for testing.')
    # parser.add_argument('--src_spk', type=str, default='p262', help = 'source speaker.')
    parser.add_argument('--src_spk', type=str, default='fucker1', help = 'source speaker.') #
    # parser.add_argument('--trg_spk', type=str, default='p272', help = 'target speaker.')
    parser.add_argument('--trg_spk', type=str, default='fucker2', help = 'target speaker.') #

    # Directories.
    parser.add_argument('--train_data_dir', type=str, default='./convertFolder/data')
    parser.add_argument('--test_data_dir', type=str, default='./convertFolder/data')
    parser.add_argument('--wav_dir', type=str, default="./convertFolder/wav")
    # parser.add_argument('--wav_dir', type=str, default="./data/source/wav16")
    parser.add_argument('--log_dir', type=str, default='./logs')
    parser.add_argument('--model_save_dir', type=str, default='./models')
    parser.add_argument('--convert_dir', type=str, default='./convertFolder')
    
    # Verbose?
    parser.add_argument("--verbose", type=bool, default=False)
    
    config = parser.parse_args()
    VERBOSE = config.verbose
    MyPrint(config)
    
    if config.resume_iters is None:
        raise RuntimeError("Please specify the step number for resuming.")
    test(config)
