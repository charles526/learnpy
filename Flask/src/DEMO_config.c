//hello charles

/****************************************************************************/
/***        Include files                                                 ***/
/****************************************************************************/
#include "bal_driver.h"
#include "app_common.h"


#ifdef DEBUG_CONFIG_FILE
#define TRACE_CONFIG_FILE  TRUE
#else
#define TRACE_CONFIG_FILE FALSE
#endif



/****************************************************************************/
/***        Type Definitions                                              ***/
/****************************************************************************/


/****************************************************************************/
/***        Local Function Prototypes                                     ***/
/****************************************************************************/

/****************************************************************************/
/***        Exported Variables                                            ***/
/****************************************************************************/

/****************************************************************************/
/***       		BAL Eeprom Factory CONFIG                                 ***/
/****************************************************************************/
#define	FACTORY_EEP_PARAM_VERSION			"FP_V102"

//Tall 128 * uint32		
const tsEEP_FactoryParam sFactoryDefault = {
		.cVersion			= FACTORY_EEP_PARAM_VERSION, 	 
		.u32SN				= 10,			 
		.u32FactoryTestOK	= FALSE,			 
		.u32ProtectEnable	= FALSE,		 
		.u32ProtectTempC	= FACTORY_PARAM_PROTECT_TEMPERATURE, 
		.i32TempOffset 		= FACTORY_PARAM_TEMP_OFFSET,  
		.u32ResetEvent		= E_EEP_RST_EVENT_UNKOWN, //0	
		.u32ResetNumber		= 0,
		.u32SystemParam		= SYS_MASK_DELETE_LIMITED,
		.u16ManufacturerCode= FACTORY_PARAM_TC_MANUFACTORY_ID,  
		.u32HeatBeatTSec	= 3300,	//RND_u32GetRand(3000, 3600), //50*60 ~ 60*60
		.u32PollingTSec		= 1, 	//Period Polling Time
		.u32SampleTsec		= FACTORY_PARAM_SAMPLE_TSEC,	//sameple every 10 secondes
		.bDownGradeEn		= FALSE,
		.bForceReportCov	= FALSE,
		.bSuitModeEn		= FALSE,
		.u32CRC				= 0
};


#ifdef SLEEP_16K_RETENTION
tsEEP_FactoryParam sEepFactory __attribute__((section(".bss.discard.app")));
#else
tsEEP_FactoryParam sEepFactory;
#endif

/****************************************************************************/
/***        App Eeprom parameter                                            ***/
/****************************************************************************/
//Include NetWork Information
#define	AAL_PARAM_VERSION			"AP_V104"


const tsEEP_AppParam sAppDefault = {
		.pcVersion  = AAL_PARAM_VERSION, 	
		.u32SN		= 0,			
		.u32CRC		= 0
};


tsEEP_AppParam sEepApp;

/****************************************************************************/
/***        default Eeprom parameter                                            ***/
/****************************************************************************/
const tsEEP_Item asEepParam[] = {
	{EEPROM_ID_FACTORY_PARAM_START_PAGE,	&sFactoryDefault, &sEepFactory}, 	/* Mandatory */
	{EEPROM_ID_APP_PARAM_START_PAGE,		&sAppDefault,     &sEepApp}   
};


tsEEP_System sCfgEEPs = {
		.u8EepNum	= ARRAY_SIZE(asEepParam),//(sizeof(asEepParam) / sizeof(tsEEP_Item)),
		.psHeadEEP	=(tsEEP_Item *)asEepParam,

};

/****************************************************************************/
/***        Config IO BAL parameter                                            ***/
/****************************************************************************/
const tsBAL_ConfigMap	asBAL_ConfigIO[] = {

//following is configed automatically don't edit  -->BAL
	{E_BAL_HWID_IO_INPUT ,	CFG_ID_PIN_BUTTON,	MAKE_BAL_INPUT_INIT(BAL_MODE_PULL_UP)},
	{E_BAL_HWID_IO_OUTPUT ,	CFG_ID_PIN_LED,	MAKE_BAL_OUTPUT_INIT(BAL_MODE_PULL_UP,BAL_LEVEL_LOW)},
	{E_BAL_HWID_IO_OUTPUT ,	CFG_ID_PIN_RELAY,	MAKE_BAL_OUTPUT_INIT(BAL_MODE_PULL_UP,BAL_LEVEL_LOW)},
	{E_BAL_HWID_IIC_CLK ,	CFG_ID_PIN_I2C_SHTX_IIC_CLK,	MAKE_BAL_IIC_INIT(BAL_MODE_PULL_UP,42)},
	{E_BAL_HWID_IIC_DATA ,	CFG_ID_PIN_I2C_SHTX_IIC_DAT,	MAKE_BAL_IIC_INIT(BAL_MODE_PULL_UP,42)},
	  
};


