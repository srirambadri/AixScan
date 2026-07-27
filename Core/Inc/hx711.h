/* Core/Inc/hx711.h - HX711 Weight Sensor Header */

#ifndef __HX711_H
#define __HX711_H

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"

/* Default Pins (Adjust in STM32CubeMX according to your board layout) */
#define HX711_SCK_GPIO_Port GPIOA
#define HX711_SCK_Pin       GPIO_PIN_5
#define HX711_DOUT_GPIO_Port GPIOA
#define HX711_DOUT_Pin      GPIO_PIN_6

/* Calibration factor: Raw ADC units per gram (Calibrate using a known weight) */
#define HX711_SCALE_FACTOR  420.0f

/* Function Declarations */
void     HX711_Init(void);
int32_t  HX711_Read_Raw(void);
void     HX711_Tare(uint8_t samples);
float    HX711_Read_Weight_Grams(void);

#ifdef __cplusplus
}
#endif

#endif /* __HX711_H */