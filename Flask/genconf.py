import pymysql
import paho.mqtt.client as mqtt
import sys
import os
import json
import time
from git import Repo
'''
src=((1, 'LED', 'OUTPUT', 'PIN:12', 'pullres:PULL_UP, outlevel:LEVEL_H', 'NONE'),
     (2, 'TEMPERATURE', 'I2C', 'IIC_CLK:7,IIC_DAT:6', 'pullres:PULL_UP,ADDR_VALUE:34', 'I2C_SHTX'),
     (3, 'RELAY', 'OUTPUT', 'PIN:3', 'pullres:PULL_UP,outlevel:LEVEL_L', 'NONE'),
     (4, 'BUTTON', 'INPUT', 'PIN:4', 'pullres:PULL_UP', 'NONE'))

const tsBAL_ConfigMap	asBAL_ConfigIO[] = {
		{E_BAL_HWID_IO_OUTPUT, 				CFG_ID_PIN_LED_BLUE, 			MAKE_BAL_OUTPUT_INIT(BAL_MODE_PULL_UP, BAL_LEVEL_HI)},
//		{E_BAL_HWID_IO_OUTPUT, 				CFG_ID_PIN_LED_RED,				MAKE_BAL_OUTPUT_INIT(BAL_MODE_PULL_UP, BAL_LEVEL_HI)},	
		{E_BAL_HWID_IO_OUTPUT, 				CFG_ID_PIN_SHT3X_I2C0_PWR,		MAKE_BAL_OUTPUT_INIT(BAL_MODE_PULL_UP, BAL_LEVEL_HI)},	
		
		{E_BAL_HWID_IO_INPUT,				CFG_ID_PIN_BUTTON_LEARN, 		MAKE_BAL_INPUT_INIT(BAL_MODE_PULL_UP)},
		{E_BAL_HWID_IO_INPUT,				CFG_ID_PIN_TEST_ENTER, 			MAKE_BAL_INPUT_INIT(BAL_MODE_PULL_UP)},	
		{E_BAL_HWID_IIC_DATA,				CFG_ID_PIN_SHT3X_I2C0_DAT,		MAKE_BAL_IIC_INIT(1, 0, CFG_ID_PIN_SHT3X_I2C0_ADDR)},
		{E_BAL_HWID_IIC_CLK,				CFG_ID_PIN_SHT3X_I2C0_CLK,		MAKE_BAL_IIC_INIT(1, 0, CFG_ID_PIN_SHT3X_I2C0_ADDR)},

		{E_BAL_HWID_IO_OUTPUT,				CFG_ID_PIN_FBM320_SPI1_PWR, 	MAKE_BAL_OUTPUT_INIT(BAL_MODE_PULL_UP, BAL_LEVEL_HI)},	
		{E_BAL_HWID_SPI_SCK,				CFG_ID_PIN_FBM320_SPI1_CLK, 	MAKE_BAL_SPI_MODE_INIT(BAL_SPI_MODE_RAISING_FIRST, BAL_SPI_MSB_FIRST)},
		{E_BAL_HWID_SPI_MISO,				CFG_ID_PIN_FBM320_SPI1_MISO,	BAL_CONFIG_INIT_IGNOR},
		{E_BAL_HWID_SPI_MOSI,				CFG_ID_PIN_FBM320_SPI1_MOSI,	BAL_CONFIG_INIT_IGNOR},
		{E_BAL_HWID_SPI_CS, 				CFG_ID_PIN_FBM320_SPI1_CS,		BAL_CONFIG_INIT_IGNOR},

//		{E_BAL_HWID_ADC_INPUT,				CFG_ID_PIN_INTERNAL_V_MONITOR,	BAL_CONFIG_INIT_IGNOR},
};
'''
def convert_h(src=()):
    print("start convert H")
    if len(src)==0:
        print("no avild param in conert_h function -->")
        return "",""
    pins_config={}
    pins_cfg="\n//following is configed automatically don't edit  -->HEAD\n"
    btn_mask=""
    for item in src:
        print(item)
        if item[5] != "NONE":
         #   print("----------------------> BUS")
            pins= item[3].split(",")
            for pin in pins:
                pt= pin.find(":")
                def_pin="CFG_ID_PIN_%s_%s"%(item[5], pin[:pt])
                cfg_pin="#define %s\t%s"%(def_pin, pin[(pt+1):])
                pins_cfg += cfg_pin + '\n'
                pins_config.update({pin[(pt+1):]:def_pin})
        else:
         #   print("----------------------> I/O")
            pt= item[3].find(":")+1
            def_pin = "CFG_ID_PIN_%s"%(item[1])
            cfg_pin = "#define %s\t%s"%(def_pin ,item[3][pt:])
            pins_cfg += cfg_pin + '\n'
            pins_config.update({item[3][pt:]:def_pin})
         # button mask & wakeup mask
        if item[1] == "BUTTON":
            if btn_mask == "":
                btn_mask = "(1 << %s)"%(def_pin)
            else:
                btn_mask += "|(1 << %s)"%(def_pin)
    btns_mask="#define CFG_BUTTONS_MASK \t (%s)"% btn_mask
    wakes_mask="#define CFG_WAKEUPS_DIO_MASK \t (CFG_BUTTONS_MASK)"

    ints_pins_mask = "#define CFG_GINT0_PIN_DIO_MASK \t CFG_BUTTONS_MASK"
    ints_enable_mask = "#define CFG_GINT0_ENA_MASK \t CFG_GINT0_PIN_DIO_MASK"
    ints_opl_mask = "#define CFG_GINT0_POL_MASK \t 0"

    rcc_mask = "#define HW_SPECIAL_CONFIG_RCC \t (BAL_CONFIG_EXT_XTAL | BAL_CONFIG_RCC_WWDT) "
    pins_cfg +="\n\n%s\n%s\n\n%s\n%s\n%s\n\n%s"%( btns_mask ,wakes_mask ,ints_pins_mask ,ints_enable_mask, ints_opl_mask, rcc_mask )
