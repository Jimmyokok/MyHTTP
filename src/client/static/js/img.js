
$(document).ready(function(){
    var filechanged = 0;
    $(".file").on("change",function(e){
        filechanged = 1;
        var filename = $(this).get(0).files[0];
        var filetype = /jpeg|png|gif|bmp/ig;
        var ext = filename.type.split("/")[1];
        var name=e.currentTarget.files[0].name;
        if(filetype.test(ext)){
            $(".uploadimg").attr("src","");
            var fileread = new FileReader();
            fileread.readAsDataURL(filename);
            fileread.onload=function(){
                console.log(this.result);
                $(".path").text(name);
                $(".content").val(this.result);
                $(".uploadimg").attr("src",this.result);
            }
        }
        else{
            alert("图片格式不正确，请重新上传！");
        }
    });
    $(".button").on("click",function(e){
        var id = $(".id").val();
        var name = $(".name").val();
        var path = $(".path").text();
        if(id == ''){
            alert("You haven't enter student id!");
            return;
        }
        else if(name == ''){
            alert("You haven't enter student name!");
            return;
        }
        else if(path == "No image here"){
            alert("You haven't upload student photo!");
            return;
        }
        else $(".wrapper").submit();
    });
});