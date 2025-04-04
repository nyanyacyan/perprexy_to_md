# coding: utf-8

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, shutil
from datetime import datetime
from pathlib import Path
from typing import List


# 自作モジュール
from method.base.utils.logger import Logger
from method.base.utils.path import BaseToPath
from method.base.decorators.decorators import Decorators

decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# ファイルに書き込みする基底クラス


class DownloadFileDelete:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()
        self.currentDate = datetime.now().strftime("%y%m%d_%H%M%S")

    #!###################################################################################
    # 結合して書き込む

    def delete_in_download_folder(self, file_name_head: str, extension: str):
        try:
            downloads_path = Path(self._downloads_path())

            search_file_name_word = f"{file_name_head}*{extension}"
            self.logger.debug(f'search_file_name_word: {search_file_name_word}')

            matching_file_path_list = list(downloads_path.glob(search_file_name_word))
            self.logger.debug(f'matching_file_path_list: {matching_file_path_list}')

            if not matching_file_path_list:
                self.logger.info(f'{self.__class__.__name__} 指定されているパターンのファイルがありませんでした: {file_name_head}*.{extension}')
                return None

            # 指定のファイルがあったため削除
            self.logger.warning(f'ファイル名: {file_name_head} があったため削除を実施')

            for file_path in matching_file_path_list:
                os.remove(file_path)
                self.logger.warning(f'{file_name_head} を削除しました: {file_path}')

        except Exception as e:
            self.logger.error(f'{self.__class__.__name__}: write_csv_joint: 処理中にエラーが発生{e}')

    #!###################################################################################
    # home_path

    def _home_path(self):
        return os.path.expanduser("~")

    # ----------------------------------------------------------------------------------
    # downloads path

    def _downloads_path(self):
        home = self._home_path()
        downloads_path = os.path.join(home, "Downloads")
        self.logger.debug(f'downloads_path: {downloads_path}')
        return downloads_path

    # ----------------------------------------------------------------------------------
