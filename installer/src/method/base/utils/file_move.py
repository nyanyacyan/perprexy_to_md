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


class FileMove:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()
        self.currentDate = datetime.now().strftime("%y%m%d_%H%M%S")
    #!###################################################################################
    # 結合して書き込む

    def move_csv_dl_to_outputDir(self, account_dir_name: str, sub_dir_name: str, file_name_head: str, extension: str):
        try:
            downloads_path = Path(self._downloads_path())

            search_file_name_word = f"{file_name_head}*{extension}"
            self.logger.debug(f'search_file_name_word: {search_file_name_word}')

            matching_files = list(downloads_path.glob(search_file_name_word))
            self.logger.debug(f'matching_files: {matching_files}')

            if not matching_files:
                self.logger.warning(f'{self.__class__.__name__} 指定されているパターンのファイルがありませんでした: {file_name_head}*.{extension}')
                return None

            old_path = matching_files[0]
            self.logger.debug(f'old_path: {old_path}\n old_path type: {type(old_path)}\nexists: {old_path.exists()}')
            new_path = self._result_dir_path(account_dir_name=account_dir_name, sub_dir_name=sub_dir_name, file_name=old_path.stem, extension=extension)
            self.logger.debug(f'new_path: {new_path}')
            shutil.move(old_path, new_path)
            return new_path

        except Exception as e:
            self.logger.error(f'{self.__class__.__name__}: write_csv_joint: 処理中にエラーが発生{e}')

    #!###################################################################################
    # 結合して書き込む

    def move_csv_dl_to_outputDir_list(self, account_dir_name: str, sub_dir_name: str, file_name_heads: List, extension: str):
        try:
            downloads_path = Path(self._downloads_path())
            all_matching_files = []

            for head in file_name_heads:
                search_file_name_word = f"{head}*{extension}"
                self.logger.debug(f'search_file_name_word: {search_file_name_word}')

                matching_files = list(downloads_path.glob(search_file_name_word))
                self.logger.debug(f'matching_files: {matching_files}')
                all_matching_files.extend(matching_files)

            if not matching_files:
                self.logger.warning(f'{self.__class__.__name__} 指定されているパターンのファイルがありませんでした: {file_name_head}*.{extension}')
                return None

            moved_files = []
            for old_path in all_matching_files:
                self.logger.debug(f'old_path: {old_path}\n old_path type: {type(old_path)}\nexists: {old_path.exists()}')
                new_path = self._result_dir_path(account_dir_name=account_dir_name, sub_dir_name=sub_dir_name, file_name=old_path.stem, extension=extension)
                self.logger.debug(f'new_path: {new_path}')
                shutil.move(old_path, new_path)
                moved_files.append(new_path)
            return moved_files

        except Exception as e:
            self.logger.error(f'{self.__class__.__name__}: write_csv_joint: 処理中にエラーが発生{e}')

    #!###################################################################################
    # ファイルの基本の移動

    def base_file_move(self, old_path: str, new_path: str):
        try:
            self.logger.debug(f'\nold_path: {old_path}\nnew_path: {new_path}')
            shutil.move(old_path, new_path)
            self.logger.info(f'ファイルの移動完了: {new_path}')
            return new_path

        except Exception as e:
            self.logger.error(f'{self.__class__.__name__} ファイルの移動中にエラー発生: {e}')

    ####################################################################################
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
    # 移動先のpath

    def _result_dir_path(self, account_dir_name: str, sub_dir_name: str, file_name: str, extension: str):
        return self.path.result_ac_date_sub_path(account_dir_name=account_dir_name, sub_dir_name=sub_dir_name, file_name=file_name, extension=extension)
