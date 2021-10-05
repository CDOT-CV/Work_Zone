import datetime
from typing import Any, Callable, Dict, Union
from collections import OrderedDict


class BrokenPath(KeyError):
    pass


class PathDict(object):
    def __init__(self, d: Union[Dict, OrderedDict], split_path_on: str = "/"):
        super().__init__()
        self.d = d
        self.split_path_on = split_path_on

    def __getitem__(self, path: str) -> Any:
        parts = path.split(self.split_path_on)
        target = self.d
        path_parts_tried: str = []
        for part in parts:
            path_parts_tried.append(part)
            try:
                target = target[part]
            except (TypeError, KeyError):
                failed_path = self.split_path_on.join(path_parts_tried)
                raise BrokenPath(f"Failed key lookup at {failed_path}")
        return target

    def get(self, path: str, trans: Callable = None, default: Any = None) -> Any:
        try:
            target = self[path]
            # Conversions like this should be handled through the trans param
            # if date_val:
            #     return int(datetime.datetime.fromisoformat(target).timestamp())
            if trans:
                '''The transformer has the duty to handle exceptions'''
                # try:
                #     return trans(target)
                # except:
                #     return default
                return trans(target)
            return target
        except BrokenPath as e:
            return default
