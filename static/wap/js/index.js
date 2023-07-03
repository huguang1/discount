
$(document).ready(function(){
    $("#djcxbutton").click(function(){
			var uname = $("#query_user").val();
			if(uname == ""){
				alert("会员帐号不能为空!");
				return false;
			}
			queryPage(1);		
	});

	//lotterylist();
  
  //	$.get('api.php?action=advice',function(data){
	//	$("#div_notice").html('<marquee scrollamount="8" scrolldelay="150" direction="left" id="msgNews" onmouseover="this.stop();" onmouseout="this.start();" style="cursor:pointer;">'+data+'</marquee>'); 		

        //jQuery(".txtMarquee-left").slide({ mainCell: ".bd ul", autoPlay: true, effect: "leftMarquee", vis: 1, interTime: 50 });
	//});
  
})
/*
function lotterylist() {
	$.ajax({
		url: 'api.php?action=list',
		dataType: 'json',
		cache: false,
		type: 'GET',
		success: function(obj) {
			var sAwardEle = "";
			$.each(obj, function(i, award) {				
              	sAwardEle += "<li>恭喜 <span>"+award.user_name+"</span> 成功办理 <span>" +award.active_name+ "</span></li>";
            });
			$(".wpgg").html('<ul>'+sAwardEle+'</ul>');
		   	//向上滚动
           $(".wpgg").myScroll({
              speed:100, //数值越大，速度越慢
              rowHeight:30 //li的高度
          });


		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			var x = 1
		}
	})
}*/

var pagesize = 1000;
function queryPage(page) {
	$.ajax({
		url: 'mine',
		dataType: 'json',
		cache: false,
		data: {
			user_name: $("#query_user").val(),
			act_name: $("#query_kinder").val(),
			csrfmiddlewaretoken:$('[name="csrfmiddlewaretoken"]').val()
		},
		type: 'POST',
		success: function(obj) {
			if(obj.count == "-1"){
				
				alert('验证码错误!');
				return;
			}
			
			$('#query_div').hide();
      		$('#query_result').show();
			
			if (obj.count != "0") {
				var sHtml1 = "";
             
				$.each(obj.data, function(i, award) {
                  	var temp = '等待审核';
					if (award.state == "1") {
						temp = '<font color=green>已通过</font>'
					}
					if (award.state == "2") {
						temp = '<font color=red>已拒绝</font>'
					}                  	

					sHtml1 += '<p> 会员账号:'+award.T_ProductName+'</p><p>申请时间：'+award.T_DateTime+'</p><p>申请状态：'+award.T_ProductNote+'</p><p>管理员留言：'+award.Remark+'</p><hr/>';
				}) 
				
      			$("#result_html").html(sHtml1);
			} else {
				$("#result_html").html("<p>未查询到信息</p>");
			}
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			var x = 1
		}
	})
}
function Paging(pageNum, pageSize, totalCount, skipCount, fuctionName, currentStyleName, currentUseLink, preText, nextText, firstText, lastText) {
	var returnValue = "";
	var begin = 1;
	var end = 1;
	var totalpage = Math.floor(totalCount / pageSize);
	if (totalCount % pageSize > 0) {
		totalpage++
	}
	if (preText == null) {
		firstText = "prev"
	}
	if (nextText == null) {
		nextText = "next"
	}
	begin = pageNum - skipCount;
	end = pageNum + skipCount;
	if (begin <= 0) {
		end = end - begin + 1;
		begin = 1
	}
	if (end > totalpage) {
		end = totalpage
	}
	for (count = begin; count <= end; count++) {
		if (currentUseLink) {
			if (count == pageNum) {
				returnValue += "<a class=\"" + currentStyleName + "\" href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ");\">" + count.toString() + "</a> "
			} else {
				returnValue += "<a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ");\">" + count.toString() + "</a> "
			}
		} else {
			if (count == pageNum) {
				returnValue += "<a class=\"" + currentStyleName + "\">" + count.toString() + "</a> "
			} else {
				returnValue += "<a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ");\">" + count.toString() + "</a> "
			}
		}
	}
	if (pageNum - skipCount > 1) {
		returnValue = " ... " + returnValue
	}
	if (pageNum + skipCount < totalpage) {
		returnValue = returnValue + " ... "
	}
	if (pageNum > 1) {
		returnValue = "<a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + (pageNum - 1).toString() + ");\"> " + preText + "</a> " + returnValue
	}
	if (pageNum < totalpage) {
		returnValue = returnValue + " <a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + (pageNum + 1).toString() + ");\">" + nextText + "</a>"
	}
	if (firstText != null) {
		if (pageNum > 1) {
			returnValue = "<a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(1);\">" + firstText + "</a> " + returnValue
		}
	}
	if (lastText != null) {
		if (pageNum < totalpage) {
			returnValue = returnValue + " " + " <a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + totalpage.toString() + ");\">" + lastText + "</a>"
		}
	}
	return returnValue
}


