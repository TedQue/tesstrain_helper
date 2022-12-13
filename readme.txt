训练自己的 Tesseract LSTM模型用于识别验证码
by 阙荣文 2022.12.12

Tesseract-OCR 官方仓库包含的训练数据直接用于识别验证码通常效果并不好,因为验证码字体往往会带有一定程度的扭曲,有必要训练自己的模型.
根据我在网上找到的资料,训练模型的方法大约有以下几种:
a. 参考 https://www.cnblogs.com/nayitian/p/15240143.html 可在 windows 平台下操作,较为繁琐
b. 使用 Tesseract-OCR 官方提供的基于 make 的训练工具 tesstrain,缺点是只支持 Linux 平台,这也是本文将要介绍的方法(以 Ubuntu 环境为例)
c. 改造官方训练工具使之可以在 windows 平台上运行,请参考 https://livezingy.com/train-tesseract-lstm-with-make-on-windows/

0. 安装
a. 安装 Tesseract-OCR 引擎, 可以参考 https://tesseract-ocr.github.io/tessdoc/Home.html 从官方 GitHub 仓库源码安装或者从 Ubuntu 软件仓库直接安装编译好的版本 "sudo apt install tesseract-ocr"
b. 安装 tesstrain 训练工具, git clone https://github.com/tesseract-ocr/tesstrain.git
c. 下载训练数据 https://github.com/tesseract-ocr/tessdata_best 只需下载 eng.traineddata, chi_sim.traineddata, 保存到 tesstrain/data/tessdata
d. 下载 langdata_lstm, git clone https://github.com/tesseract-ocr/langdata_lstm.git,
整个项目很大,下载困难的话可以只下载顶层文件以及 eng, chi_sim 两个子目录, 保存到 tesstrain/data/langdata

1. 准备用于训练的验证码图片
需要收集大量验证码图片,数量越多效果越好.

2. 验证码图片通常带有较多干扰因素,需要预先处理(清洗).
通常包括灰度化,二值化,降噪,字符切分,并存储为 tif 或 png 格式

3. 标注
对于每个输入图片 "a.tif"(假设图片的内容就是字符 "a") tesstrain 要求同目录下存在名为 "a.gt.txt" 的文本文件,且该文件的内容为 "a",这样 tesstrain 就可以建立起图片与内容之间的联系,此过程即通常所说的"标注".

验证码图片内容通常比较简单,我们可以像上述那样用验证码内容作为文件名,比如从网站获取到内容为 "ABCD" 的验证码图片我们就把它存为 ABCD.jpg,然后再编写一个 python 脚本根据文件名生成对应的 ABCD.gt.txt 文件,其内容为 "ABCD" 我们约定,如果有相同内容的验证码图片,则按照 ABCD_0.jpg ABCD_1.jpg 依次命名,附录的 python 脚本依赖于这个约定.

我们可以编写一个 python 脚本(参考附录1),批量执行步骤 2, 3 这样,我们只要收集大量的验证码图片,然后人工根据验证码内容重命名这些文件(这一步人工介入就是"教会"模型的关键),剩下的事可以由 python 脚本处理.

4. 选择基础训练数据
我们在 Tesseract-OCR 官方提供的 _best 训练数据的基础上添加验证码字符特征而不是重头训练一个新模型,如果验证码只包含英文字符则选择 eng.traineddata 如果含有中文字符则选择 chi_sim.traineddata

5. 准备输入数据
为自己的模型取个名字,假设为 "abc",把第 3 步中由 python 脚本生成的所有 .tif 和 .gt.txt 文件复制到 tesstrain/data/abc-ground-truth

6. 开始训练
$make training MODEL_NAME=abc START_MODEL=eng TESSDATA=data/tessdata PSM=7
(PSM=7 表示假设输入图片为单行文本,如果输入图片已经过了字符切割,则设置 PSM=10) 

7. 把训练结果 tesstrain/data/abc.traineddata 复制到 tesseract-ocr 目录(/usr/share/tessdata)
运行 $tesseract --list-langs 可以看到我们的模型 "abc" 已经出现在列表中

附录1:
实际应用中,验证码图片各式各样,如何做前期清洗非常见功力,除了通常的灰度化,二值化之外并无一定之规,不过关于如何处理验证码图片网上的文章较多,这里我提供一个 python 脚本实现上述步骤 2, 3 只实现简单清洗和字符切分,仅供参考.

运行前把收集到的验证码图片(jpg 格式),按照步骤 3 人工标注后放在目录 input 中,另建立一个输出目录 output,然后运行 "tesstrain_helper.py -s input output" (选项 -s 可以控制是否切割为单个字符)即可得到用于训练模型的 .tif 和 .gt.txt 文件.

附录2: update log
2022.12.13
1. 更新版本号,添加开发日志附录
	-> v0.0.2