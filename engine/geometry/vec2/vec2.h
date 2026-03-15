#ifndef COILFORGE_VEC2_H
#define COILFORGE_VEC2_H

typedef struct
{
    double x;
    double y;
} CF_Vec2;

CF_Vec2 cf_vec2(double x, double y);
CF_Vec2 cf_vec2_add(CF_Vec2 a, CF_Vec2 b);
CF_Vec2 cf_vec2_sub(CF_Vec2 a, CF_Vec2 b);
CF_Vec2 cf_vec2_scale(CF_Vec2 v, double s);

double  cf_vec2_dot(CF_Vec2 a, CF_Vec2 b);
double  cf_vec2_norm(CF_Vec2 v);

CF_Vec2 cf_vec2_normalize(CF_Vec2 v);
CF_Vec2 cf_vec2_rotate(CF_Vec2 v, double angle_rad);

#endif /* COILFORGE_VEC2_H */
