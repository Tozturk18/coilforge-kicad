#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
    double hole_radius;
    double turns;
    double track_width;
    double spacing;
    double center_x;
    double center_y;
    double angle;
    int    layers;
    char   direction[8];
    char   net_name[128];
    double via_size;
} CoilConfig;

static int parse_args(int argc, char *argv[], CoilConfig *cfg) {
    int i;

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
        else if (strcmp(argv[i], "-s") == 0) {
            cfg->spacing = atof(argv[++i]);
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
            strncpy(cfg->direction, argv[++i], sizeof(cfg->direction) - 1);
            cfg->direction[sizeof(cfg->direction) - 1] = '\0';
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

    return 1;
}

int main(int argc, char *argv[]) {
    CoilConfig cfg = {0};

    if (!parse_args(argc, argv, &cfg)) {
        return 1;
    }

    printf("C ENGINE RECEIVED:\n");
    printf("Hole Radius: %.3f mm\n", cfg.hole_radius);
    printf("Turns: %.3f\n", cfg.turns);
    printf("Track Width: %.3f mm\n", cfg.track_width);
    printf("Spacing: %.3f mm\n", cfg.spacing);
    printf("Center X: %.3f mm\n", cfg.center_x);
    printf("Center Y: %.3f mm\n", cfg.center_y);
    printf("Angle: %.3f deg\n", cfg.angle);
    printf("Layers: %d\n", cfg.layers);
    printf("Direction: %s\n", cfg.direction);
    printf("Net Name: %s\n", cfg.net_name);
    printf("Via Size: %.3f mm\n", cfg.via_size);

    return 0;
}