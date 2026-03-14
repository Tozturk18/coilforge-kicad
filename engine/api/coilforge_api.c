/* COILFORGE API IMPLEMENTATION
 * filename: coilforge_api.c
 * author:   Ozgur Tuna Ozturk [@Tozturk18]
 * date:     14/03/2024
 * license:  MIT License
 * description: This file implements the CoilForge API functions defined in coilforge_api.h.
 *    The main function, coilforge_process_config, takes a CoilForgeConfig structure as input
 *    and generates a formatted string output based on the configuration parameters.
 */

 /* --- INCLUDES --- */
#include "coilforge_api.h"

#include <stdio.h>
#include <string.h>

/* --- FUNCTION DEFINITIONS --- */

/*
 * Processes the CoilForge configuration and generates a formatted string output.
 *
 * Args: 
 *  config          [const CoilForgeConfig *] - A pointer to the configuration structure.
 *  out_buffer      [char *]                  - A pointer to the output buffer where the formatted string will be stored.
 *  out_buffer_size [size_t]                  - The size of the output buffer.
 *
 * Returns: 1 if successful, 0 otherwise.
 */
int coilforge_process_config( const CoilForgeConfig *config, char *out_buffer, size_t out_buffer_size ) {

    // Validate input parameters
    if (config == NULL || out_buffer == NULL || out_buffer_size == 0) {
        return 0;
    }

    // Temporary variable to hold the string representation of the direction
    const char *direction_str;
    // Convert the direction integer to a string for output
    direction_str = (config->direction == 0) ? "CW" : "CCW";

    // Generate the formatted output string based on the configuration parameters
    snprintf(
        out_buffer,
        out_buffer_size,
        "C API RECEIVED:\n"
        "Hole Radius: %.3f mm\n"
        "Turns: %.3f\n"
        "Track Width: %.3f mm\n"
        "Pitch: %.3f mm\n"
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
        config->center_x,
        config->center_y,
        config->angle,
        config->layers,
        direction_str,
        config->net_name,
        config->via_size
    );

    // Indicate successful processing
    return 1;
}
