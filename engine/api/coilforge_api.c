/* COILFORGE API IMPLEMENTATION
 * filename: coilforge_api.c
 * author:   Ozgur Tuna Ozturk [@Tozturk18]
 * date:     14/03/2026
 * license:  MIT License
 * description: This file implements the CoilForge API functions defined in
 *  coilforge_api.h. These functions are intended to be called from Python
 *  through ctypes.
 */

/* --- INCLUDES --- */
#include "coilforge_api.h"

#include "../coil/coil.h"

#include <stdio.h>

/* --- FUNCTION DEFINITIONS --- */

int coilforge_process_config(
    const CoilForgeConfig *config,
    char *out_buffer,
    size_t out_buffer_size
)
{
    const char *direction_str;

    if (config == NULL || out_buffer == NULL || out_buffer_size == 0)
    {
        return 0;
    }

    direction_str = (config->direction < 0) ? "CW" : "CCW";

    snprintf(
        out_buffer,
        out_buffer_size,
        "C API RECEIVED:\n"
        "Hole Radius: %.3f mm\n"
        "Turns: %.3f\n"
        "Track Width: %.3f mm\n"
        "Pitch: %.3f mm\n"
        "Arc Resolution: %d\n"
        "Center: (%.3f, %.3f) mm\n"
        "Angle: %.3f deg\n"
        "Layers: %d\n"
        "Direction: %s\n"
        "Net Name: %s\n"
        "Via Size: %.3f mm\n",
        config->hole_radius,
        config->turns,
        config->track_width,
        config->pitch,
        config->arc_resolution,
        config->center_x,
        config->center_y,
        config->angle,
        config->layers,
        direction_str,
        config->net_name,
        config->via_size
    );

    return 1;
}

int coilforge_get_node_count(const CoilForgeConfig *config, int *out_node_count)
{
    if (config == NULL || out_node_count == NULL)
    {
        return 0;
    }

    return cf_coil_get_node_count(config, out_node_count);
}

int coilforge_generate_nodes(
    const CoilForgeConfig *config,
    CoilForgeVec2 *out_nodes,
    int max_nodes,
    int *out_node_count
)
{
    CF_Coil coil;
    int i;

    if (config == NULL || out_nodes == NULL || out_node_count == NULL)
    {
        return 0;
    }

    if (!cf_coil_generate_single_layer(config, &coil))
    {
        return 0;
    }

    if (max_nodes < coil.node_count)
    {
        cf_coil_free(&coil);
        return 0;
    }

    for (i = 0; i < coil.node_count; ++i)
    {
        out_nodes[i].x = coil.nodes[i].x;
        out_nodes[i].y = coil.nodes[i].y;
    }

    *out_node_count = coil.node_count;

    cf_coil_free(&coil);
    return 1;
}
