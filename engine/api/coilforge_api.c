#include "coilforge_api.h"

#include <stdio.h>
#include <string.h>

int coilforge_process_config( const CoilForgeConfig *config, char *out_buffer, size_t out_buffer_size ) {
    const char *direction_str;

    if (config == NULL || out_buffer == NULL || out_buffer_size == 0) {
        return 0;
    }

    direction_str = (config->direction == 0) ? "CW" : "CCW";

    snprintf(
        out_buffer,
        out_buffer_size,
        "C API RECEIVED:\n"
        "Hole Radius: %.3f mm\n"
        "Turns: %.3f\n"
        "Track Width: %.3f mm\n"
        "Spacing: %.3f mm\n"
        "Center: (%.3f, %.3f) mm\n"
        "Angle: %.3f deg\n"
        "Layers: %d\n"
        "Direction: %s\n"
        "Net Name: %s\n"
        "Via Size: %.3f mm\n",
        config->hole_radius,
        config->turns,
        config->track_width,
        config->spacing,
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
