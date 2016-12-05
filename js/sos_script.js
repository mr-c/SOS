$(document).ready(function(){

	var dir = "https://github.com/BoPeng/SOS/tree/onepage/doc/documentation_html/";
	var fileextension = ".html";
	$("#documentation > .container").append('<div class="row">')
	$.ajax({
	    //This will retrieve the contents of the folder if the folder is configured as 'browsable'
	    url: dir,
	    success: function (data) {
	        //List all .png file names in the page
	        $(data).find("a:contains(" + fileextension + ")").each(function () {
	
	        	var cons=this.href.split("/");
	        	var name=cons.slice(1).slice(-2);
	        	var path="./"+name[0]+"/"+name[1];
	            var oneString='<div class="col-md-4 col-sm-6 portfolio-item">'
        				+'<div class="portfolio-caption">';
        		oneString+="<a href="+path+">"+name[1].replace("html","")+"</a>";
        		oneString+='</div></div>';       	
        		 $("#documentation > .container").append(
			       	oneString
			     );
	  
	        });
	    }
	});
	$("#documentation > .container").append('</div>');

	var dir = "https://github.com/BoPeng/SOS/tree/gh-pages-doc/doc/tutorial_html/";
	var fileextension = ".html";
	$("#tutorial > .container").append('<div class="row">')
	$.ajax({
	    //This will retrieve the contents of the folder if the folder is configured as 'browsable'
	    url: dir,
	    success: function (data) {
	        //List all .png file names in the page
	        $(data).find("a:contains(" + fileextension + ")").each(function () {
	
	        	var cons=this.href.split("/");
	        	var name=cons.slice(1).slice(-2);
	        	var path="./"+name[0]+"/"+name[1];
	            var oneString='<div class="col-md-4 col-sm-6 portfolio-item">'
        				+'<div class="portfolio-caption">';
        		oneString+="<a href="+path+">"+name[1].replace("html","")+"</a>";
        		oneString+='</div></div>';       	
        		 $("#tutorial > .container").append(
			       	oneString
			     );
	  
	        });
	    }
	});
	$("#tutorial > .container").append('</div>');





	// var portfolioString='"<div class="row">';
	// var fileList= ["Auxilary_Steps","Command_Line_Options","Configuration_Files","Extending_SoS"];
 //    for (var i=0;i<fileList.length;i++){
 //    	var name=fileList[i];
 //        var oneString='<div class="col-md-4 col-sm-6 portfolio-item">'
 //        				+'<div class="portfolio-caption">';
 //        oneString+='<a href="./documentation_html/'+name+'.html" class="portfolio-link"><h4>'+name+'</h4></a>';
 //        oneString+='</div></div>';
 //        portfolioString+=oneString;
 //    }
 //    portfolioString+='</div>"';
 //    console.log(portfolioString);

 //    $("#portfolio > .container").append(
 //       	portfolioString
 //     );
	
});