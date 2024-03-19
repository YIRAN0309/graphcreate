# dedupe.py - Find duplicate OEM files and optionally delete stale ones.
# Copyright (C) 2022 University of Texas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#这段代码是 dedupe.py 文件的头部注释，表示这是一个 Python 脚本，旨在查找重复的轨道星历消息（OEM）文件，
#并可选地删除过时的文件。该脚本由德克萨斯大学拥有版权，并在 GNU 通用公共许可证版本 3 或（根据用户选择）任何更高版本下发布。
#该程序的目的是提供实用性，但没有任何明示的保证，即不保证适销性也不保证特定目的的适用性。
#该程序的分发应包含 GNU 通用公共许可证的副本。如果没有，用户应访问 http://www.gnu.org/licenses/ 以获取许可证副本。
#简而言之，dedupe.py 是用于管理 OEM 文件的工具，帮助识别和处理重复项，确保数据的整洁和更新。








from glob import iglob
from os import getenv, path, remove
import sys

def dedupe(root_dir, recursive=True, delete_stale_files=True):
    try:
        id_map = {}
        cat_file = getenv("CASPY_OBJECT_CATALOG", path.expanduser(path.join("~", "object_catalog.csv")))
        with open(cat_file, "r") as fp:
            for line in fp.read().splitlines():
                tok = line.split(",")
                id_map[tok[1]] = tok[0]
    except Exception as exc:
        print(f"Warning: {exc}")

    fresh_files, stale_files = {}, []

    for fname in (f for f in iglob(path.join(root_dir, "**"), recursive=recursive) if (path.isfile(f) and f.endswith(".oem"))):
        oid, start = None, None
        with open(fname, "r") as fp:
            for line in fp.read().splitlines():
                tok = [t.strip() for t in line.split("=")]
                if (tok[0] == "OBJECT_ID"):
                    oid = id_map.get(tok[1], tok[1])
                if (tok[0] == "START_TIME"):
                    start = tok[1]
                if (oid and start):
                    if (oid in fresh_files):
                        prev = fresh_files[oid]
                        if (prev[1] < start):
                            stale_files.append(prev[0])
                            fresh_files[oid] = (fname, start)
                        else:
                            stale_files.append(fname)
                    else:
                        fresh_files[oid] = (fname, start)
                    break

    if (delete_stale_files):
        for fname in stale_files:
            remove(fname)

    return(fresh_files, stale_files)

if (__name__ == "__main__"):
    root_dir = sys.argv[1] if (len(sys.argv) > 1) else "."
    dedupe(root_dir, recursive=True, delete_stale_files=True)
