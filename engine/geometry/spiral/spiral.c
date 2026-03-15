#include "spiral.h"

#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

double cf_deg_to_rad(double angle_deg) {
    return angle_deg * M_PI / 180.0;
}

double cf_spiral_omega(double pitch) {
    return 2.0 * M_PI / pitch;
}

double cf_spiral_end_u(const CF_SpiralParams *params) {
    return params->hole_radius + params->turns * params->pitch;
}

CF_Vec2 cf_spiral_base_point(double u, const CF_SpiralParams *params) {
    double omega = cf_spiral_omega(params->pitch);
    double phi   = cf_deg_to_rad(params->angle_deg);
    double theta = u * omega + phi;

    return cf_vec2(
        u * cos(theta),
        u * sin(theta)
    );
}

CF_Vec2 cf_spiral_axis_unit(const CF_SpiralParams *params) {
    double u_end = cf_spiral_end_u(params);
    CF_Vec2 A = cf_spiral_base_point(u_end, params);
    return cf_vec2_normalize(A);
}

CF_Vec2 cf_spiral_directional_point(double u, const CF_SpiralParams *params) {
    CF_Vec2 base = cf_spiral_base_point(u, params);
    CF_Vec2 axis = cf_spiral_axis_unit(params);

    /* d = +1 => original
       d = -1 => reflected across axis */
    double d = (params->direction >= 0) ? 1.0 : -1.0;

    /* x_d = d*x + (1-d)*(x.a)*a */
    double proj = cf_vec2_dot(base, axis);

    CF_Vec2 original_part  = cf_vec2_scale(base, d);
    CF_Vec2 reflected_part = cf_vec2_scale(axis, (1.0 - d) * proj);

    return cf_vec2_add(original_part, reflected_part);
}

double cf_spiral_trimmed_end_u(const CF_SpiralParams *params, double via_size) {
    double u_end = cf_spiral_end_u(params);

    if (via_size <= 0.0)
    {
        return u_end;
    }

    /* Back off the end point slightly so the via can attach tangentially.
       This uses a geometric angular offset at the outer radius. */
    {
        double outer_radius = u_end;
        double via_radius   = 0.5 * via_size;
        double arg          = via_radius / (2.0 * outer_radius);

        if (outer_radius <= 0.0)
        {
            return u_end;
        }

        if (arg > 1.0)
        {
            arg = 1.0;
        }
        else if (arg < -1.0)
        {
            arg = -1.0;
        }

        {
            double delta_theta = 2.0 * asin(arg);
            double delta_u = (delta_theta / (2.0 * M_PI)) * params->pitch;
            return u_end - delta_u;
        }
    }
}
