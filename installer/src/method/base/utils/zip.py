# coding: utf-8

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, shutil, zipfile
from datetime import datetime, date
from pathlib import Path


# 自作モジュール
from method.base.utils.logger import Logger
from method.base.utils.path import BaseToPath
from method.base.decorators.decorators import Decorators

decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# ファイルに書き込みする基底クラス


class ZipOperation:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()
        self.currentDate = datetime.now().strftime("%y%m%d_%H%M%S")

    # ----------------------------------------------------------------------------------
    # Zipファイルの解凍

    def unzip_same_position(self, zipfile_path: str):
        try:
            base_dir = os.path.dirname(zipfile_path)
            zip_name = os.path.splitext(os.path.basename(zipfile_path))[0]
            unzip_dir = os.path.join(base_dir, zip_name)

            unique_unzip_file_dir = self._get_unique_folder_path(unzip_dir)
            os.makedirs(unique_unzip_file_dir, exist_ok=True)

            with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
                zip_ref.extractall(unique_unzip_file_dir)

            self.logger.info(f'Zipファイルの解凍を行いました: {unique_unzip_file_dir}')

            return unique_unzip_file_dir

        except Exception as e:
            self.logger.error(f'{self.__class__.__name__}: write_csv_joint: 処理中にエラーが発生{e}')

    # ----------------------------------------------------------------------------------
    # フォルダ名が被らないようにする

    def _get_unique_folder_path(self, base_path: Path):
        if not os.path.exists(base_path):
            return base_path

        counter = 1
        while True:
            new_path = f"{base_path}({counter})"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    # ----------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------
