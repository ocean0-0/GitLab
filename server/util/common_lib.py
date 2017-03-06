# !/usr/bin/env python
# --*-- coding:utf-8 --*--
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2016.09.27

import util

def get_routine_test_ip_list(config_name, proj_name):
    re = util.get_dict_from_config(config_name, proj_name)
    if re.has_key('ip'):
        return re['ip']
    return -1

def get_cmd_list(config_name, proj_name, test_name):
    re = util.get_dict_from_config(config_name, proj_name)
    for key in re.keys():
        if key == test_name:
            return re[key]
    return -1

def get_download_file_info(config_name, proj_name):
    re = util.get_dict_from_config(config_name, proj_name)
    return re

def get_start_test_time(config_name, proj_name):
    re = util.get_dict_from_config(config_name, proj_name)
    return int(re['start_hour']),int(re['start_minute'])

def get_update_kernel_time(config_name, proj_name):
    re = util.get_dict_from_config(config_name, proj_name)
    return int(re['start_hour']),int(re['start_minute'])

if __name__ == '__main__':
    print get_update_kernel_time('../config_server.ini', 'update_kernel')