//for interrupte

extern void APP_vGintCallback(void);


const tsBAL_InitParam sBAL_InitParam = {
		.u8BalConfigIoNum 	= ARRAY_SIZE(asBAL_ConfigIO), 
		.psHeadBalConfigIO	= asBAL_ConfigIO,

	 	.u32GintPolMask 	= CFG_GINT0_POL_MASK,
		.u32GintEnaMask 	= CFG_GINT0_ENA_MASK,
		.pfBAL_GintCallBack = APP_vGintCallback,
		.bGintDisable		= FALSE,
		
		.bTemperatureEnable	= TRUE,
		.bBatteryCheckEnable= TRUE,	
};


/****************************************************************************/
/***        Config IO DAL parameter                                            ***/
/**/
/****************************************************************************/
#define CFG_ID_PIN_BUS_I2C_SHT3X	 (MAKE_DAL_BUS_HEADER(E_BAL_I2C_CH0, CFG_ID_BUS_IGNOR_ADDR) | MAKE_DAL_MASK_I2C_SHT3X_PIN(CFG_ID_PIN_I2C_SHTX_IIC_DAT,CFG_ID_PIN_I2C_SHTX_IIC_CLK)) 

const tsDAL_ConfigMap	asDAL_ConfigIO[] = {

//following is configed automatically don't edit  -->DAL
	{MAKE_DAL_HWID_BI_INDEX(CFG_ID_PIN_BUTTON),	 CFG_ID_PIN_BUTTON,	MAKE_DAL_BI_INIT_ACTIVE(FALSE),	NONE},
	{MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_LED),	 CFG_ID_PIN_LED,	MAKE_DAL_BO_INIT_ACTIVE(FALSE),	NONE},
	{MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_RELAY),	 CFG_ID_PIN_RELAY,	MAKE_DAL_BO_INIT_ACTIVE(FALSE),	NONE},
	{MAKE_DAL_HWID_BUS_INDEX(E_DAL_BUS_ID_I2C+0),	 CFG_ID_PIN_BUS_I2C_SHT3X,	DAL_CONFIG_INIT_IGNOR,	&STR_BUS_I2C_SHTX},

};

tsDAL_InitParam sDAL_InitParam = {
		.u8DalConfigIoNum 	= ARRAY_SIZE(asDAL_ConfigIO), 
		.psHeadDalConfigIO	= asDAL_ConfigIO,
#if TRACE_CONFIG_FILE
		.bShowBusDevice 	= TRUE,
#else
		.bShowBusDevice 	= FALSE,
#endif

};



/****************************************************************************/
/***        Config IO APL parameter                                            ***/
/****************************************************************************/
const tsAAL_ConfigMap	asAAL_ConfigIO[] = {

//following is configed automatically don't edit  -->AAL
	{E_AAL_HWID_BUTTON_BI,	 0,	MAKE_DAL_HWID_BI_INDEX(CFG_ID_PIN_BUTTON),	"BUTTON"},
	{E_AAL_HWID_LED_BO,	 0,	MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_LED),	"LED"},
	{E_AAL_HWID_RELAY_BO,	 0,	MAKE_DAL_HWID_BO_INDEX(CFG_ID_PIN_RELAY),	"RELAY"},
	{E_AAL_HWID_TEMPERTRUE_BUS,	 0|0,	MAKE_DAL_HWID_BUS_INDEX(E_DAL_BUS_ID_I2C+0),	"TEMPERATURE"},

};




tsAAL_InitParam sAAL_InitParam = {
		.u8MapBalNum 	= ARRAY_SIZE(asAAL_ConfigIO), 
		.psHeadMapBal	= asAAL_ConfigIO,

};


/****************************************************************************/
/***        Config IO APP parameter                                            ***/
/****************************************************************************/
#define	APP_INIT_PARAM_VERSION			"APP_V10"

tsAPP_InitParam sAPP_InitParam = {
		.cVersion 			= APP_INIT_PARAM_VERSION , 
		.u8AppButtonMode 	= APP_BUTTON_MODE_ONLY_SIGLE_CLICK,
};


/****************************************************************************/
/***        System parameter                                            ***/
/****************************************************************************/

tsSys_Param sSysParam = {
		.pcModelId  = LUMI_MODLE_ID,
		.psEeprom	= &sCfgEEPs,
		.psBalInit	= &sBAL_InitParam,
		.psDalInit	= &sDAL_InitParam,
		.psAalInit	= &sAAL_InitParam,
		.psAppInit	= &sAPP_InitParam,
		
};


/****************************************************************************/
/***        END OF FILE                                                   ***/
/****************************************************************************/

