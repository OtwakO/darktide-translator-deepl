# -*- coding: utf-8 -*-
import os, sys, time
import concurrent.futures
from PyDeepLX import PyDeepLX
from .proxy_api import ProxyGen
from loguru import logger


os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))


class DeeplTranslator:
    def __init__(self):
        self.ProxyGen = ProxyGen()

    def single_job(self, sentence):
        if "\n" in sentence:
            split_line = sentence.split("\n")
            translation = self.translate(
                split_line, source_lang=self.source_lang, target_lang=self.target_lang
            )
            concat_translation = "\n".join(translation)
            return concat_translation
        else:
            proxy = self.ProxyGen.rand_proxy()
            proxy_str = f"{proxy.split('@')[-1]}"
            while True:
                try:
                    translation = PyDeepLX.translate(
                        text=sentence,
                        sourceLang=self.source_lang,
                        targetLang=self.target_lang,
                        proxies=proxy,
                    )
                    if self.logger:
                        logger.success(
                            f"\n{'-'*100}\nRaw: {sentence}\nTranslation: {translation}\nProxy: {proxy_str}\n{'-'*100}"
                        )
                    return translation
                except PyDeepLX.TooManyRequestsException as e:
                    self.ProxyGen.remove_proxy(proxy)
                    proxy = self.ProxyGen.rand_proxy()
                    if self.logger:
                        logger.error("Too many request! Changing proxy...")
                        proxy_str += f" --> {proxy.split('@')[-1]}"
                    continue
                except Exception as e:
                    self.ProxyGen.remove_proxy(proxy)
                    proxy = self.ProxyGen.rand_proxy()
                    if self.logger:
                        logger.error("Too many request! Changing proxy...")
                        proxy_str += f" --> {proxy.split('@')[-1]}"
                    continue

    def translation_jobs(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.single_job, sentence)
                for sentence in self.sentences
            ]
            translations = [f.result() for f in futures]
        return translations

    def translate(
        self, sentences: list, source_lang=None, target_lang=None, logger=False
    ):
        self.sentences = sentences
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.logger = logger
        return self.translation_jobs()


if __name__ == "__main__":
    JAPANESE_SENTENCES = [
        "昨日、友達と一緒に美味しい寿司を食べました。",
        "東京に行くと、いつも新しい発見があります。",
        "最近日本の伝統文化に興味を持ち始めました。",
        "新しい仕事を始める前にしっかりと計画を立てることが大切です。",
        "日本の四季折々の美しさは本当に魅力的ですね。",
        "毎週末、公園で散歩することが私のリラックス方法です。",
        "新しい言語を学ぶことは挑戦的ですが、楽しいです。",
        "夏の夜空には、星がたくさん見えて本当に美しいですね。",
        "日本の伝統的な祭りに参加すると、地元の文化を深く理解できます。",
        "自分の夢を追い求めることは、時には困難でも、充実感があります。",
        "おいしい料理を作ることは、家族や友達との特別な瞬間を作り出します。",
        "毎日の小さな習慣が、大きな変化をもたらすことがあります。",
        "新しい本を読むことは、知識を広げる素晴らしい方法です。",
        "健康的なライフスタイルを維持するためには、バランスの取れた食事が不可欠です。",
        "友達と一緒に旅行すると、思い出がたくさん作れます。",
        "人々の異なる文化に興味を持ち、理解することは、世界を豊かにします。",
        "自然の美しさに触れることは、心を穏やかにします。",
        "新しい技術の進化は、私たちの生活に革命をもたらしています。",
        "仕事とプライベートのバランスを取ることは、健康的な生活を維持する上で重要です。",
        "人生の挑戦に立ち向かうことで、成長と学びが得られます。",
    ]
    deepl = DeeplTranslator()

    for i in range(100):
        translations = deepl.translate(
            JAPANESE_SENTENCES, source_lang="JP", target_lang="EN", logger=True
        )
        print(translations)
