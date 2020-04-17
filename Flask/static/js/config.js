var pins=new Array(5);
var inits=new Array(5);
var drivers=new Array(5);
var tables=new Array(3);
function parse_bustype(result)
{
 //  alert('parse: '+result);
   var obj = JSON.parse(result);
   if(obj.peripheral != "NONE")
   {
       options = obj.peripheral;
       for(var i=0; i<options.length; i++)
           $("#peripheral").append("<option value='1'>"+options[i]+"</option>");  
   }

   if(obj.io_type != "NONE")
   {
       options = obj.io_type;
       for(var i=0; i<options.length; i++)
           $("#io_type").append("<option value='1'>"+options[i]+"</option>");  
   }

//   $(".pin_bus").show();
   $(".pins #one").hide();
   $(".pins #two").hide();
   $(".pins #three").hide();
   $(".pins #four").hide();
   $(".pins #five").hide();
   pins.splice(0,pins.length);
   inits.splice(0,inits.length);
   drivers.splice(0,drivers.length);
   tables.splice(0,tables.length);

   $(".initialize #init_1").hide();
   $(".initialize #init_2").hide();
   $(".initialize #init_3").hide();
   $(".initialize #init_4").hide();
   $(".chip_set").hide();

   if(obj.one != "NONE")
   {
      $(".pins #one").show();
      $(".pins #one").attr({
              "placeholder":obj.one,
              "type":"number"});
      pins.push("one");
   }
   if(obj.two != "NONE")
   {
      $(".pins #two").show();
      $(".pins #two").attr({
              "placeholder":obj.two,
              "type":"number"});
      pins.push("two");
   }
   if(obj.three != "NONE")
   {
      $(".pins #three").show();
      $(".pins #three").attr({
              "placeholder":obj.three,
              "type":"number"});
      pins.push("three");
   }
   if(obj.four != "NONE")
   {
      $(".pins #four").show();
      $(".pins #four").attr({
              "placeholder":obj.four,
              "type":"number"});
      pins.push("four");
   }
   if(obj.five != "NONE")
   {
      $(".pins #five").show();
      $(".pins #five").attr({
              "placeholder":obj.five,
              "type":"number"});
      pins.push("five");
   }


   if(obj.init_tb1 != "NONE")
   {
       tables.push(obj.init_tb1);
   }
   if(obj.init_tb2 != "NONE")
   {
       tables.push(obj.init_tb2);
   }

   if(obj.init_1 != "NONE")
   {
      $(".initialize #init_1").show();
       driver_set = obj.init_1;
       // alert(driver_set);
       $("#init_1 option").remove();
       for(var i=0; i<driver_set.length; i++)
           $("#init_1").append("<option value='1'>"+driver_set[i]+"</option>");  
      inits.push("init_1");
   }

   if(obj.init_2 != "NONE")
   {
       $(".initialize #init_2").show();
       driver_set = obj.init_2;
       // alert(driver_set);
       $("#init_2 option").remove();
       for(var i=0; i<driver_set.length; i++)
           $("#init_2").append("<option value='1'>"+driver_set[i]+"</option>");  
      inits.push("init_2");
   }

   if(obj.init_3 != "NONE")
   {
      $(".initialize #init_3").show();
      $(".initialize #init_3").attr({
              "placeholder":obj.init_3,
              "type":"number"});
      inits.push("init_3");
   }

   if(obj.init_4 != "NONE")
   {
      $(".initialize #init_4").show();
      $(".initialize #init_4").attr({
              "placeholder":obj.init_4,
              "type":"number"});
      inits.push("init_4");
   }

   if(obj.init_5 != "NONE")
   {
       $(".chip_set").show();
       driver_set = obj.init_5;
       // alert(driver_set);
       $("#driver_set option").remove();
       for(var i=0; i<driver_set.length; i++)
           $("#driver_set").append("<option value='1'>"+driver_set[i]+"</option>");  
       drivers.push("driver_set");
   }
}

