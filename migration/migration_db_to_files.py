#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL 데이터를 파일로 저장하는 마이그레이션 스크립트
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

import mysql.connector
from mysql.connector import Error


class DatabaseMigration:
    def __init__(self, host: str, user: str, password: str, database: str, port: int, output: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.output = output
        self.conn = None

    def connect(self) -> bool:
        """데이터베이스에 연결"""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
            )
            print(f"✅ {self.database} 데이터베이스에 연결되었습니다.")
            return True
        except Error as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False

    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("🔌 데이터베이스 연결이 해제되었습니다.")

    def export_layouts(self):
        """레이아웃 데이터를 내보냄"""
        os.makedirs(self.output, exist_ok=True)
        layout_dir = os.path.join(self.output, "layouts")
        if os.path.exists(layout_dir):
            shutil.rmtree(layout_dir)
        os.makedirs(layout_dir, exist_ok=True)

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM template_layouts")
        data = cursor.fetchall()
        for item in data:
            file_name = item["name"].strip().replace("layouts/", "")
            with open(os.path.join(layout_dir, file_name), "w", encoding="utf-8") as f:
                f.write(self._get_default_description(item["created"], item["updated"]))
                f.write(item["content"])
        cursor.close()
        return data

    def _get_default_description(self, created: datetime, updated: datetime) -> str:
        _created = created.strftime("%Y-%m-%d %H:%M:%S") if created else None
        _updated = updated.strftime("%Y-%m-%d %H:%M:%S") if updated else None

        return (
            "{#-"
            "\n"
            "description: system migration"
            "\n"
            f"created_at: {_created}"
            "\n"
            "created_by: system"
            "\n"
            f"updated_at: {_updated}"
            "\n"
            "updated_by: system"
            "\n"
            "-#}"
            "\n"
        )

    def export_partials(self):
        """파트리얼 데이터를 내보냄"""
        os.makedirs(self.output, exist_ok=True)
        partials_dir = os.path.join(self.output, "partials")
        if os.path.exists(partials_dir):
            shutil.rmtree(partials_dir)
        os.makedirs(partials_dir, exist_ok=True)

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM template_partials")
        data = cursor.fetchall()
        for item in data:
            file_name = item["import_name"].strip()
            with open(os.path.join(partials_dir, file_name), "w", encoding="utf-8") as f:
                f.write(self._get_default_description(item["created"], item["updated"]))
                f.write(item["content"])
        cursor.close()
        return data

    def _get_layout_name(self, layout_id: int | None) -> str | None:
        if layout_id is None:
            return None
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT name 
            FROM template_layouts 
            WHERE id = %s
            """,
            (layout_id,),
        )
        data = cursor.fetchone()
        cursor.close()
        return data["name"] if data else None

    def _get_partial_import_names(self, template_id: int) -> List[str]:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT tp.import_name
            FROM template_partial_associations tpa
                    INNER JOIN template_partials tp ON tpa.partial_id = tp.id
            WHERE template_id = %s
            """,
            (template_id,),
        )
        data = cursor.fetchall()
        cursor.close()
        # 딕셔너리에서 import_name 값만 추출해서 리스트로 반환
        return [item["import_name"] for item in data]

    def export_templates(self):
        """템플릿 데이터를 내보냄"""
        os.makedirs(self.output, exist_ok=True)
        templates_dir = os.path.join(self.output, "templates")
        if os.path.exists(templates_dir):
            shutil.rmtree(templates_dir)
        os.makedirs(templates_dir, exist_ok=True)

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM templates")
        data = cursor.fetchall()
        for item in data:
            category_dir = os.path.join(templates_dir, item["code"].strip())
            os.makedirs(category_dir, exist_ok=True)
            file_name = item["format"].strip()
            layout_name = self._get_layout_name(item["layout_id"])
            partial_import_names = self._get_partial_import_names(item["id"])
            with open(os.path.join(category_dir, file_name), "w", encoding="utf-8") as f:
                f.write(self._get_default_description(item["created"], item["updated"]))
                if layout_name:
                    f.write(f"{{%- extends 'layouts/{layout_name}' -%}}\n")
                if partial_import_names:
                    for partial_import_name in partial_import_names:
                        f.write(
                            f"{{%- from 'partials/{partial_import_name}' import render as {partial_import_name} with context -%}}\n"
                        )
                f.write(item["content"])
        cursor.close()
        return data


def main(host: str, user: str, password: str, database: str, port: int, output: str):
    """MySQL 데이터를 JSON 파일로 내보내는 도구"""

    print("🚀 MySQL 데이터 마이그레이션을 시작합니다...")

    # 마이그레이션 객체 생성
    migration = DatabaseMigration(host, user, password, database, port, output)

    # 데이터베이스 연결
    if not migration.connect():
        return 1

    try:
        # 모든 테이블 내보내기
        # success = migration.export_all_tables(output)
        migration.export_layouts()
        migration.export_partials()
        migration.export_templates()
        success = True
        return 0 if success else 1
    finally:
        migration.disconnect()


if __name__ == "__main__":
    try:
        DATABASE_URL = os.environ["DATABASE_URL"]
        parsed_url = urlparse(DATABASE_URL)

        # 기본값 설정
        host = parsed_url.hostname or "127.0.0.1"
        user = parsed_url.username or "root"
        password = parsed_url.password or "1234"
        database = parsed_url.path.lstrip("/") or "noti_temply"
        port = parsed_url.port or 3306

        output = sys.argv[1] if len(sys.argv) > 1 else "./exported_data"

        if not output:
            raise ValueError("output 파라미터가 필요합니다.")

        # Click 함수를 직접 호출
        main(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            output=output,
        )

    except KeyError as e:
        print(sys.argv)
        print(e)
        exit(1)
