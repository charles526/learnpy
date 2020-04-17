{{%DESC}}

#ifndef {{%HEAD}}
#define {{%HEAD}}

#include "app_common.h"
#include "aal_common.h"


#define MANUFACTORY_NAME	"LUMI"
#define SWBUILD_ID			"2019"
#define PRODUCT_CODE		""
#define PRODUCT_URL		 	"www.aqara.com"



#define PRESSURE_FBM320		0x11
#define PRESSURE_GMP102		0x22

//for eeprom
#define FACTORY_PARAM_TC_MANUFACTORY_ID   		0x1234
#define FACTORY_PARAM_IAS_ZONE_ID				0xFF
#define FACTORY_PARAM_IS_ENROLLED				FALSE

#define FACTORY_PARAM_ICE_IEEE   				0

#define FACTORY_PARAM_TEMP_OFFSET				0


#define FACTORY_PARAM_PROTECT_TEMPERATURE		70	//90C
#define FACTORY_PARAM_PROTECT_POWER100W			25	//2Kw

#define FACTORY_PARAM_SAMPLE_TSEC				10	//10Sec

{{%CONTENT}}


#if (CFG_BUTTONS_NUM  >  MAX_AAL_BTN_NUM)
#error "CFG_BUTTONS_NUM  >  MAX_AAL_BTN_NUM"
#endif


//Learn & Load comb
#define APP_COMB_BUTTON		

/****************************************************************************/
/***        External Variables                                            ***/
/****************************************************************************/
typedef struct
{
	//model id
	char *pcModelId;
	
	//eeprom
    tsEEP_System * psEeprom;

	//bal -> hw pin
	const tsBAL_InitParam * psBalInit;

	//dal -> hw pin
	const tsDAL_InitParam * psDalInit;

	//Aal-> mapping
	const tsAAL_InitParam * psAalInit;

	//App
	tsAPP_InitParam * psAppInit;


}tsSys_Param;

extern tsSys_Param sSysParam;
/****************************************************************************/
/***        Exported Functions                                            ***/
/****************************************************************************/


PUBLIC bool CFG_bAppPinsInit(bool bWarmUp);
PUBLIC void CFG_ReConfigIoPreSleep(void);

PUBLIC uint32 CFG_u32VoltageBATmV(void);

PUBLIC uint8 App_u8GetPressurePID(void);
PUBLIC bool App_bSavePressurePID(uint8 u8PID);


/****************************************************************************/
/***        END OF FILE                                                   ***/
/****************************************************************************/

#endif /* {{%HEAD}} */


