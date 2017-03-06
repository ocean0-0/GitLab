// Global
$(function() {
	
	// hightlight current page
	$("#menu a").each(function(){

	if ($(this)[0].href === String(window.location)) {
			$(this).parent().addClass("active");
		}else {
			$(this).parent().removeClass("active");
		}
	});


	// stick to top
	$(window).scroll(function() {
		
		if ($(this).scrollTop()> 0) {
			$("#toTop").fadeIn();
		} else {
			$("#toTop").fadeOut();
		}
	});

	$("#toTop").click(function(){
		$("html,body").animate({scrollTop:0},"slow");
		return false;
	});


	// hightlight keyword
	function createExp(arry){

		var str="";

		for(var i=0;i<arry.length;i++){

			if(i!=arry.length-1){			
				str=str+arry[i]+"|";
			}else{
				str=str+arry[i];
			}
		}
		return "("+str+")";
	}

	function highlightKey(id, key){

		var arr=null;
		var regStr=null;
		var content=null;
		var Reg=null;
		var newContent=null;

		arr=key.split(/\s+/);
		regStr=createExp(arr);
		content=$("#"+id+"").innerHTML;
		Reg=new RegExp(regStr,"g");

		return newContent =content.replace(Reg,"<span class=keyword>"+key+"</span>");

	}

	function searchWords(id){

		var thediv=document.getElementById(id);
		var words= new Array("fail","failed","ERROR");
		var itemContent = $("#"+id+"").innerText;

		for (var i=0; i<words.length; i++){

			if (itemContent.indexOf(words[i])>-1){
				$("#"+id+"").innerHTML=highlightKey(id,words[i]);
			}
		}
	}

	// content show and fold
	function showAndFold(id) {

		var text = $("#"+id+"").innerHTML;
		var newBox = document.createElement("div");
		var btn = document.createElement("a");

		if(text){
			newBox.innerHTML = text.substring(0,1);
			btn.innerHTML = text.length > 1 ? "show" : " ";
			btn.href = "###";
			btn.onclick = function() {
				if (btn.innerHTML == "show") {
					btn.innerHTML = "fold";
					newBox.innerHTML = text;
				} else {			
					btn.innerHTML = "show";
					newBox.innerHTML = text.substring(0,1);
					}
				}
			}

		$("#"+id+"").innerHTML = "";
		$("#"+id+"").append(newBox,btn);

	}

	showAndFold("pressure_record");
});