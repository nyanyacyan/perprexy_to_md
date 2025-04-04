# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, re
from typing import Dict
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
from io import BytesIO

# 自作モジュール
from method.base.utils.logger import Logger
from method.base.utils.path import BaseToPath
from method.base.utils.fileWrite import FileWrite
from method.base.spreadsheet.spreadsheetWrite import GssWrite

# const
from method.const_str import DriveMime
from method.const_element import ErrCommentInfo


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class GoogleDriveUpload:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()
        self.file_write = FileWrite()
        self.gss_write = GssWrite()

    #!###################################################################################
    # ✅ ダウンロードリクエストを送信

    def upload_file_to_drive(self, parents_folder_url: str, file_path: str, gss_info: Dict, account_name: str):
        file_name = ""
        try:
            parents_folder_id = self._get_parents_folder_id(parents_folder_url=parents_folder_url)
            self.logger.debug(f'file_path: {file_path}')
            file_name = Path(file_path).name
            self.logger.debug(f'file_name: {file_name}')

            upload_folder_id = parents_folder_id  # デフォルトで親フォルダにアップする
            self.logger.debug(f'upload_folder_id: {upload_folder_id}')
            if account_name:
                upload_folder_id = self._get_or_create_folder(gss_info=gss_info, child_folder_name=account_name, parent_folder_id=parents_folder_id)

            file_metadata = {
                'name': file_name,
                'parents': [upload_folder_id]
            }

            with open(file_path, "rb") as f:
                uploader = MediaIoBaseUpload(f, mimetype="application/octet-stream", resumable=True)

                drive_service = self._client(gss_info=gss_info)
                drive_service.files().create(body=file_metadata, media_body=uploader, fields='id', supportsAllDrives=True).execute()

                self.logger.info(f'{file_name} のアップロード処理完了')

        except Exception as e:
            self.logger.error(f'{self.__class__.__name__} ファイルアップロード中にエラーが発生: \n{e}')
            raise

    #!###################################################################################

    # ----------------------------------------------------------------------------------
    # スプシの認証プロパティ

    def _creds(self, gss_info: Dict):
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        jsonKeyPath = self.path._get_secret_key_path(file_name=gss_info['JSON_KEY_NAME'])
        creds = Credentials.from_service_account_file(jsonKeyPath, scopes=SCOPES)
        return creds

    # ----------------------------------------------------------------------------------
    # Driveへのアクセス

    def _client(self, gss_info: Dict):
        credentials = self._creds(gss_info=gss_info)
        drive_service = build("drive", "v3", credentials=credentials)
        return drive_service

    # ----------------------------------------------------------------------------------
    # 親フォルダのfolder_idを取得

    def _get_parents_folder_id(self, parents_folder_url: str):
        match_element = re.search(r'/folders/([a-zA-Z0-9_-]+)', parents_folder_url)

        if not match_element:
            raise ValueError("URLが正しくありません")

        parents_folder_id = match_element.group(1)
        self.logger.debug(f'parents_folder_id: {parents_folder_id}')

        return parents_folder_id

    # ----------------------------------------------------------------------------------
    # 子フォルダを作成

    def _create_folder(self, gss_info: Dict, child_folder_name: str, parents_folder_id: str):
        drive_service = self._client(gss_info=gss_info)
        file_metadata = {
            "name": child_folder_name,
            "mimeType": 'application/vnd.google-apps.folder',
            "parents": [parents_folder_id]
        }

        folder = drive_service.files().create(body=file_metadata, fields="id", supportsAllDrives=True).execute()
        create_folder_id = folder["id"]
        self.logger.info(f"📁 フォルダ「{child_folder_name}」を作成しました（ID: {create_folder_id}）")

        return create_folder_id

    # ----------------------------------------------------------------------------------
    # 対象のフォルダの存在確認

    def _get_or_create_folder(self, gss_info: Dict, child_folder_name: str, parent_folder_id: str):
        self.logger.debug(f'parent_folder_id: {parent_folder_id}')
        # ファイルを指定するための命令文
        query = f"name='{child_folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed = false"
        self.logger.debug(f'query: {query}')

        # drive_serviceへリクエスト→指定のファイルをくれ！
        drive_service = self._client(gss_info=gss_info)
        try:
            results = drive_service.files().list(q=query, fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
            self.logger.debug(f'results: {results}')
        except Exception as e:
            self.logger.error(f'{self.__class__.__name__} ファイルアップロード中にエラーが発生: {e}')
            raise

        # レスポンスから'files'を抽出
        get_folders = results.get('files', [])

        if get_folders:
            self.logger.info(f"フォルダ「{child_folder_name}」は既に存在します（ID: {get_folders[0]['id']}）")
            return get_folders[0]["id"]
        else:
            # フォルダがないため作成
            self.logger.warning(f"フォルダ「{child_folder_name}」がないため作成します")
            create_folder_id = self._create_folder(gss_info=gss_info, child_folder_name=child_folder_name, parents_folder_id=parent_folder_id)
            return create_folder_id

    # ----------------------------------------------------------------------------------