#    print(pins_cfg)
#    print(pins_config)
    return pins_config, pins_cfg


def parse_inits(values=""):
    inits= values.split(",")
    result=""
    for init in inits:
#        print(init)
        pt= init.find(":")
        key=init[:pt]
        value=init[(pt+1):]
#        print(key)
#        print(value)
        pt= key.find("_VALUE")
#        print(pt)
        if len(result) > 0:   
            result += ','
        if pt > 0:#edit
            # print("found edit !!!")
            result +=value
        else:  #select
            sql=r'SELECT * FROM %s WHERE name="%s"'%(key,value)
#            print(sql)
            ret=req_sql(origin=sql)
           # print(ret[0][2])
            result +=ret[0][2]
#    print(result)
    return result


def bal_pack(filter="", inits="", pin_map=""):
    inits=parse_inits(inits)
    sql=r'SELECT * FROM bal_layer WHERE ios_type="%s"'%filter
    ret=req_sql(origin=sql)
    if ret[0][3] == "NONE":
       init_value="BAL_CONFIG_INIT_IGNOR"
    else:
       init_value="%s(%s)"%(ret[0][3], inits)
    return '\t{%s,\t%s,\t%s},\n'%(ret[0][1], pin_map, init_value)


def dal_bus_pack(filter="", inits="", pins=[]):
    sql=r'SELECT * FROM busdriver WHERE name LIKE "%'+'%s'%filter +'%"'
    ret=req_sql(origin=sql)
 #   print(ret)
    make_param=""
    head=ret[0][5].replace("%", "0")#"E_BAL_I2C_CH%, CFG_ID_BUS_IGNOR_ADDR"
#    print(pins)
    params=ret[0][6].split(",")
    for item in params:
        for pin in pins:
    #        print(pin)
     #       print(item)
            if pin.find(item) > 0:
                if len(make_param) > 0:
                    make_param += ','
                make_param += pin
                break
    dal_def="#define %s\t (MAKE_DAL_BUS_HEADER(%s) | %s(%s)) "%(ret[0][3], head, ret[0][4], make_param)
#    print(dal_def)
    return dal_def, ret[0][3]


def aal_bus_pack(bus_name="", peripheral="", pins={}):
    sql=r'SELECT * FROM busdriver WHERE name LIKE "%'+'%s'%bus_name +'%"'
    ret=req_sql(origin=sql)
 #   print(ret)
    dal_pin=pins[ret[0][3]]
    sql=r'SELECT * FROM aal_layer WHERE peripheral="%s" AND io_type="BUS"'%(peripheral)
    ret=req_sql(origin=sql)
#    print(ret)
    aal_bus='\t{%s,\t %s,\t%s,\t"%s"},\n'%(ret[0][1], "0|0", dal_pin, peripheral)
    return aal_bus;


