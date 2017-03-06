
var timer = null;  
var width = 0;     

/* click hide file browse */
function file_browse() 
{
  document.getElementById('firmware').click();
  
  document.getElementById('start_test').disabled = false;

}


/* update firmware name */
function updateFirmwareName()
{
  var f = document.getElementById('firmware');
  var filename = f.value

  if (!filename.endsWith('.bin'))
  {
    alert('The format of test file must be .bin.');
  }
  else
  {
    document.getElementById('firmware_name').value = filename;

  }


 
}


/* check form data validity*/
function checkFormData() 
{

}  

/*  submit form */
function submit_form()
{

  document.getElementById('upload_info').click();

}

/* control progress bar */ 
function update_process_bar() 
{  

  if(width == 600) 
  {  
    window.clearTimeout(timer);  
  }

  else 
  {  
    width += 1;  
    document.getElementById("fw_bar").style.width = width + "px";  
    timer = window.setTimeout("update_process_bar()", 100*5);  
  }  
} 


   