function checkForm()
{
    //check if it is integrality
    peripheral=$("#peripheral option:selected");
    io_type=$("#io_type option:selected");
    str=', "'+peripheral.text() +'","' + io_type.text() + '","' ;
    //check if it is already stored in databbase
    len = pins.length;
    for(var i=0; i<len; i++)
    {
       if (document.getElementById(pins.slice(i,i+1)).value == '')
       {
          alert("PIN ( " + $(".pins #"+ pins.slice(i,i+1)).attr("placeholder") + " ) 不能为空");
          return "";
       }
       else
       {
           if (len == 1)
              str += 'PIN:' + document.getElementById(pins.slice(i,i+1)).value ;
           else
           {
              if(i > 0)
                 str +=',';
              str += $(".pins #"+  pins.slice(i,i+1)).attr("placeholder") + ':' + document.getElementById(pins.slice(i,i+1)).value;
           }
       }
    }
    str += '", "';
    //check initialize 
    len = inits.length;
    for(var i=0; i<len; i++)
    {
        if(inits.slice(i,i+1) == "init_1")
        {
            str += tables.slice(0,1)+ ':';
            str +=  $("#init_1 option:selected").text();
        }
        if(inits.slice(i,i+1) == "init_2") 
        {
            str += tables.slice(1,2)+ ':';
            str +=  $("#init_2 option:selected").text();
        }
        if((inits.slice(i,i+1) == "init_3") || (inits.slice(i,i+1)=="init_4"))
        {
            if (document.getElementById(inits.slice(i,i+1)).value == '')
               continue;
            str += $("#"+  inits.slice(i,i+1)).attr("placeholder") + '_VALUE:' + document.getElementById(inits.slice(i,i+1)).value;
        }
        if((i+1) < len)
            str +=',';
    }
    str +='"';
    //check driver
    if(drivers.length)
    {
       str += ', "' + $("#"+drivers.pop() +" option:selected").text() + '"';
    }
    else
       str += ',"NONE"';     
    alert(str);
    return str;
}

function init()
{
    $(".proccess").hide();
    $(".downloadfile").hide();
    $.ajax({
            url:"/ajax_iotype",
            data:{
                   "io_type": "NONE",
                   "state": "init",
            },
            success:function(result){
                    parse_bustype(result);
            }
    });
}

function query_status(compile){

        $.ajax({
            url:"/ajax_query",
            data:{
                   "query": compile,
                   "timestamp": "",
            },
            success:function(result){
                   //alert(result);
                   return result;
                   // $(".downloadfile").show();
            }});

}

function proccess(n){
    var prog=document.getElementById('proccessing');
    prog.firstChild.nodeValue=n+"%";
    prog.style.width=(n*5)+"px";
    n+=1;
    if((n%10==0) && (query_status("compile")=="ok"))
    {
          clearTimeout( progT);
          $(".downloadfile").show();
          return;
    }    
    if(n>100){
          n=100;
          clearTimeout( progT);
          $(".downloadfile").show();   
          return;
    }
    progT = setTimeout('proccess('+n+')',200);
}


$(document).ready(function(){
     $("p").click(function(){
         $(this).hide();
     });

     init();

     $("#cfg_bin").click(function(){
        proccess(1);
        $(".proccess").show();

        $.ajax({
            url:"/ajax_genbin",
            data:{
                   "state": "generate bin",
                   "table_name": "lumi_demofile",
            },
            success:function(result){
                    //$("#div1").html(result);
                  //  proccess(1);
                  //  alert(result);
                   // $(".proccess").show();
                   // $(".downloadfile").show();
            }});
     });
     
     $("#add").click(function(){
        data = checkForm();
        if(data=="")
          return;    
        $.ajax({
            url:"/ajax_add",
            data:{
                   "operate": "ADD",
                   "data": data,
            },
            success:function(result){
                    //proccess(1);
                    alert(result);
                    // $(".proccess").show();
            }});
     });

     $("#io_type").change(function(){
         $(this).css("background-color","#D6D6FF");
         var options=$("#io_type option:selected");
         //alert(options.val());//获取value
         // alert(options.text());//获取文本
         $.ajax({
                url:"/ajax_iotype",
                data:{
                   "io_type": options.text(),
                   "state": "select",
                },
                success:function(result){
                    parse_bustype(result);
                }
         });
//  $("body div:first").addClass("important blue");
     });
/*
     $("#chk_ex").change(function(){
          if($('#chk_ex').is(':checked'))
          {
             $(".ex_init").show();
             $("#ex_1").append("<option value='1'>Text</option>");  
          
             $.ajax({
                 url:"/ajax_exinit",
                 data:{
                     "bus_type": $("#iotype").val(),
                     "member": 4,
                 },
                 success:function(result){
                       parse_exinit(result);
                 }
              });
          }
          else
          {
             $(".ex_init").hide();
             //alert("no")
          }
     });
*/
//     var ret=$("#chk_ex").find("input:checkbox:checked").val();
});

