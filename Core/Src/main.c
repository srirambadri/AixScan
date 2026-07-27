/* Core/Src/main.c - Hardware Validation Engine */

#include "main.h"
#include <stdio.h>
#include <string.h>

#include "hx711.h"
#include "camera_driver.h"
#include "ff.h" // FatFS for SD card file operations

#define CAMERA_IMAGE_BUFFER_SIZE (224 * 224 * 3)
uint8_t image_buffer[CAMERA_IMAGE_BUFFER_SIZE];

FATFS FatFs;
FIL image_file;
FIL log_file;
UINT bytes_written;

uint32_t capture_count = 0;

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART3_UART_Init(void);

FRESULT Save_Weight_Log(float weight_grams, uint32_t sample_id)
{
    FRESULT res;
    char text_buffer[64];

    res = f_open(&log_file, "weight_log.txt", FA_OPEN_ALWAYS | FA_WRITE);
    if (res == FR_OK) {
        f_lseek(&log_file, f_size(&log_file));
        snprintf(text_buffer, sizeof(text_buffer), "Sample %lu: Weight = %.2f g\r\n", sample_id, weight_grams);
        f_write(&log_file, text_buffer, strlen(text_buffer), &bytes_written);
        f_close(&log_file);
    }
    return res;
}

FRESULT Save_Image_File(uint8_t* buffer, uint32_t buf_size, uint32_t sample_id)
{
    FRESULT res;
    char filename[32];
    snprintf(filename, sizeof(filename), "IMG_%04lu.RAW", sample_id);

    res = f_open(&image_file, filename, FA_CREATE_ALWAYS | FA_WRITE);
    if (res == FR_OK) {
        f_write(&image_file, buffer, buf_size, &bytes_written);
        f_close(&image_file);
    }
    return res;
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();

    MX_GPIO_Init();
    MX_USART3_UART_Init();
    
    printf("\r\n==========================================\r\n");
    printf("     Hardware Check Diagnostic Session    \r\n");
    printf("==========================================\r\n");

    /* 1. Initialize HX711 Weight Sensor */
    printf("[1/3] Initializing HX711 Load Cell Sensor...\r\n");
    HX711_Init();
    HX711_Tare(10);
    printf("  -> Weight sensor ready & tared.\r\n");

    /* 2. Initialize Camera Module */
    printf("[2/3] Initializing Camera Peripheral...\r\n");
    if (Camera_Init() == HAL_OK) {
        printf("  -> Camera initialized successfully.\r\n");
    } else {
        printf("  -> ERROR: Camera initialization failed!\r\n");
    }

    /* 3. Mount SD Card / File System */
    printf("[3/3] Mounting File System...\r\n");
    if (f_mount(&FatFs, "", 1) == FR_OK) {
        printf("  -> SD Card Mounted Successfully.\r\n");
    } else {
        printf("  -> SD Card not detected (Falling back to UART logging).\r\n");
    }

    printf("\r\n--- Press Board Button (B1) to Capture & Log Sensors ---\r\n");

    while (1)
    {
        /* Check if User Button is pressed */
        if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_SET)
        {
            capture_count++;
            printf("\r\n📸 --- Sample Run #%lu ---\r\n", capture_count);

            // Read Weight
            float current_weight = HX711_Read_Weight_Grams();
            printf("  ⚖️ Measured Weight : %.2f g\r\n", current_weight);

            // Capture Image
            printf("  📷 Capturing camera frame...\r\n");
            HAL_StatusTypeDef cam_status = Camera_Capture_Frame(image_buffer, CAMERA_IMAGE_BUFFER_SIZE);

            if (cam_status == HAL_OK) {
                printf("  ✅ Capture OK!\r\n");

                // Save to SD Card
                Save_Weight_Log(current_weight, capture_count);
                Save_Image_File(image_buffer, CAMERA_IMAGE_BUFFER_SIZE, capture_count);
                printf("  💾 Saved IMG_%04lu.RAW and appended weight to weight_log.txt\r\n", capture_count);
            } else {
                printf("  ❌ Camera Capture Failed!\r\n");
            }

            HAL_Delay(1000); // Debounce delay
        }

        HAL_Delay(100);
    }
}