def convert_c(src=()):
    print("start convert C")
    ret_all={}
    if len(src)==0:
        print("Please input the parameter")
        return ret_all
    filter=""
    index=""
    dal_pin_map={}
    bal_pin_map, def_pins_head=convert_h(src)
#    print(bal_pin_map)
    bal_cfg="\n//following is configed automatically don't edit  -->BAL\n"
    dal_def=""
    dal_cfg="\n//following is configed automatically don't edit  -->DAL\n"
    aal_cfg="\n//following is configed automatically don't edit  -->AAL\n"
    for item in src:
#        print(item)
        if item[5] != "NONE":
         #   print("----------------------> BUS")
            bus_pin=[]
            pins= item[3].split(",")
            for pin in pins:
                pt=pin.find(':')
                index=pin[pt+1:]
                str=pin[:pt]
                pt=str.find('_')
                filter=item[2]+str[pt:]
                bal_cfg += bal_pack(filter=filter, inits=item[4], pin_map=bal_pin_map[index])
                bus_pin.append(bal_pin_map[index])
           # dal handle    
            dal_def, dalpin=dal_bus_pack(filter=item[5], inits="", pins=bus_pin)
            driver='&STR_BUS_%s'%(item[5])
            sql=r'SELECT * FROM dal_layer WHERE io_type LIKE "%'+'%s'%item[2] +'%"'
            ret=req_sql(origin=sql)
            dal_id=r'%s(%s+%d)'%(ret[0][1],ret[0][4], 0) #MAKE_DAL_HWID_BUS_INDEX(E_DAL_BUS_ID_I2C + 0)
            # {MAKE_DAL_HWID_BUS_INDEX(E_DAL_BUS_ID_I2C + 0),  CFG_ID_PIN_BUS_I2C_SHT3X,  DAL_CONFIG_INIT_IGNOR, &STR_BUS_I2C_SHTX},
            dal_cfg += '\t{%s,\t %s,\t%s,\t%s},\n'%( dal_id, dalpin,ret[0][2], driver)
            dal_pin_map.update({dalpin:dal_id})
           #aal handle
            aal_cfg +=aal_bus_pack(bus_name=item[5], peripheral=item[1], pins=dal_pin_map)
            
        else:
         #   print("----------------------> IO")
            pt= item[3].find(":")+1        
            index=item[3][pt:]
            bal_cfg += bal_pack(filter=item[2], inits=item[4], pin_map=bal_pin_map[index])
        
           # dal handle    
            sql=r'SELECT * FROM dal_layer WHERE io_type LIKE "%'+'%s'%item[2] +'%"'
            ret=req_sql(origin=sql)
            dal_id=r'%s(%s)'%(ret[0][1], bal_pin_map[index])
            #{MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_LED), CFG_ID_PIN_LED,  MAKE_DAL_BO_INIT_ACTIVE(FALSE), NONE},
            dal_cfg += '\t{%s,\t %s,\t%s(FALSE),\t%s},\n'%(dal_id, bal_pin_map[index],ret[0][2], "NONE")
            dal_pin_map.update({bal_pin_map[index]:dal_id})
           # aal handle    
            sql=r'SELECT * FROM aal_layer WHERE io_type="%s" AND peripheral="%s"'%(item[2],item[1])
            ret=req_sql(origin=sql)
   #         print(ret)
            aal_cfg += '\t{%s,\t %s,\t%s,\t"%s"},\n'%(ret[0][1], 0, dal_pin_map[ bal_pin_map[index]], item[1])
    print(def_pins_head + "\n\n")
    print(bal_cfg + "\n\n")
    print(dal_def)
    print(dal_cfg + "\n\n") 
#    print(dal_pin_map)
    print(aal_cfg + "\n\n") 

    ret_all={}
    ret_all.update({"head":def_pins_head})
    ret_all.update({"bal":bal_cfg})
    ret_all.update({"dal_def":dal_def})
    ret_all.update({"dal":dal_cfg})
    ret_all.update({"aal":aal_cfg})
    return ret_all
