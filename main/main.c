#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "../engine/api/coilforge_api.h"

static int parse_args(int argc, char *argv[], CoilForgeConfig *cfg) {
    int i;
    double legacy_spacing;
    int saw_legacy_spacing;
    int saw_pitch;

    legacy_spacing = 0.0;
    saw_legacy_spacing = 0;
    saw_pitch = 0;

    if ((argc - 1) % 2 != 0) {
        fprintf(stderr, "Invalid number of arguments. Arguments should be in pairs.\n");
        return 0;
    }

    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-r") == 0) {
            cfg->hole_radius = atof(argv[++i]);
        }
        else if (strcmp(argv[i], "-t") == 0) {
            cfg->turns = atof(argv[++i]);
        }
        else if (strcmp(argv[i], "-w") == 0) {
            cfg->track_width = atof(argv[++i]);
        }
        else if (strcmp(argv[i], "-p") == 0) {
            cfg->pitch = atof(argv[++i]);
            saw_pitch = 1;
        }
        else if (strcmp(argv[i], "-s") == 0) {
            legacy_spacing = atof(argv[++i]);
            saw_legacy_spacing = 1;
        }
        else if (strcmp(argv[i], "-x") == 0) {
            cfg->center_x = atof(argv[++i]);
        }
        else if (strcmp(argv[i], "-y") == 0) {
            cfg->center_y = atof(argv[++i]);
        }
        else if (strcmp(argv[i], "-a") == 0) {
            cfg->angle = atof(argv[++i]);
        }
        else if (strcmp(argv[i], "-l") == 0) {
            cfg->layers = atoi(argv[++i]);
        }
        else if (strcmp(argv[i], "-d") == 0) {
            const char *direction = argv[++i];

            if (strcmp(direction, "CW") == 0) {
                cfg->direction = 0;
            }
            else if (strcmp(direction, "CCW") == 0) {
                cfg->direction = 1;
            }
            else {
                fprintf(stderr, "Direction must be CW or CCW, got: %s\n", direction);
                return 0;
            }
        }
        else if (strcmp(argv[i], "-n") == 0) {
            strncpy(cfg->net_name, argv[++i], sizeof(cfg->net_name) - 1);
            cfg->net_name[sizeof(cfg->net_name) - 1] = '\0';
        }
        else if (strcmp(argv[i], "-v") == 0) {
            cfg->via_size = atof(argv[++i]);
        }
        else {
            fprintf(stderr, "Unknown or incomplete argument: %s\n", argv[i]);
            return 0;
        }
    }

    if (saw_legacy_spacing && !saw_pitch) {
        cfg->pitch = legacy_spacing + cfg->track_width;
    }

    return 1;
}

int main(int argc, char *argv[]) {
    CoilForgeConfig cfg = {0};
    char buffer[1024];

    if (!parse_args(argc, argv, &cfg)) {
        return 1;
    }
    
    if (!coilforge_process_config(&cfg, buffer, sizeof(buffer)))
    {
        fprintf(stderr, "coilforge_process_config failed\n");
        return 1;
    }

    printf("%s", buffer);

    return 0;
}
