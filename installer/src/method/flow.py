# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/ccx_csv_to_drive/installer/src"
# export PYTHONPATH="/Users/nyanyacyan/Desktop/Project_file/ccx_csv_to_drive/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time
import pandas as pd
import concurrent.futures
from typing import Dict
from datetime import datetime, date, timedelta

# 自作モジュール
from method.base.utils.logger import Logger
from method.base.selenium.chrome import ChromeManager
from method.base.selenium.loginWithId import SingleSiteIDLogin
from method.base.selenium.seleniumBase import SeleniumBasicOperations
from method.base.spreadsheet.spreadsheetRead import GetDataGSSAPI
from method.base.selenium.get_element import GetElement
from method.base.decorators.decorators import Decorators
from method.base.utils.time_manager import TimeManager
from method.base.selenium.google_drive_download import GoogleDriveDownload
from method.base.spreadsheet.spreadsheetWrite import GssWrite
from method.base.spreadsheet.select_cell import GssSelectCell
from method.base.spreadsheet.err_checker_write import GssCheckerErrWrite
from method.base.selenium.loginWithId import SingleSiteIDLogin
from method.base.utils.popup import Popup
from method.base.selenium.click_element import ClickElement
from method.base.utils.file_move import FileMove
from method.base.selenium.google_drive_upload import GoogleDriveUpload

# Flow
from method.download_flow import FollowerDownloadFlow, EngagementDownloadFlow, PostDownloadFlow, StoriesDownloadFlow

# const
from method.const_element import GssInfo, LoginInfo, ErrCommentInfo, PopUpComment, Element

deco = Decorators()

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class FlowProcess:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.time_manager = TimeManager()
        self.gss_read = GetDataGSSAPI()
        self.gss_write = GssWrite()
        self.drive_download = GoogleDriveDownload()
        self.select_cell = GssSelectCell()
        self.gss_check_err_write = GssCheckerErrWrite()
        self.popup = Popup()

        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # const
        self.const_gss_info = GssInfo.CCX.value
        self.const_login_info = LoginInfo.CCX.value
        self.const_err_cmt_dict = ErrCommentInfo.CCX.value
        self.popup_cmt = PopUpComment.CCX.value


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 各メソッドをまとめる

    def parallel_process(self, max_workers: int = 1):
        try:
            # スプシにアクセス（Worksheet指定）
            df = self.gss_read._get_df_gss_url(gss_info=self.const_gss_info)
            df_filtered = df[df["チェック"] == "TRUE"]
            self.logger.debug(f'DataFrame: {df_filtered.head()}')

            # 並列処理
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []

                for i, row in df_filtered.iterrows():
                    row_num = i + 1
                    get_gss_row_dict = row.to_dict()  # ここにgss情報

                    # 完了通知column名
                    complete_datetime_col_name = self.const_gss_info["POST_COMPLETE_DATE"]

                    # エラーcolumn名
                    err_datetime_col_name = self.const_gss_info["ERROR_DATETIME"]
                    err_cmt_col_name = self.const_gss_info["ERROR_COMMENT"]

                    complete_cell = self.select_cell.get_cell_address( gss_row_dict=get_gss_row_dict, col_name=complete_datetime_col_name, row_num=row_num, )

                    err_datetime_cell = self.select_cell.get_cell_address( gss_row_dict=get_gss_row_dict, col_name=err_datetime_col_name, row_num=row_num, )
                    err_cmt_cell = self.select_cell.get_cell_address( gss_row_dict=get_gss_row_dict, col_name=err_cmt_col_name, row_num=row_num, )

                    # `SingleProcess` を **新しく作成**
                    single_flow_instance = SingleProcess()

                    future = executor.submit( single_flow_instance._single_process, gss_row_data=get_gss_row_dict, gss_info=self.const_gss_info, complete_cell=complete_cell, err_datetime_cell=err_datetime_cell, err_cmt_cell=err_cmt_cell, login_info=self.const_login_info, )

                    futures.append(future)

                concurrent.futures.wait(futures)

            self.popup.popupCommentOnly(
                popupTitle=self.popup_cmt["ALL_COMPLETE_TITLE"],
                comment=self.popup_cmt["ALL_COMPLETE_COMMENT"],
            )

        except Exception as e:
            self.logger.error(f'{self.__class__.__name__} 処理中にエラーが発生: {e}')



    # ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class SingleProcess:
    def __init__(self):
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()
        self.timestamp = datetime.now()
        self.timestamp_two = self.timestamp.strftime("%Y-%m-%d %H:%M")
        self.date_only_stamp = self.timestamp.date().strftime("%m月%d日")

        # const
        self.const_gss_info = GssInfo.CCX.value
        self.const_login_info = LoginInfo.CCX.value
        self.const_element = Element.CCX.value
        self.const_err_cmt_dict = ErrCommentInfo.CCX.value
        self.popup_cmt = PopUpComment.CCX.value

