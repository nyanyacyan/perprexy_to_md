# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os
from pathlib import Path

import pandas as pd
from typing import List

# 自作モジュール
from method.base.utils.logger import Logger
from method.base.utils.path import BaseToPath


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class SearchFileNameHead:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()


    ####################################################################################
    # 指定のPathにファイル名の頭部分を指定して検索

    def get_search_file_name_head(self, search_folder_path: str, file_name_head: str, extension: str):
        try:
            search_file_name_parts = f"{file_name_head}*{extension}"
            self.logger.debug(f'search_file_name_parts: {search_file_name_parts}')
            search_path = Path(search_folder_path)
            self.logger.debug(f'search_path: {search_path}')

            for f in search_path.iterdir():
                self.logger.debug(f"ファイル: {f.name}")

            matching_files = list(search_path.glob(search_file_name_parts))
            self.logger.debug(f'matching_files: {matching_files}')

            if not matching_files:
                self.logger.warning(f'{self.__class__.__name__} 指定されているパターンのファイルがありませんでした: {file_name_head}*.{extension}')
                return None

            elif len(matching_files) > 1:
                self.logger.warning(f'{self.__class__.__name__} 指定のファイルが複数あるためエラー: {file_name_head}*.{extension}')
                return None

            searched_file = matching_files[0]
            self.logger.debug(f'searched_file: {searched_file}')
            return searched_file

        except Exception as e:
            self.logger.error(f'{self.__class__.__name__} 指定のPathにファイル名の頭部分を指定して検索の処理中にエラーが発生: {e}')

    ####################################################################################

    # ----------------------------------------------------------------------------------



    # ----------------------------------------------------------------------------------



    # ----------------------------------------------------------------------------------
