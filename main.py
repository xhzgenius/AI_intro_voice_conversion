import os
import argparse
from solver import Solver
from data_loader import get_loader, TestDataset
from torch.backends import cudnn


def str2bool(v):
    return v.lower() in ('true')

def main(config):
    '''
    这里是XHZGenius。这是一点简短说明。
    
    要改参数的话请移步下面的if __name__ == '__main__'部分。
    
    整个main()函数干的事情：
    
    创建一个训练集的data loader和一个测试集的data loader。（他们用来读取数据集里的东西）
    
    创建一个Solver对象。这是个自定义类的对象，包括了模型在内。
    
    调用它的train()方法，会使用上面的两个data loader来读取数据，并使用梯度下降法来训练模型，
    
    然后把训练过程输出到控制台和TensorboardX这个图形化界面。
    '''
    # For fast training.
    cudnn.benchmark = True

    # Create directories if not exist.
    if not os.path.exists(config.log_dir):
        os.makedirs(config.log_dir)
    if not os.path.exists(config.model_save_dir):
        os.makedirs(config.model_save_dir)
    if not os.path.exists(config.sample_dir):
        os.makedirs(config.sample_dir)

    # Data loader.
    train_loader = get_loader(config.train_data_dir, config.batch_size, 'train', num_workers=config.num_workers)
    test_loader = TestDataset(config.test_data_dir, config.wav_dir, src_spk='p225', trg_spk='p262')

    # Solver for training and testing StarGAN.
    solver = Solver(train_loader, test_loader, config)

    if config.mode == 'train':    
        solver.train()

    # elif config.mode == 'test':
    #     solver.test()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # ##### 以下是解析命令行的代码。里面的default是参数默认值。可以直接在这里改。#########################
    # Model configuration.
    parser.add_argument('--num_speakers', type=int, default=10, help='dimension of speaker labels')
    # parser.add_argument('--num_speakers', type=int, default=4, help='dimension of speaker labels') #
    parser.add_argument('--lambda_cls', type=float, default=10, help='weight for domain classification loss')
    parser.add_argument('--lambda_rec', type=float, default=10, help='weight for reconstruction loss')
    parser.add_argument('--lambda_gp', type=float, default=10, help='weight for gradient penalty')
    parser.add_argument('--sampling_rate', type=int, default=16000, help='sampling rate')
    
    # Training configuration.
    # parser.add_argument('--batch_size', type=int, default=32, help='mini-batch size') # 在集群上跑是可以开成32的
    parser.add_argument('--batch_size', type=int, default=8, help='mini-batch size') # 在自己电脑上跑，还是改成8
    parser.add_argument('--num_iters', type=int, default=200000, help='number of total iterations for training D')
    parser.add_argument('--num_iters_decay', type=int, default=100000, help='number of iterations for decaying lr')
    parser.add_argument('--g_lr', type=float, default=0.0001, help='learning rate for G')
    parser.add_argument('--d_lr', type=float, default=0.0001, help='learning rate for D')
    parser.add_argument('--n_critic', type=int, default=5, help='number of D updates per each G update')
    parser.add_argument('--beta1', type=float, default=0.5, help='beta1 for Adam optimizer')
    parser.add_argument('--beta2', type=float, default=0.999, help='beta2 for Adam optimizer')
    parser.add_argument('--resume_iters', type=int, default=None, help='resume training from this step')

    # Test configuration.
    parser.add_argument('--test_iters', type=int, default=100000, help='test model from this step')

    # Miscellaneous.
    parser.add_argument('--num_workers', type=int, default=4)
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'test'])
    parser.add_argument('--use_tensorboard', type=str2bool, default=True)

    # Directories.
    parser.add_argument('--train_data_dir', type=str, default='/processed_data/mc/train')
    parser.add_argument('--test_data_dir', type=str, default='/processed_data/mc/test')
    parser.add_argument('--i_vector_dir', type=str, default='/processed_data/i_vector')
    # parser.add_argument('--wav_dir', type=str, default="./data/VCTK-Corpus/wav16")
    parser.add_argument('--wav_dir', type=str, default="/dataset/VCTK-Corpus/newByXHZ") #
    parser.add_argument('--log_dir', type=str, default='/logs')
    parser.add_argument('--model_save_dir', type=str, default='/model')
    parser.add_argument('--sample_dir', type=str, default='/samples')

    # Step size.
    parser.add_argument('--log_step', type=int, default=10)
    parser.add_argument('--sample_step', type=int, default=1000)
    parser.add_argument('--model_save_step', type=int, default=1000)
    parser.add_argument('--lr_update_step', type=int, default=1000)

    config = parser.parse_args()
    # ################# 解析命令行完成。##############################################################
    print(config)
    main(config)