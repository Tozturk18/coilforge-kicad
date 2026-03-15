#ifndef COILFORGE_SPIRAL_H
#define COILFORGE_SPIRAL_H

#include "../vec2/vec2.h"

typedef struct
{
    double hole_radius;     /* [mm] inner radius parameter */
    double turns;           /* [#] number of turns */
    double pitch;           /* [mm] radial pitch per turn */
    double angle_deg;       /* [deg] global rotation */
    int    direction;       /* +1 = CCW, -1 = CW */
} CF_SpiralParams;

double  cf_deg_to_rad(double angle_deg);
double  cf_spiral_omega(double pitch);
double  cf_spiral_end_u(const CF_SpiralParams *params);

CF_Vec2 cf_spiral_base_point(double u, const CF_SpiralParams *params);
CF_Vec2 cf_spiral_axis_unit(const CF_SpiralParams *params);
CF_Vec2 cf_spiral_directional_point(double u, const CF_SpiralParams *params);

double  cf_spiral_trimmed_end_u(const CF_SpiralParams *params, double via_size);

#endif /* COILFORGE_SPIRAL_H */
