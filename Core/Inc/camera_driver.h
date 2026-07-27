/* Core/Inc/camera_driver.h - Camera Peripheral Interface */

#ifndef __CAMERA_DRIVER_H
#define __CAMERA_DRIVER_H

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"

/* Camera Frame Dimensions */
#define CAMERA_WIDTH   224
#define CAMERA_HEIGHT  224
#define CAMERA_CHANNELS 3 // RGB888

/* Function Declarations */
HAL_StatusTypeDef Camera_Init(void);
HAL_StatusTypeDef Camera_Capture_Frame(uint8_t* buffer, uint32_t buffer_size);

#ifdef __cplusplus
}
#endif

#endif /* __CAMERA_DRIVER_H */