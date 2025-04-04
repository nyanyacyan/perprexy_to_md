# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/multi_site_post_flow/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, shutil
from typing import Dict
from datetime import datetime
from selenium.webdriver.chrome.webdriver import WebDriver

# 自作モジュール
from method.base.utils.logger import Logger
from method.base.utils.path import BaseToPath
from method.base.selenium.chrome import ChromeManager
from method.base.selenium.loginWithId import SingleSiteIDLogin
from method.base.selenium.seleniumBase import SeleniumBasicOperations
from method.base.spreadsheet.spreadsheetRead import GetDataGSSAPI
from method.base.selenium.get_element import GetElement
from method.base.selenium.click_element import ClickElement
from method.base.decorators.decorators import Decorators
from method.base.utils.time_manager import TimeManager
from method.base.selenium.google_drive_download import GoogleDriveDownload
from method.base.spreadsheet.spreadsheetWrite import GssWrite
from method.base.spreadsheet.select_cell import GssSelectCell
from method.base.spreadsheet.err_checker_write import GssCheckerErrWrite
from method.base.utils.popup import Popup
from method.base.utils.file_move import FileMove
from method.base.utils.file_delete import DownloadFileDelete
from method.base.utils.zip import ZipOperation
from method.base.utils.search_file_name_head import SearchFileNameHead

# const
from method.const_element import GssInfo, LoginInfo, ErrCommentInfo, PopUpComment, FollowerAnalysisElement, EngagementAnalysisElement, PostAnalysisElement, StoriesAnalysisElement

