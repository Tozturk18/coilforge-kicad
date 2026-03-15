/* COILFORGE API HEADER
 * filename: coilforge_api.h
 * author:   Ozgur Tuna Ozturk [@Tozturk18]
 * date:     14/03/2026
 * license:  MIT License
 * description: This header file defines the CoilForge API, including the
 *  configuration structure and the public functions used by the Python ctypes
 *  bridge.
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
 * This structure defines the parameters for generating coil geometries.
 * All dimensions are in millimeters [mm] and angles in degrees [deg].
 */
typedef struct
{
    double hole_radius;        /* [mm]    Hole radius               */
    double turns;              /* [#]     Number of turns           */
    double track_width;        /* [mm]    Track width               */
    double pitch;              /* [mm]    Pitch between tracks      */
    int    arc_resolution;     /* [#]     Arcs per turn             */
    double center_x;           /* [mm]    Center X coordinate       */
    double center_y;           /* [mm]    Center Y coordinate       */
    double angle;              /* [deg]   Angle in degrees          */
    int    layers;             /* [int]   Number of layers          */
    int    direction;          /* [-1/1]  -1 = CW, 1 = CCW          */
    double via_size;           /* [mm]    Via Size                  */
    char   net_name[128];      /* [char*] Null-terminated string    */
} CoilForgeConfig;

/*
 * Public 2D point used for returning coil nodes to Python.
 */
typedef struct
{
    double x;
    double y;
} CoilForgeVec2;

/*
 * Process the coil configuration and generate a formatted output string.
 * Returns non-zero on success, 0 on failure.
 */
COILFORGE_API int coilforge_process_config(
    const CoilForgeConfig *config,
    char *out_buffer,
    size_t out_buffer_size
);

/*
 * Compute the number of distinct spiral nodes required for the current config.
 * Returns non-zero on success, 0 on failure.
 */
COILFORGE_API int coilforge_get_node_count(
    const CoilForgeConfig *config,
    int *out_node_count
);

/*
 * Generate the node list for a single-layer coil centerline.
 *
 * The caller allocates the output array.
 * max_nodes must be at least the required node count returned by
 * coilforge_get_node_count().
 *
 * Returns non-zero on success, 0 on failure.
 */
COILFORGE_API int coilforge_generate_nodes(
    const CoilForgeConfig *config,
    CoilForgeVec2 *out_nodes,
    int max_nodes,
    int *out_node_count
);

#ifdef __cplusplus
}
#endif

#endif /* COILFORGE_API_H */
