/* Core/Src/hx711.c - HX711 Weight Sensor Implementation */

#include "hx711.h"

static int32_t tare_offset = 0;

void HX711_Init(void)
{
    HAL_GPIO_WritePin(HX711_SCK_GPIO_Port, HX711_SCK_Pin, GPIO_PIN_RESET);
}

int32_t HX711_Read_Raw(void)
{
    uint32_t count = 0;

    // Wait until DOUT goes low (Data Ready)
    uint32_t timeout = 100000;
    while(HAL_GPIO_ReadPin(HX711_DOUT_GPIO_Port, HX711_DOUT_Pin) == GPIO_PIN_SET)
    {
        if (--timeout == 0) return 0; // Timeout safety
    }

    // Shift in 24 bits
    for (uint8_t i = 0; i < 24; i++)
    {
        HAL_GPIO_WritePin(HX711_SCK_GPIO_Port, HX711_SCK_Pin, GPIO_PIN_SET);
        count = count << 1;
        HAL_GPIO_WritePin(HX711_SCK_GPIO_Port, HX711_SCK_Pin, GPIO_PIN_RESET);

        if (HAL_GPIO_ReadPin(HX711_DOUT_GPIO_Port, HX711_DOUT_Pin) == GPIO_PIN_SET)
        {
            count++;
        }
    }

    // 25th pulse sets gain to 128 for channel A
    HAL_GPIO_WritePin(HX711_SCK_GPIO_Port, HX711_SCK_Pin, GPIO_PIN_SET);
    HAL_GPIO_WritePin(HX711_SCK_GPIO_Port, HX711_SCK_Pin, GPIO_PIN_RESET);

    // Convert 24-bit signed to 32-bit signed
    if (count & 0x800000)
    {
        count |= 0xFF000000;
    }

    return (int32_t)count;
}

void HX711_Tare(uint8_t samples)
{
    int64_t sum = 0;
    for (uint8_t i = 0; i < samples; i++)
    {
        sum += HX711_Read_Raw();
        HAL_Delay(10);
    }
    tare_offset = (int32_t)(sum / samples);
}

float HX711_Read_Weight_Grams(void)
{
    int32_t raw_value = HX711_Read_Raw();
    int32_t net_value = raw_value - tare_offset;
    float weight = (float)net_value / HX711_SCALE_FACTOR;

    return (weight < 0.0f) ? 0.0f : weight; // Prevent small negative jitter readings
}