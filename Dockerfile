FROM centos:7

# セットアップ
RUN set -x
RUN yum clean all && yum -y update

# 必要パッケージのインストール
RUN yum install -y git vim wget unzip make swig gcc gcc-c++ \
                   cmake boost boost-devel bzip2 bzip2-devel \
                   zlib-devel zlib-static xz-devel

# python3.6のインストール
RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm
RUN yum install -y python36u python36u-libs python36u-devel python36u-pip

# mecabのインストール
RUN rpm -ivh http://packages.groonga.org/centos/groonga-release-1.1.0-1.noarch.rpm
RUN yum install -y mecab mecab-devel mecab-ipadic

# UniDic辞書のダウンロード
RUN mkdir /home/tools
WORKDIR /home/tools
RUN wget https://ja.osdn.net/dl/unidic/unidic-mecab-2.1.2_src.zip
RUN unzip unidic-mecab-2.1.2_src.zip
WORKDIR /home/tools/unidic-mecab-2.1.2_src
RUN ./configure
RUN make
RUN make install

# kenlmのインストール
WORKDIR /home/tools
RUN wget -O - https://bitbucket.org/eigen/eigen/get/3.2.8.tar.bz2 |tar xj
RUN export EIGEN3_ROOT=/home/tools/eigen-eigen-07105f7124f9
RUN wget -O - https://kheafield.com/code/kenlm.tar.gz |tar xz
RUN mkdir /home/tools/kenlm/build
WORKDIR /home/tools/kenlm/build
RUN cmake ..
RUN make -j2

# モデルファイルのマウント先
RUN mkdir /home/tools/kenlm/data

# git clone (https://qiita.com/Jah524/items/fa68f99c8b787f94b884)
WORKDIR /home
RUN git clone https://db07bc1dc6b5ced230d48b4dc0bf4be3e6cff2f2:x-oauth-basic@github.com/youichiro/language-model-error-checker.git

# pip install
RUN pip3.6 install flask flask-bootstrap mecab-python3 gunicorn \
                   https://github.com/kpu/kenlm/archive/master.zip

# 公開ポート
EXPOSE 5000

# 実行コマンド
WORKDIR /home/language-model-error-checker
CMD [ "gunicorn", "-b", "0.0.0.0:5000", "-w", "1", "app:app" ]


# docker build -t lm-checker-image .
# docker run --name lm-checker-container -d -p <PORT>:5000 -v ~/KENLM/BINARY/FILE/PATH:/home/tools/kenlm/data lm-checker-image

