$(function() {

  // upload firmware test bin

  $('#file_upload').click(function(){
    
    $('#firmware').click();

    $('#firmware').change(function(){
       var name = $('#firmware').val();
      $('#firmware_name').val(name);
      if (name.endsWith('.bin')){
        $('#btn_start_test').attr("disabled", false); 
      }
      else {
        alert("The format of test file must be '.bin'!");
        $('#btn_start_test').attr("disabled",true);
      }
    });
     
  });


  // submit form data

  $('#btn_start_test').click(function(){
    $('#submit_form').click();
  });


  // check firmware test status
  function test_stage_match(status) {

    var 
      stage_list = {

        'offline': "offline",
        '0': "The ipcam you choose is free, you can start firmware test.",
        '1': "Stage 1/3:Fw_test upload file finished.",
        '2': "Stage 2/3:Update image finished.",
        '3': "Stage 3/3:Firmware test completed."
      },

      error_list = {

        '100': "BOARD_OFFLINE",
        '101': "UPDATE_IMAGE_ERROR",
        '105': "CP_IMAGE_ROOTFS_FW_ERROR",
        '106': "MAKE_PACK_ERROR",
        '107': "CP_LINUX_BIN_ERROR",
        '108': "TIMEOUT_REBOOT",
        '109': "PEXPECT_ERROR",
        '110': "SEND_FILE_TO_WEBSERVER",
        '111': "DOWNLOAD_FILE_FROM_WEBSERVER_ERR GET_STATUS_ERROR",
        '112': "GET_STATUS_ERROR"
    };

    if (stage_list.hasOwnProperty(status)) {
      stage = stage_list[status];
    } else {
      // error code
      stage = status;
    }

    return stage;
  };
  

function check_test_status(){

        $.get('firmware_test_status.json').done(
            function(info) {

                // change the info format from string to object
                var obj_info = eval("("+info+")");

                // get the status from the info
                var test_status_ov9715 = obj_info.ov9715[0];
                var test_status_ov9750 = obj_info.ov9750[0];

                // match the status with the stage
                var stage_9715 = test_stage_match(test_status_ov9715);
                var stage_9750 = test_stage_match(test_status_ov9750);

                // update the status
                $("#fw_test_board_ov9750").html(stage_9750);
                $("#fw_test_board_ov9715").html(stage_9715);

                if ((test_status_ov9715 == '0') || (test_status_ov9750 == '0')){
                    $('#file_upload').attr("disabled",false);
                    $('#btn_start_test').attr("value", "开始测试");
                }

                // update the testing gif according to the status
                if(test_status_ov9715 === '1' || test_status_ov9715 === '2' || 
                          test_status_ov9715 === '3'|| test_status_ov9715 === 'offline'){

                    $('#ov9715_testing').show();

                    if ($('#Sensor').val() == 'ov9715') {

                        $('#file_upload').attr("disabled",true);
                        $('#btn_start_test').attr("value", "正在测试");
                        $('#btn_start_test').attr("disabled",true);
                    }
                }
                else {
                    $('#ov9715_testing').hide();
                }


                if(test_status_ov9750 == '1' ||test_status_ov9750 == '2' || 
                          test_status_ov9750 == '3'|| test_status_ov9715 === 'offline'){

                    $('#ov9750_testing').show();

                    if ($('#Sensor').val() == 'ov9750') {

                        $('#file_upload').attr("disabled",true);
                        $('#btn_start_test').attr("value", "正在测试");
                        $('#btn_start_test').attr("disabled",true);
                    }
                }
                else {
                    $('#ov9750_testing').hide();
                }
            }
        )
    }
   

  setInterval(check_test_status, 1000*2);


  // check firmware log

  function check_firmware_log() {
      $.get('firmware_log_check.json').done(
        function(result) { 
          // the type of result:string

          if (result.indexOf('firmware')>=0) {
            var result_sub = result.indexOf('firmware')

            var start_tag = result.indexOf('firmware');
            var sub_start_tag = start_tag  + 14;
            var len_result = result.length -2
            var log_name = result.substring(start_tag, len_result);
            var sub_log_name = log_name.substring(14,len_result)
            var len_log_name = log_name.length;
            
            var log_status = document.getElementById("firmware_log");
            var newNode = document.createElement('a');   
            var log_folder = log_name.substring(14,22);
            var log_link = log_folder +'-'+ log_name;
            var now = new Date();

            var now_date = now.getFullYear()+now.getMonth()+now.getDate();
            
            if (log_status.hasChildNodes()) {
              log_status.removeChild(log_status.lastChild);
            }
            newNode.href = '/'+ log_folder +'#firmware_test';
            newNode.innerText = 'Click here for latest';
            log_status.appendChild(newNode);
          }
      });
    }

  setInterval(check_firmware_log, 1000*5);

  function appendSensor(sensor_type){
    $("#Sensor").append("<option value=sensor_type>"+sensor_type+"</option>");
  }

    $('#GetList').click(function(){
      $.get('firmware_board_list.json').done(
        function(board_list) {

          obj_board_list = eval("("+board_list+")");
          $("#Sensor").empty();
          for(key in obj_board_list){ 
              appendSensor(key);
          }
        });
    });

});



