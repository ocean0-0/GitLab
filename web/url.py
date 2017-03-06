#!/usr/bin/env python
#-*- coding: utf-8 -*-

urls = (
    '/', 'index.Index',
    '/(\d+)', 'folder.Folder',
    '/(\d+)-(.*)', 'file.ShowFileContent',
    '/firmware', 'firmware.Firmware',
    '/about', 'about.About',
    '/more', 'more.More',
    '/fail_compile.json', 'fail_compile.FailCompile',
    '/fail_data.json', 'fail_data.FailData',
    '/fail_ratio.json', 'fail_ratio.FailRatio',
    '/total_test.json', 'total_test.TotalTest',
    '/firmware_test_status.json', 'firmware.FirmwareTestStatus',
    '/firmware_log_check.json', 'firmware.FirmwareLogCheck',
    '/firmware_board_list.json','firmware.FirmwareBoardList',
)
