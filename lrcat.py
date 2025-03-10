import sqlite3
from datetime import datetime, timedelta
from typing import List, Iterable
from uuid import uuid1

import pytz


class Image:
    def __init__(self, rawdata: tuple, catalog: 'LRCatalog') -> None:
        self.id = rawdata[0]
        self.file_format = rawdata[1]
        self.root_path = rawdata[2]
        self.path = rawdata[3]
        self.base_name = rawdata[4]
        self.extension = rawdata[5]
        self.catalog = catalog

    def get_file_path(self) -> str:
        return self.catalog.get_converted_root_path(self.root_path) + self.path + self.base_name + "." + self.extension

    def get_caption(self) -> str:
        cur = self.catalog.con.cursor()
        param = (self.id,)
        cur.execute("select caption from AgLibraryIPTC where image=?", param)
        result = cur.fetchone()
        return "" if result[0] is None else result[0]

    def set_caption(self, caption: str) -> None:
        cur = self.catalog.con.cursor()
        param = (caption, self.id)
        cur.execute("update AgLibraryIPTC set caption=? where image=?", param)
        cur.connection.commit()

    def get_keywords(self) -> List[str]:
        cur = self.catalog.con.cursor()
        param = (self.id,)
        cur.execute("""select name from AgLibraryKeywordImage
left join AgLibraryKeyword on AgLibraryKeywordImage.tag=AgLibraryKeyword.id_local
where image=?""", param)
        return [row[0] for row in cur]

    def has_keyword(self, keyword: str) -> bool:
        cur = self.catalog.con.cursor()
        param = (self.id, keyword)
        cur.execute("""select count(*) from AgLibraryKeywordImage
left join AgLibraryKeyword on AgLibraryKeywordImage.tag=AgLibraryKeyword.id_local
where image=? and name=?""", param)
        result = cur.fetchone()
        return result[0] != 0

    def set_keyword(self, keyword: str, is_person: bool = False) -> None:
        if self.has_keyword(keyword):
            return
        keyword_id = self.catalog.get_keyword_id(keyword)
        if keyword_id == -1:
            keyword_type = "person" if is_person else None
            keyword_id = self.catalog.create_new_keyword(keyword, keyword_type)
        param = (self.catalog.get_max_id() + 1, self.id, keyword_id)
        cur = self.catalog.con.cursor()
        cur.execute("insert into AgLibraryKeywordImage values (?,?,?)", param)
        timestamp = LRCatalog.convert_datetime_to_lrtimestamp()
        param = (timestamp, keyword_id)
        cur.execute("update AgLibraryKeyword set lastApplied=? where id_local=?", param)
        cur.connection.commit()

    def remove_keyword(self, keyword: str, remove_if_not_used: bool = False):
        cur = self.catalog.con.cursor()
        keyword_id = self.catalog.get_keyword_id(keyword)
        if keyword_id == -1:
            return
        if self.has_keyword(keyword):
            param = (self.id, keyword_id)
            cur.execute("delete from AgLibraryKeywordImage where image=? and tag=?", param)
            cur.connection.commit()
        if remove_if_not_used:
            param = (keyword_id,)
            cur.execute("select count(*) from AgLibraryKeywordImage where tag=?", param)
            result = cur.fetchone()
            if result[0] == 0:
                cur.execute("delete from AgLibraryKeyword where id_local=?", param)
                cur.connection.commit()

    def __str__(self):
        return f"Image:{self.base_name}"


class LRCatalog:
    def __init__(self, path: str, root_dictionary: dict = None) -> None:
        if root_dictionary is None:
            root_dictionary = {}
        self.path=path
        self.con = sqlite3.connect(path)
        self.root_dictionary = root_dictionary

    def get_max_id(self) -> int:
        max_id = 0
        cur = self.con.cursor()
        for table in cur.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'"):
            cur1 = self.con.cursor()
            cur1.execute("select count(*) from pragma_table_info(?) where name='id_local'", table)
            result = cur1.fetchone()
            if result[0] > 0:
                cur2 = self.con.cursor()
                cur2.execute(f"select max(id_local) from {table[0]}")
                result = cur2.fetchone()
                if result[0] is not None:
                    max_id = max(max_id, result[0])
        return max_id

    def get_image_by_id(self, image_id: int) -> Image:
        cur = self.con.cursor()
        param = (image_id,)
        cur.execute("""select Adobe_images.id_local,fileFormat,absolutePath,pathFromRoot,baseName,extension 
from Adobe_images
left join AgLibraryFile on Adobe_images.rootFile=AgLibraryFile.id_local 
left join AgLibraryFolder on AgLibraryFile.folder=AgLibraryFolder.id_local 
left join AgLibraryRootFolder on AgLibraryFolder.rootFolder=AgLibraryRootFolder.id_local
where Adobe_images.id_local=?""", param)
        result = cur.fetchone()
        if result is None:
            return Image((-1, "", "", "", "", ""), self)
        return Image(result, self)

    def get_all_image(self) -> Iterable[Image]:
        cur = self.con.cursor()
        for row in cur.execute("""select Adobe_images.id_local,fileFormat,absolutePath,pathFromRoot,baseName,extension 
from Adobe_images
left join AgLibraryFile on Adobe_images.rootFile=AgLibraryFile.id_local
left join AgLibraryFolder on AgLibraryFile.folder=AgLibraryFolder.id_local
left join AgLibraryRootFolder on AgLibraryFolder.rootFolder=AgLibraryRootFolder.id_local"""):
            yield Image(row, self)

    def get_keyword_id(self, keyword: str) -> int:
        cur = self.con.cursor()
        param = (keyword.lower(),)
        cur.execute("select id_local from AgLibraryKeyword where lc_name=?", param)
        result = cur.fetchone()
        return -1 if result is None else result[0]

    def create_new_keyword(self, keyword: str, keyword_type: str = None, exportable: int = 1) -> int:
        cur = self.con.cursor()
        cur.execute("select id_local from AgLibraryKeyword where parent is null")
        parent_id = cur.fetchone()[0]
        keyword_id = self.get_max_id() + 1
        uuid = str(uuid1())
        timestamp = LRCatalog.convert_datetime_to_lrtimestamp()
        genealogy = self.create_genealogy(parent_id, keyword_id)
        param = (
            keyword_id, uuid, timestamp, genealogy, None, exportable, exportable, exportable, keyword_type, None,
            keyword.lower(), keyword,
            parent_id)
        cur.execute("insert into AgLibraryKeyword values (?,?,?,?,?,?,?,?,?,?,?,?,?)", param)
        self.con.commit()
        return keyword_id

    def get_keywords(self) -> List[str]:
        cur = self.con.cursor()
        cur.execute("select name from AgLibraryKeyword where name!=''")
        return [row[0] for row in cur]

    def get_converted_root_path(self, root_path: str) -> str:
        if root_path in self.root_dictionary:
            return self.root_dictionary[root_path]
        return root_path

    @staticmethod
    def convert_lrtimestamp_to_str(timestamp: float) -> str:
        utc = pytz.utc.localize(datetime(2001, 1, 1, 0, 0, 0) + timedelta(seconds=timestamp))
        return utc.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def convert_datetime_to_lrtimestamp(dt: datetime = datetime.now()) -> float:
        return (dt - datetime(2001, 1, 1, 0, 0, 0)).total_seconds()

    @staticmethod
    def create_genealogy(parent_id: int, keyword_id: int) -> str:
        return f'/{len(str(parent_id))}{parent_id}/{len(str(keyword_id))}{keyword_id}'

    def __repr__(self):
        return f"LRCatalog({self.path})"



