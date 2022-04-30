# 文档

XHZGenius



### 写在前面

其实英文好的同学看原作者写的文档就够了。但那里面没有各个模块的说明，那我简单解释一下。



##### 环境依赖

* Python 3.6 (or 3.5)（亲测，3.7也行）
* Pytorch 0.4.0（最好是cuda版。建议在官网找安装指令。）
* pyworld
* tqdm
* librosa（注意，版本不能大于等于0.8，因为0.8移除了一个代码里用到的函数。下载的时候输入pip install librosa==0.7.2，还是0.72来着忘了。同时，numba包版本需要是0.48（好像）。用pip install numba==0.48来下载旧版本。如果错了的话百度就能查到。）
* tensorboardX and tensorboard

用pip安装就行了。别用conda装包，贼慢。可以用conda创建虚拟环境，然后conda install pip，再用虚拟环境里的pip下包，什么NTR剧情（



### 几个.py文件都是干什么用的？

* convert.py：训练完成后，用来语音转换。需要运行。
* data_loader.py：用于加载训练数据的，自定义的类/函数。无需运行它。
* logger.py：用来显示训练日志（包括可视化界面tensorboradX）。用vscode打开它，然后点击“启动tensorboard会话”即可，无需运行。
* main.py：需要运行。用于训练。
* model.py：定义了模型的结构。（没有定义损失函数，那是在solver中定义的，反向传播也是在那里进行的）无需运行。
* preprocess.py：需要运行。用于预处理数据。
* solver.py：用来训练的自定义类。无需运行。
* utils.py：定义了一些辅助函数。无需运行。



### 怎么跑？

1）先下载数据集。

2）预处理数据。

3）跑。

##### 第一步：下载数据集

我的文件夹里有现成的数据集。如果只想跑一下看个结果，可以跳过第一步。

如果想要用那个10G的数据集（建议不要！下载特别慢，几十kb每秒，我已经跟助教说了，让他下载了放在学校那个平台上面）：

打开命令行cmd。

如果你没下载数据集，那么请输入：

```bash
mkdir ./data
wget https://datashare.is.ed.ac.uk/bitstream/handle/10283/2651/VCTK-Corpus.zip?sequence=2&isAllowed=y
unzip VCTK-Corpus.zip -d ./data
```

如果下载下来是tar格式，最后一行改为这个：

```bash
tar -xzvf VCTK-Corpus.tar.gz -C ./data
```

这样你就下载完了。数据集在./data文件夹。

##### 第二步：预处理数据

输入python preprocess.py。用默认参数就可以了。

要改参数也别在命令行里面改。。蛋疼死了，直接在preprocess.py文件里面改就可以了。

具体如下：

```python
    # ############### 以下是命令行参数的默认值。在这里改的话就不用在命令行手动输入了。##################
    # 采样率：
    sample_rate_default = 16000
    # 原始音频位置目录：
    # origin_wavpath_default = "./data/VCTK-Corpus/wav48"（这种被我注释掉的是原代码，我换了数据集所以改了）
    origin_wavpath_default = "./VCC2020-database-master/source" #
    # 降采样生成的16kwav的目录：
    # target_wavpath_default = "./data/VCTK-Corpus/wav16"
    target_wavpath_default = "./data/source/wav16" #
    # 处理完成的numpy一维数组的目录：（分别是训练集和测试集）
    mc_dir_train_default = './data/mc/train'
    mc_dir_test_default = './data/mc/test'
    # #############################################################################################
```

##### 第三步：跑

输入python main.py。

记得改参数：speaker-num代表数据集中说话者的数量。请一定要填写正确的值，不然会报错。



##### 第四步：训练完了以后，怎么用这个模型得到语音转换后的结果？

作者贴心地写了个convert.py。

要改的参数：num_speakers，这个跟数据集有关；num_converted_wavs代表你要随机抽取多少个音频来转换，这个随便，别超过测试集里面说话人所说的音频的总数就行了；resume_iters代表模型的检查点（checkpoint）（比如你训练了24000次iteration，那就填24000）；src_spk和trg_spk代表源和目标speaker的名字。

示例：restore model at step 200000 and specify the source speaker and target speaker to `p262` and `p272`, respectively.

```
convert.py --resume_iters 200000 --src_spk p262 --trg_spk p272
```



### 如果你要改代码：

请注意：凡是被注释掉的代码，并且下面一行代码末尾带#号的，都是我稍作修改的代码。例如：

```python
def test(config):
    os.makedirs(join(config.convert_dir, str(config.resume_iters)), exist_ok=True)
    sampling_rate, num_mcep, frame_period=16000, 36, 5
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # G = Generator().to(device) # 奶奶滴，这写代码的人压根没测试过别的数据集，连参数都不传直接用默认值？？
    G = Generator(num_speakers=config.num_speakers).to(device) # 辛亏爷发现滴早，机智如我
    test_loader = TestDataset(config)
```

里面的6、7行就是我修改的。为了保留原来的代码，我不会轻易的删除整行。这样，如果有需要的话，可以改回来。

##### 如果你要用新的数据集：

注意数据集里面文件和文件夹的命名规则。有的形如"说话人\_语料编号"，有的形如"说话人-语料编号"，有的形如"语料编号"。为了方便起见，尽量统一一下命名规则，不然的话要改代码里的一些细节，比如用split()分割字符串和用join()拼接字符串的地方。



### 最后：

我自己跑了一下代码，花了大约两天时间，缝缝补补，终于让代码在一个迷你数据集（大概几十M）上面成功跑了起来。跑了四五个小时，24000次迭代，看起来不太能继续收敛了（可能数据集太小了），效果还不错。

我希望（并且我觉得能做）的，是把说话者特征（speaker feature）的部分改进一下。当前模型中用的是one-hot vector（n维向量，只有第i个元素是1，其它都是0，代表第i个speaker），这样的话，模型训练的结果不能推广到未知的说话者。最简单（且好实现）的方法是：我们可以让模型输入一个代表说话者特征的向量，这个向量怎么获得呢，我们可以预训练一个分类器，然后抽取分类器的隐层（一般隐层里面的输出包含了说话者特征）作为我们要的向量。然后我们用这个预先训练好的固定不动的“特征提取器”作为辅助，来训练我们的这个StarGAN网络。

谢谢朋友们！
