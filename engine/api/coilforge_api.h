/* COILFORGE API HEADER
 * filename: coilforge_api.h
 * author:   Ozgur Tuna Ozturk [@Tozturk18]
 * date:     14/03/2024
 * license:  MIT License
 * description: This header file defines the CoilForge API, including the configuration
 *  structure and the function
 */

#ifndef COILFORGE_API_H
#define COILFORGE_API_H

#include <stddef.h>

#ifdef _WIN32
    #ifdef COILFORGE_BUILD_DLL
        #define COILFORGE_API __declspec(dllexport)
    #else
        #define COILFORGE_API __declspec(dllimport)
    #endif
#else
    #define COILFORGE_API
#endif


#ifdef __cplusplus
extern "C" {
#endif

/*
 * CoilForge configuration structure
 * This sctructure defines the parameters for generating coil geometries.
 * All dimensions are in millimeters [mm] and angles in degrees [deg].
 */
typedef struct
{
    double hole_radius;        /* [mm]    Hole radius               */
    double turns;              /* [#]     Number of turns           */
    double track_width;        /* [mm]    Track width               */
    double spacing;            /* [mm]    Spacing between tracks    */
    double center_x;           /* [mm]    Center X coordinate       */
    double center_y;           /* [mm]    Center Y coordinate       */
    double angle;              /* [deg]   Angle in degrees          */
    int    layers;             /* [int]   Number of layers          */
    int    direction;          /* [0/1]   0 = CW, 1 = CCW           */
    double via_size;           /* [mm]    Via Size                  */
    char   net_name[128];      /* [char*] Null-terminated string    */
} CoilForgeConfig;


/* coilforge_process_config()
* Process the coil configuration and generate output.
* The output is written to the provided buffer, which should be large enough to hold the result.
* Returns non-zero on success, 0 on failure.
*/
COILFORGE_API int coilforge_process_config(
    const CoilForgeConfig *config,  /**< [in]  Pointer to the coil configuration */
    char *out_buffer,               /**< [out] Buffer to receive the output string */
    size_t out_buffer_size          /**< [in]  Size of the output buffer in bytes */
);

#ifdef __cplusplus
}
#endif

#endif
