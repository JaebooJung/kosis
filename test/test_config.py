# -*- coding: utf-8 -*-

import os.path

from kosis import get_apikey, set_apikey
from kosis.config import get_config_filepath


def test_get_config_filepath():
    config_filepath = get_config_filepath()
    assert os.path.exists(config_filepath)
    backup_apikey = get_apikey()
    new_apikey = "new apikey"
    set_apikey(new_apikey)
    assert new_apikey == get_apikey()
    set_apikey(backup_apikey)
    assert backup_apikey == get_apikey()