'''
const tsDAL_ConfigMap	asDAL_ConfigIO[] = {
		{MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_LED_BLUE), 		CFG_ID_PIN_LED_BLUE, 			MAKE_DAL_BO_INIT_ACTIVE(FALSE), 	NULL},//active value
		{MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_LED_RED), 		CFG_ID_PIN_LED_RED, 			MAKE_DAL_BO_INIT_ACTIVE(FALSE), 	NULL},	
		{MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_SHT3X_I2C0_PWR),	CFG_ID_PIN_SHT3X_I2C0_PWR, 		MAKE_DAL_BO_INIT_ACTIVE(TRUE), 		NULL},	

		{MAKE_DAL_HWID_BI_INDEX(CFG_ID_PIN_BUTTON_LEARN),	CFG_ID_PIN_BUTTON_LEARN,		MAKE_DAL_BI_INIT_ACTIVE(FALSE), 	NULL},//need to exteranl pull up
		{MAKE_DAL_HWID_BI_INDEX(CFG_ID_PIN_TEST_ENTER), 	CFG_ID_PIN_TEST_ENTER, 			MAKE_DAL_BI_INIT_ACTIVE(FALSE), 	NULL},	
		
		{MAKE_DAL_HWID_BUS_INDEX(E_DAL_BUS_ID_I2C + 0), 	CFG_ID_PIN_BUS_I2C_SHT3X, 		DAL_CONFIG_INIT_IGNOR,				&STR_BUS_I2C_SHT3X},	
		{MAKE_DAL_HWID_BUS_INDEX(CFG_ID_PIN_SPI_INDEX),		CFG_ID_PIN_BUS_SPI_FBM320,		DAL_CONFIG_INIT_IGNOR,				&STR_BUS_SPI_FBM320},	
//		{MAKE_DAL_HWID_AI_INDEX(0), 						CFG_ID_PIN_ADC_TEST, 			BAL_LEVEL_HI, 			NULL},	
		{MAKE_DAL_HWID_AI_INDEX(CFG_ID_PIN_INTERNAL_V_MONITOR),	CFG_ID_PIN_INTERNAL_V_MONITOR,	DAL_CONFIG_INIT_IGNOR, 			NULL}, 

};

const tsAAL_ConfigMap	asAAL_ConfigIO[] = {

	{E_AAL_HWID_LED_BO, 		E_AAL_LED_TYPE_STATUS,	MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_LED_BLUE),			"LED"},
	{E_AAL_HWID_LED_BO, 		E_AAL_LED_TYPE_COMM,	MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_LED_RED), 			"LED"},

	{E_AAL_HWID_BUTTON_BI,		E_AAL_BUTTON_TYPE_LRN,	MAKE_DAL_HWID_BI_INDEX(CFG_ID_PIN_BUTTON_LEARN),		"Button"},
	{E_AAL_HWID_DEV_TEST_ENTER_BI,	E_AAL_DEV_CHANNEL_NONE,		MAKE_DAL_HWID_BI_INDEX(CFG_ID_PIN_TEST_ENTER),		"TestEnter"}, 

	{E_AAL_HWID_BO_DEV_GENERAL, 	E_AAL_LED_TYPE_COMM,		MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_SHT3X_I2C0_PWR),	"sensor power"},
	{E_AAL_HWID_AI_DEV_GENERAL, 	E_ALIAS_AI_CH_BAT_VOLTAGE,	MAKE_DAL_HWID_AI_INDEX(CFG_ID_PIN_INTERNAL_V_MONITOR),	"Supply voltage"},

	{E_AAL_HWID_TEMPERTRUE_BUS, 	(E_AAL_TEMPERATURE_TYPE_CH1|MAKE_LOGIC_CH(LOGIC_CH1_I2C_SHT3X_TEMPERATURE)),MAKE_DAL_HWID_BUS_INDEX(E_DAL_BUS_ID_I2C+0),	"temperature"}, 
	{E_AAL_HWID_HUMIDITY_BUS,	(E_AAL_HUMIDITY_TYPE_CH1  | MAKE_LOGIC_CH(LOGIC_CH2_I2C_SHT3X_HUMIDITY)),	MAKE_DAL_HWID_BUS_INDEX(E_DAL_BUS_ID_I2C+0),	"humidity"}, 
        {E_AAL_HWID_PRESSURE_BUS,	(E_AAL_PRESSURE_TYPE_CH1  | MAKE_LOGIC_CH(LOGIC_CH1_SPI_FMB320_PRESSURE)),	MAKE_DAL_HWID_BUS_INDEX(CFG_ID_PIN_SPI_INDEX),	"Pressure"}, 

};
'''