# **********************************************************************************
    # ----------------------------------------------------------------------------------


    def _single_process(self, gss_row_data: Dict, gss_info: Dict, complete_cell: str, err_datetime_cell: str, err_cmt_cell: str, login_info: Dict):
        """ 各プロセスを実行する """

        # ✅ Chrome の起動をここで行う
        self.chromeManager = ChromeManager()
        self.chrome = self.chromeManager.flowSetupChrome()

        try:
            # インスタンスの作成 (chrome を引数に渡す)
            self.login = SingleSiteIDLogin(chrome=self.chrome)
            self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
            self.get_element = GetElement(chrome=self.chrome)
            self.selenium = SeleniumBasicOperations(chrome=self.chrome)
            self.gss_read = GetDataGSSAPI()
            self.gss_write = GssWrite()
            self.drive_download = GoogleDriveDownload()
            self.drive_upload = GoogleDriveUpload()
            self.select_cell = GssSelectCell()
            self.gss_check_err_write = GssCheckerErrWrite()
            self.popup = Popup()
            self.click_element = ClickElement(chrome=self.chrome)
            self.file_move = FileMove()

            # URLのアクセス→ID入力→Passの入力→ログイン
            self.login.flow_login_id_input_url( login_info=login_info, login_url=login_info["LOGIN_URL"], id_text=gss_row_data[self.const_gss_info["ID"]], pass_text=gss_row_data[self.const_gss_info["PASSWORD"]], gss_info=gss_info, err_datetime_cell=err_datetime_cell, err_cmt_cell=err_cmt_cell )

            # フォロワー分析クリック → フォロワーチャート
            # ダウンロードFlow
            follower_flow = FollowerDownloadFlow(chrome=self.chrome)
            follower_upload_file = follower_flow.downloads_process(gss_row_data=gss_row_data, err_datetime_cell=err_datetime_cell, err_cmt_cell=err_cmt_cell)


            # エンゲージメント分析をクリック → エンゲージメントの推移、プロフィールインサイトチャート
            # ダウンロードFlow
            engage_flow = EngagementDownloadFlow(chrome=self.chrome)
            engage_upload_file_list = engage_flow.downloads_process(gss_row_data=gss_row_data, err_datetime_cell=err_datetime_cell, err_cmt_cell=err_cmt_cell)

            # 投稿一覧 → インサイト投稿一覧
            # ダウンロードFlow
            post_flow = PostDownloadFlow(chrome=self.chrome)
            post_upload_file = post_flow.downloads_process(gss_row_data=gss_row_data, err_datetime_cell=err_datetime_cell, err_cmt_cell=err_cmt_cell)

            # ストーリーズ分析をクリック → ストーリーズ投稿一覧
            # ダウンロードFlow
            stories_flow = StoriesDownloadFlow(chrome=self.chrome)
            stories_upload_file = stories_flow.downloads_process(gss_row_data=gss_row_data, err_datetime_cell=err_datetime_cell, err_cmt_cell=err_cmt_cell)

            # upload_pathをリスト化
            upload_path_list = [item for x in [follower_upload_file, engage_upload_file_list, post_upload_file, stories_upload_file] for item in (x if isinstance(x, list) else [x])]
            self.logger.info(f'upload_path_list: {upload_path_list}')

            # アップロードフォルダからすべてのファイルをDriveアップロード
            count = 0
            for upload_path in upload_path_list:
                self.logger.debug(f'upload_path: {upload_path}')
                self.drive_upload.upload_file_to_drive(parents_folder_url=self.const_gss_info["DRIVE_PARENTS_URL"], file_path=upload_path, gss_info=gss_info, account_name=gss_row_data[self.const_gss_info["NAME"]])
                count += 1
                self.logger.info(f'{count} つ目のファイルアップロード完了 {upload_path}')

            # 実施を成功欄に日付を書込をする
            self.gss_write.write_data_by_url(gss_info, complete_cell, input_data=str(self.timestamp_two))

            self.logger.info(f'{gss_row_data[self.const_gss_info["NAME"]]}: 処理完了')

        except TimeoutError:
            timeout_comment = "タイムエラー：ログインに失敗している可能性があります。"
            self.logger.error(f'{self.__class__.__name__} {timeout_comment}')
            # エラータイムスタンプ
            self.gss_write.write_data_by_url(gss_info=gss_info, cell=err_datetime_cell, input_data=self.timestamp)

            # エラーコメント
            self.gss_write.write_data_by_url(gss_info=gss_info, cell=err_cmt_cell, input_data=timeout_comment)

        except Exception as e:
            process_error_comment = f"{self.__class__.__name__} 処理中にエラーが発生 {e}"
            self.logger.error(process_error_comment)
            # エラータイムスタンプ
            self.logger.debug(f'self.timestamp: {self.timestamp}')
            self.gss_write.write_data_by_url(gss_info=gss_info, cell=err_datetime_cell, input_data=self.timestamp_two)

            # エラーコメント
            self.gss_write.write_data_by_url(gss_info=gss_info, cell=err_cmt_cell, input_data=process_error_comment)

        finally:
            delete_count = 0
            for upload_path in upload_path_list:
                self._delete_file(upload_path)  # CSVファイルを消去
                delete_count += 1
                self.logger.info(f'{delete_count} つ目のCSVファイルの削除を実施')

            # ✅ Chrome を終了
            self.chrome.quit()


    # ----------------------------------------------------------------------------------

    def _delete_file(self, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)
            self.logger.info(f'指定のファイルの削除を実施: {file_path}')

        else:
            self.logger.error(f'{self.__class__.__name__} ファイルが存在しません: {file_path}')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == "__main__":

    test_flow = FlowProcess()
    # 引数入力
    test_flow.parallel_process()