deco = Decorators()

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FollowerDownloadFlow:
    def __init__(self, chrome: WebDriver):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chrome = chrome

        # 必要info
        self.gss_info = GssInfo.CCX.value

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
        self.get_element = GetElement(chrome=self.chrome)
        self.click_element = ClickElement(chrome=self.chrome)
        self.time_manager = TimeManager()
        self.selenium = SeleniumBasicOperations(chrome=self.chrome)
        self.gss_read = GetDataGSSAPI()
        self.gss_write = GssWrite()
        self.drive_download = GoogleDriveDownload()
        self.select_cell = GssSelectCell()
        self.gss_check_err_write = GssCheckerErrWrite()
        self.popup = Popup()
        self.path = BaseToPath()
        self.file_move = FileMove()
        self.zip = ZipOperation()
        self.search_file_name_head = SearchFileNameHead()
        self.downloads_file_delete = DownloadFileDelete()

        # const
        self.const_gss_info = GssInfo.CCX.value
        self.const_login_info = LoginInfo.CCX.value
        self.const_err_cmt_dict = ErrCommentInfo.CCX.value
        self.popup_cmt = PopUpComment.CCX.value

        # downloads_const
        self.const_download_kinds_info = FollowerAnalysisElement.CCX.value

        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    #!###################################################################################
    # 準備工程 スプシチェッカー > 写真のダウンロード > 動画のダウンロード

    def downloads_process( self, gss_row_data: Dict, err_datetime_cell: str, err_cmt_cell: str, ):
        try:
            # ダウンロードフォルダに既存でないかチェック→あったら削除
            self.downloads_file_delete.delete_in_download_folder(file_name_head=self.const_download_kinds_info["ZIP_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["ZIP_EXTENSION"])

            # 対象の分析をクリック
            self.click_element.clickElement(value=self.const_download_kinds_info["ANALYSIS_VOL"])
            self.logger.warning(f'{self.__class__.__name__} 対象の分析をクリック: 実施済み')
            self.selenium._random_sleep()

            # 一括ダウンロードをクリック
            self.click_element.clickElement(value=self.const_download_kinds_info["BULK_DOWNLOAD_BTN_VOL"])
            self.logger.warning(f'{self.__class__.__name__} 対象の分析をクリック: 実施済み')
            self.selenium._random_sleep()

            # Zipファイルの移動 → result_output → アカウント → date → *zip
            new_zip_path = self.file_move.move_csv_dl_to_outputDir(account_dir_name=gss_row_data[self.const_gss_info["NAME"]], sub_dir_name=self.const_download_kinds_info["DOWNLOAD_DIR_NAME"], file_name_head=self.const_download_kinds_info["ZIP_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["ZIP_EXTENSION"])
            self.selenium._random_sleep()

            # zipの解凍
            unzip_folder_dir = self.zip.unzip_same_position(zipfile_path=new_zip_path)
            self.selenium._random_sleep()

            # 対象ファイルのPathを取得
            discovery_file = self.search_file_name_head.get_search_file_name_head(search_folder_path=unzip_folder_dir, file_name_head=self.const_download_kinds_info["CSV_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["CSV_EXTENSION"])
            self.selenium._random_sleep()

            # アップロード先のPathを取得
            file_name = os.path.basename(discovery_file)  # ファイルまでのPathを取得
            self.logger.debug(f'base_dir: {file_name}')
            upload_path = self._get_upload_file_path(account_dir_name=gss_row_data[self.const_gss_info["NAME"]], file_name=file_name)

            # アップロードファイルに移動
            self.file_move.base_file_move(old_path=discovery_file, new_path=upload_path)
            self.logger.info(f'アカウント名: {gss_row_data[self.const_gss_info["NAME"]]} ダウンロード処理完了')


        except Exception as e:
            error_comment = f"フォロワーダウンロードflow処理中にエラーが発生: {e}"

            self.logger.error(f"{self.__class__.__name__} {error_comment}")

            # エラータイムスタンプ
            self.gss_write.write_data_by_url(gss_info=self.const_gss_info, cell=err_datetime_cell, input_data=self.timestamp)

            # エラーコメント
            self.gss_write.write_data_by_url(gss_info=self.const_gss_info, cell=err_cmt_cell, input_data=error_comment)

        finally:
            # Zipを削除
            self._delete_file(file_path=new_zip_path)
            self._delete_file(file_path=unzip_folder_dir)
            return upload_path

    #!###################################################################################
    # ----------------------------------------------------------------------------------
    # downloads path

    def _downloads_path(self):
        home = self._home_path()
        downloads_path = os.path.join(home, "Downloads")
        self.logger.debug(f'downloads_path: {downloads_path}')
        return downloads_path

    # ----------------------------------------------------------------------------------
    # アップロード用のpath

    def _get_upload_file_path(self, account_dir_name: str, file_name: str):
        dir_name = self.const_download_kinds_info["UPLOAD_DIR_NAME"]
        self.logger.debug(f'dir_name: {dir_name}')
        self.logger.debug(f'file_name: {file_name}')
        upload_file_path = self.path.result_ac_date_sub_path_two(account_dir_name=account_dir_name, sub_dir_name=dir_name, file_name=file_name)
        self.logger.debug(f'upload_file_path: {upload_file_path}')
        return upload_file_path

    # ----------------------------------------------------------------------------------
    # 不必要なファイルを削除

    def _delete_file(self, file_path: str):
        if os.path.isfile(file_path):
            os.remove(file_path)
            self.logger.info(f'指定のファイル削除を実施: {file_path}')

        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            self.logger.info(f'指定のフォルダ削除を実施: {file_path}')

        else:
            self.logger.error(f'{self.__class__.__name__} ファイルが存在しません: {file_path}')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# **********************************************************************************
# 一連の流れ

class EngagementDownloadFlow:
    def __init__(self, chrome: WebDriver):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chrome = chrome

        # 必要info
        self.gss_info = GssInfo.CCX.value

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
        self.get_element = GetElement(chrome=self.chrome)
        self.click_element = ClickElement(chrome=self.chrome)
        self.time_manager = TimeManager()
        self.selenium = SeleniumBasicOperations(chrome=self.chrome)
        self.gss_read = GetDataGSSAPI()
        self.gss_write = GssWrite()
        self.drive_download = GoogleDriveDownload()
        self.select_cell = GssSelectCell()
        self.gss_check_err_write = GssCheckerErrWrite()
        self.popup = Popup()
        self.path = BaseToPath()
        self.file_move = FileMove()
        self.zip = ZipOperation()
        self.search_file_name_head = SearchFileNameHead()
        self.downloads_file_delete = DownloadFileDelete()

        # const
        self.const_gss_info = GssInfo.CCX.value
        self.const_login_info = LoginInfo.CCX.value
        self.const_err_cmt_dict = ErrCommentInfo.CCX.value
        self.popup_cmt = PopUpComment.CCX.value

        # downloads_const
        self.const_download_kinds_info = EngagementAnalysisElement.CCX.value

        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    #!###################################################################################
    # 準備工程 スプシチェッカー > 写真のダウンロード > 動画のダウンロード

    def downloads_process( self, gss_row_data: Dict, err_datetime_cell: str, err_cmt_cell: str, ):
        try:
            # ダウンロードフォルダに既存でないかチェック→あったら削除
            self.downloads_file_delete.delete_in_download_folder(file_name_head=self.const_download_kinds_info["ZIP_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["ZIP_EXTENSION"])

            # 対象の分析をクリック
            self.click_element.clickElement(value=self.const_download_kinds_info["ANALYSIS_VOL"])
            self.logger.warning(f'{self.__class__.__name__} 対象の分析をクリック: 実施済み')
            self.selenium._random_sleep()

            # 一括ダウンロードをクリック
            self.click_element.clickElement(value=self.const_download_kinds_info["BULK_DOWNLOAD_BTN_VOL"])
            self.logger.warning(f'{self.__class__.__name__} 対象の分析をクリック: 実施済み')
            self.selenium._random_sleep()

            # Zipファイルの移動 → result_output → アカウント → date → *zip
            new_zip_path = self.file_move.move_csv_dl_to_outputDir(account_dir_name=gss_row_data[self.const_gss_info["NAME"]], sub_dir_name=self.const_download_kinds_info["DOWNLOAD_DIR_NAME"], file_name_head=self.const_download_kinds_info["ZIP_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["ZIP_EXTENSION"])
            self.selenium._random_sleep()

            # zipの解凍
            unzip_folder_dir = self.zip.unzip_same_position(zipfile_path=new_zip_path)
            self.selenium._random_sleep()

            discovery_files = []

            # 対象ファイルのPathを取得
            discovery_file_first = self.search_file_name_head.get_search_file_name_head(search_folder_path=unzip_folder_dir, file_name_head=self.const_download_kinds_info["CSV_FILE_HEAD_FIRST_NAME"], extension=self.const_download_kinds_info["CSV_EXTENSION"])
            discovery_files.append(discovery_file_first)

            discovery_file_second = self.search_file_name_head.get_search_file_name_head(search_folder_path=unzip_folder_dir, file_name_head=self.const_download_kinds_info["CSV_FILE_HEAD_SECOND_NAME"], extension=self.const_download_kinds_info["CSV_EXTENSION"])
            discovery_files.append(discovery_file_second)

            upload_path_list = []

            for discovery_file in discovery_files:

                # アップロード先のPathを取得
                file_name = os.path.basename(discovery_file)  # ファイルまでのPathを取得
                upload_path = self._get_upload_file_path(account_dir_name=gss_row_data[self.const_gss_info["NAME"]], file_name=file_name)

                # アップロードファイルに移動
                self.file_move.base_file_move(old_path=discovery_file, new_path=upload_path)
                upload_path_list.append(upload_path)

            self.logger.debug(f'upload_path_list: {upload_path_list}')
            self.logger.info(f'アカウント名: {gss_row_data[self.const_gss_info["NAME"]]} ダウンロード処理完了')

        except Exception as e:
            error_comment = "エンゲージメントダウンロードflow処理中にエラーが発生"

            self.logger.error(f"{self.__class__.__name__} {error_comment}: {e}")

            # エラータイムスタンプ
            self.gss_write.write_data_by_url(gss_info=self.const_gss_info, cell=err_datetime_cell, input_data=self.timestamp)

            # エラーコメント
            self.gss_write.write_data_by_url(gss_info=self.const_gss_info, cell=err_cmt_cell, input_data=error_comment)

        finally:
            # Zipを削除
            self._delete_file(file_path=new_zip_path)
            self._delete_file(file_path=unzip_folder_dir)
            return upload_path_list

    #!###################################################################################
    # ----------------------------------------------------------------------------------
    # アップロード用のpath

    def _get_upload_file_path(self, account_dir_name: str, file_name: str):
        dir_name = self.const_download_kinds_info["UPLOAD_DIR_NAME"]
        upload_file_path = self.path.result_ac_date_sub_path_two(account_dir_name=account_dir_name, sub_dir_name=dir_name, file_name=file_name)
        return upload_file_path

    # ----------------------------------------------------------------------------------
    # 不必要なファイルを削除

    def _delete_file(self, file_path: str):
        if os.path.isfile(file_path):
            os.remove(file_path)
            self.logger.info(f'指定のファイル削除を実施: {file_path}')

        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            self.logger.info(f'指定のフォルダ削除を実施: {file_path}')

        else:
            self.logger.error(f'{self.__class__.__name__} ファイルが存在しません: {file_path}')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# **********************************************************************************
# 一連の流れ

class PostDownloadFlow:
    def __init__(self, chrome: WebDriver):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chrome = chrome

        # 必要info
        self.gss_info = GssInfo.CCX.value

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
        self.get_element = GetElement(chrome=self.chrome)
        self.click_element = ClickElement(chrome=self.chrome)
        self.time_manager = TimeManager()
        self.selenium = SeleniumBasicOperations(chrome=self.chrome)
        self.gss_read = GetDataGSSAPI()
        self.gss_write = GssWrite()
        self.drive_download = GoogleDriveDownload()
        self.select_cell = GssSelectCell()
        self.gss_check_err_write = GssCheckerErrWrite()
        self.popup = Popup()
        self.path = BaseToPath()
        self.file_move = FileMove()
        self.zip = ZipOperation()
        self.search_file_name_head = SearchFileNameHead()
        self.downloads_file_delete = DownloadFileDelete()

        # const
        self.const_gss_info = GssInfo.CCX.value
        self.const_login_info = LoginInfo.CCX.value
        self.const_err_cmt_dict = ErrCommentInfo.CCX.value
        self.popup_cmt = PopUpComment.CCX.value

        # downloads_const
        self.const_download_kinds_info = PostAnalysisElement.CCX.value

        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    #!###################################################################################
    # 準備工程 スプシチェッカー > 写真のダウンロード > 動画のダウンロード

    def downloads_process( self, gss_row_data: Dict, err_datetime_cell: str, err_cmt_cell: str, ):
        try:
            # ダウンロードフォルダに既存でないかチェック→あったら削除
            self.downloads_file_delete.delete_in_download_folder(file_name_head=self.const_download_kinds_info["ZIP_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["ZIP_EXTENSION"])

            # 対象の分析をクリック
            self.click_element.clickElement(value=self.const_download_kinds_info["ANALYSIS_VOL"])
            self.logger.warning(f'{self.__class__.__name__} 対象の分析をクリック: 実施済み')
            self.selenium._random_sleep()

            # 一括ダウンロードをクリック
            self.click_element.clickElement(value=self.const_download_kinds_info["BULK_DOWNLOAD_BTN_VOL"])
            self.logger.warning(f'{self.__class__.__name__} 対象の分析をクリック: 実施済み')
            self.selenium._random_sleep()

            # Zipファイルの移動 → result_output → アカウント → date → *zip
            new_zip_path = self.file_move.move_csv_dl_to_outputDir(account_dir_name=gss_row_data[self.const_gss_info["NAME"]], sub_dir_name=self.const_download_kinds_info["DOWNLOAD_DIR_NAME"], file_name_head=self.const_download_kinds_info["ZIP_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["ZIP_EXTENSION"])
            self.selenium._random_sleep()

            # zipの解凍
            unzip_folder_dir = self.zip.unzip_same_position(zipfile_path=new_zip_path)
            self.selenium._random_sleep()

            # 対象ファイルのPathを取得
            discovery_file = self.search_file_name_head.get_search_file_name_head(search_folder_path=unzip_folder_dir, file_name_head=self.const_download_kinds_info["CSV_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["CSV_EXTENSION"])
            self.selenium._random_sleep()

            # アップロード先のPathを取得
            file_name = os.path.basename(discovery_file)  # ファイルまでのPathを取得
            self.logger.debug(f'base_dir: {file_name}')
            upload_path = self._get_upload_file_path(account_dir_name=gss_row_data[self.const_gss_info["NAME"]], file_name=file_name)

            # アップロードファイルに移動
            self.file_move.base_file_move(old_path=discovery_file, new_path=upload_path)
            self.logger.info(f'アカウント名: {gss_row_data[self.const_gss_info["NAME"]]} ダウンロード処理完了')


        except Exception as e:
            error_comment = "フォロワーダウンロードflow処理中にエラーが発生"

            self.logger.error(f"{self.__class__.__name__} {error_comment}: {e}")

            # エラータイムスタンプ
            self.gss_write.write_data_by_url(gss_info=self.const_gss_info, cell=err_datetime_cell, input_data=self.timestamp)

            # エラーコメント
            self.gss_write.write_data_by_url(gss_info=self.const_gss_info, cell=err_cmt_cell, input_data=error_comment)

        finally:
            # Zipを削除
            self._delete_file(file_path=new_zip_path)
            self._delete_file(file_path=unzip_folder_dir)
            return upload_path

    #!###################################################################################
    # ----------------------------------------------------------------------------------
    # downloads path

    def _downloads_path(self):
        home = self._home_path()
        downloads_path = os.path.join(home, "Downloads")
        self.logger.debug(f'downloads_path: {downloads_path}')
        return downloads_path

    # ----------------------------------------------------------------------------------
    # アップロード用のpath

    def _get_upload_file_path(self, account_dir_name: str, file_name: str):
        dir_name = self.const_download_kinds_info["UPLOAD_DIR_NAME"]
        self.logger.debug(f'dir_name: {dir_name}')
        self.logger.debug(f'file_name: {file_name}')
        upload_file_path = self.path.result_ac_date_sub_path_two(account_dir_name=account_dir_name, sub_dir_name=dir_name, file_name=file_name)
        self.logger.debug(f'upload_file_path: {upload_file_path}')
        return upload_file_path

    # ----------------------------------------------------------------------------------
    # 不必要なファイルを削除

    def _delete_file(self, file_path: str):
        if os.path.isfile(file_path):
            os.remove(file_path)
            self.logger.info(f'指定のファイル削除を実施: {file_path}')

        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            self.logger.info(f'指定のフォルダ削除を実施: {file_path}')

        else:
            self.logger.error(f'{self.__class__.__name__} ファイルが存在しません: {file_path}')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# **********************************************************************************
# 一連の流れ

class StoriesDownloadFlow:
    def __init__(self, chrome: WebDriver):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chrome = chrome

        # 必要info
        self.gss_info = GssInfo.CCX.value

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
        self.get_element = GetElement(chrome=self.chrome)
        self.click_element = ClickElement(chrome=self.chrome)
        self.time_manager = TimeManager()
        self.selenium = SeleniumBasicOperations(chrome=self.chrome)
        self.gss_read = GetDataGSSAPI()
        self.gss_write = GssWrite()
        self.drive_download = GoogleDriveDownload()
        self.select_cell = GssSelectCell()
        self.gss_check_err_write = GssCheckerErrWrite()
        self.popup = Popup()
        self.path = BaseToPath()
        self.file_move = FileMove()
        self.zip = ZipOperation()
        self.search_file_name_head = SearchFileNameHead()
        self.downloads_file_delete = DownloadFileDelete()

        # const
        self.const_gss_info = GssInfo.CCX.value
        self.const_login_info = LoginInfo.CCX.value
        self.const_err_cmt_dict = ErrCommentInfo.CCX.value
        self.popup_cmt = PopUpComment.CCX.value

        # downloads_const
        self.const_download_kinds_info = StoriesAnalysisElement.CCX.value

        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    #!###################################################################################
    # 準備工程 スプシチェッカー > 写真のダウンロード > 動画のダウンロード

    def downloads_process( self, gss_row_data: Dict, err_datetime_cell: str, err_cmt_cell: str, ):
        try:
            # ダウンロードフォルダに既存でないかチェック→あったら削除
            self.downloads_file_delete.delete_in_download_folder(file_name_head=self.const_download_kinds_info["ZIP_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["ZIP_EXTENSION"])

            # 対象の分析をクリック
            self.click_element.clickElement(value=self.const_download_kinds_info["ANALYSIS_VOL"])
            self.logger.warning(f'{self.__class__.__name__} 対象の分析をクリック: 実施済み')
            self.selenium._random_sleep()

            # 一括ダウンロードをクリック
            self.click_element.clickElement(value=self.const_download_kinds_info["BULK_DOWNLOAD_BTN_VOL"])
            self.logger.warning(f'{self.__class__.__name__} 対象の分析をクリック: 実施済み')
            self.selenium._random_sleep()

            # Zipファイルの移動 → result_output → アカウント → date → *zip
            new_zip_path = self.file_move.move_csv_dl_to_outputDir(account_dir_name=gss_row_data[self.const_gss_info["NAME"]], sub_dir_name=self.const_download_kinds_info["DOWNLOAD_DIR_NAME"], file_name_head=self.const_download_kinds_info["ZIP_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["ZIP_EXTENSION"])
            self.selenium._random_sleep()

            # zipの解凍
            unzip_folder_dir = self.zip.unzip_same_position(zipfile_path=new_zip_path)
            self.selenium._random_sleep()

            # 対象ファイルのPathを取得
            discovery_file = self.search_file_name_head.get_search_file_name_head(search_folder_path=unzip_folder_dir, file_name_head=self.const_download_kinds_info["CSV_FILE_HEAD_NAME"], extension=self.const_download_kinds_info["CSV_EXTENSION"])
            self.selenium._random_sleep()

            # アップロード先のPathを取得
            file_name = os.path.basename(discovery_file)  # ファイルまでのPathを取得
            self.logger.debug(f'base_dir: {file_name}')
            upload_path = self._get_upload_file_path(account_dir_name=gss_row_data[self.const_gss_info["NAME"]], file_name=file_name)

            # アップロードファイルに移動
            self.file_move.base_file_move(old_path=discovery_file, new_path=upload_path)
            self.logger.info(f'アカウント名: {gss_row_data[self.const_gss_info["NAME"]]} ダウンロード処理完了')

        except Exception as e:
            error_comment = "フォロワーダウンロードflow処理中にエラーが発生"

            self.logger.error(f"{self.__class__.__name__} {error_comment}: {e}")

            # エラータイムスタンプ
            self.gss_write.write_data_by_url(gss_info=self.const_gss_info, cell=err_datetime_cell, input_data=self.timestamp)

            # エラーコメント
            self.gss_write.write_data_by_url(gss_info=self.const_gss_info, cell=err_cmt_cell, input_data=error_comment)

        finally:
            # Zipを削除
            self._delete_file(file_path=new_zip_path)
            self._delete_file(file_path=unzip_folder_dir)
            return upload_path

    #!###################################################################################
    # ----------------------------------------------------------------------------------
    # downloads path

    def _downloads_path(self):
        home = self._home_path()
        downloads_path = os.path.join(home, "Downloads")
        self.logger.debug(f'downloads_path: {downloads_path}')
        return downloads_path

    # ----------------------------------------------------------------------------------
    # アップロード用のpath

    def _get_upload_file_path(self, account_dir_name: str, file_name: str):
        dir_name = self.const_download_kinds_info["UPLOAD_DIR_NAME"]
        self.logger.debug(f'dir_name: {dir_name}')
        self.logger.debug(f'file_name: {file_name}')
        upload_file_path = self.path.result_ac_date_sub_path_two(account_dir_name=account_dir_name, sub_dir_name=dir_name, file_name=file_name)
        self.logger.debug(f'upload_file_path: {upload_file_path}')
        return upload_file_path

    # ----------------------------------------------------------------------------------
    # 不必要なファイルを削除

    def _delete_file(self, file_path: str):
        if os.path.isfile(file_path):
            os.remove(file_path)
            self.logger.info(f'指定のファイル削除を実施: {file_path}')

        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            self.logger.info(f'指定のフォルダ削除を実施: {file_path}')

        else:
            self.logger.error(f'{self.__class__.__name__} ファイルが存在しません: {file_path}')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