def create_inc(desc="", name="", content=''):
    config_fpath= os.path.join(os.getcwd(), 'src', 'pattern_config.h')
    dstFile=os.path.join(os.getcwd(), 'src', '%s_config.h'%name)
    print(config_fpath)
    print(dstFile)
    try:
        fpat =open(config_fpath, 'r')    #打开文件  F:\2019_work\python\qt5
        # f =open(r'F:\2019_work\python\qt5\res\user_param.json',encoding='utf-8')    #打开文件 )
        contest = fpat.read()
        dstfp = open(dstFile, 'w')
        contest=contest.replace("{{%DESC}}", desc)#"E_BAL_I2C_CH%, CFG_ID_BUS_IGNOR_ADDR"
        contest=contest.replace("{{%HEAD}}", 'CONFIG_%s__H'%name)#"E_BAL_I2C_CH%, CFG_ID_BUS_IGNOR_ADDR"
        contest=contest.replace("{{%CONTENT}}", content)#"E_BAL_I2C_CH%, CFG_ID_BUS_IGNOR_ADDR"
        dstfp.write(contest)
        dstfp.close()
        fpat.close()
    except Exception as e:
        print(e)
        print(config_fpath)
       
 #   head=ret[0][5].replace("%", "0")#"E_BAL_I2C_CH%, CFG_ID_BUS_IGNOR_ADDR"
def create_src(desc="", name="", bal="", dal_def="", dal="", aal=""):
    config_fpath= os.path.join(os.getcwd(), 'src', 'pattern_config.c')
    dstFile=os.path.join(os.getcwd(), 'src', '%s_config.c'%name)
    print(config_fpath)
    print(dstFile)
    try:
        fpat =open(config_fpath, 'r')    #打开文件  F:\2019_work\python\qt5
        # f =open(r'F:\2019_work\python\qt5\res\user_param.json',encoding='utf-8')    #打开文件 )
        contest = fpat.read()
        dstfp = open(dstFile, 'w')
        contest=contest.replace("{{%DESC}}", desc)
        contest=contest.replace("{{%HEAD}}", 'CONFIG_%s__H'%name)
        contest=contest.replace("{{%BAL}}", bal)
        contest=contest.replace("{{%DAL_DEF}}",dal_def)
        contest=contest.replace("{{%DAL}}", dal)
        contest=contest.replace("{{%AAL}}", aal)
        dstfp.write(contest)
        dstfp.close()
        fpat.close()
    except Exception as e:
        print(e)
        print(config_fpath)
       


# the following is about the database
#sql_ip = "192.168.116.130"
#sql_user="root"
#sql_pw = "123456"
#sql_db ="db_learn"
#sql_tb_default = "db_learn"
#print("ip:%s user:%s pw:%s db:%s tb:%s" %(sql_ip, sql_user ,sql_pw ,sql_db ,sql_tb_default) )
def req_sql(id=0, table_name="busdriver", db_name="db_learn", like="",column="*", name="name", origin=""):
    db = pymysql.connect("192.168.116.130", "root", "123456", db_name )
    cursor = db.cursor()
    if origin == "":
        if like == "":
            if id == 0:
                sql="SELECT * FROM %s"%table_name
            else:
                sql="SELECT * FROM %s WHERE id=%d" %(table_name,id)
        else:
            sql=r'SELECT %s FROM %s WHERE %s LIKE "%s"' %(column, table_name,name, like)
    else:
        sql=origin
    try:
    #    print(sql)
        cursor.execute(sql)
        results = cursor.fetchall()
    #    print(type(results))
    except:
        traceback.print_exc()
    db.close()
    return results  # tuple


def start_gen_file(src=()):
    gen= convert_c(src)
    if len(gen) == 0:
        print("no valid parameter in start_gen_file function --->")
        return False
    create_inc(desc="//hello charles", name="DEMO", content=gen["head"])
    create_src(desc="//hello charles", name="DEMO", bal=gen["bal"], dal_def=gen["dal_def"],dal=gen["dal"], aal=gen["aal"])
    return True


if __name__ == '__main__':
    src=((1, 'LED', 'OUTPUT', 'PIN:12', 'pullres:PULL_UP, outlevel:LEVEL_H', 'NONE'),
        (2, 'TEMPERATURE', 'I2C', 'IIC_CLK:7,IIC_DAT:6', 'pullres:PULL_UP,ADDR_VALUE:34', 'I2C_SHTX'),
        (3, 'RELAY', 'OUTPUT', 'PIN:3', 'pullres:PULL_UP,outlevel:LEVEL_L', 'NONE'),
        (4, 'BUTTON', 'INPUT', 'PIN:4', 'pullres:PULL_UP', 'NONE'))
    #gen= convert_c()
    start_gen_file(src)

