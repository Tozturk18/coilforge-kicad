#include "vec2.h"

#include <math.h>

CF_Vec2 cf_vec2(double x, double y) {
    CF_Vec2 v;
    v.x = x;
    v.y = y;
    return v;
}

CF_Vec2 cf_vec2_add(CF_Vec2 a, CF_Vec2 b) {
    return cf_vec2(a.x + b.x, a.y + b.y);
}

CF_Vec2 cf_vec2_sub(CF_Vec2 a, CF_Vec2 b) {
    return cf_vec2(a.x - b.x, a.y - b.y);
}

CF_Vec2 cf_vec2_scale(CF_Vec2 v, double s) {
    return cf_vec2(v.x * s, v.y * s);
}

double cf_vec2_dot(CF_Vec2 a, CF_Vec2 b) {
    return a.x * b.x + a.y * b.y;
}

double cf_vec2_norm(CF_Vec2 v) {
    return sqrt(cf_vec2_dot(v, v));
}

CF_Vec2 cf_vec2_normalize(CF_Vec2 v) {
    double n = cf_vec2_norm(v);

    if (n <= 0.0)
    {
        return cf_vec2(1.0, 0.0);
    }

    return cf_vec2_scale(v, 1.0 / n);
}

CF_Vec2 cf_vec2_rotate(CF_Vec2 v, double angle_rad) {
    double c = cos(angle_rad);
    double s = sin(angle_rad);

    return cf_vec2(
        v.x * c - v.y * s,
        v.x * s + v.y * c
    );
}
