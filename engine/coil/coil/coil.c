#include "coil.h"

#include <math.h>
#include <stdlib.h>

static void cf_coil_init(CF_Coil *coil)
{
    if (coil == NULL)
    {
        return;
    }

    coil->nodes = NULL;
    coil->node_count = 0;
    coil->via_node = cf_vec2(0.0, 0.0);
    coil->has_via = 0;
}

void cf_coil_free(CF_Coil *coil)
{
    if (coil == NULL)
    {
        return;
    }

    free(coil->nodes);
    coil->nodes = NULL;
    coil->node_count = 0;
    coil->via_node = cf_vec2(0.0, 0.0);
    coil->has_via = 0;
}

int cf_coil_get_node_count(const CoilForgeConfig *config, int *out_node_count)
{
    double arc_count_exact;
    int full_arc_count;
    double frac_arc_count;
    int node_count;
    const double eps = 1e-12;

    if (config == NULL || out_node_count == NULL)
    {
        return 0;
    }

    if (config->turns <= 0.0)
    {
        return 0;
    }

    if (config->pitch <= 0.0)
    {
        return 0;
    }

    if (config->arc_resolution < 2)
    {
        return 0;
    }

    if ((config->arc_resolution % 2) != 0)
    {
        return 0;
    }

    arc_count_exact = config->turns * (double)config->arc_resolution;
    full_arc_count  = (int)floor(arc_count_exact);
    frac_arc_count  = arc_count_exact - (double)full_arc_count;

    node_count = 2 * full_arc_count + 1;

    if (frac_arc_count > eps)
    {
        node_count += 2;
    }

    *out_node_count = node_count;
    return 1;
}

int cf_coil_build_node_parameters(
    const CoilForgeConfig *config,
    double *out_q_values,
    int max_q_values,
    int *out_count
)
{
    double arc_count_exact;
    int full_arc_count;
    double frac_arc_count;
    int node_count;
    int idx;
    int k;
    const double eps = 1e-12;

    if (config == NULL || out_q_values == NULL || out_count == NULL)
    {
        return 0;
    }

    if (config->turns <= 0.0 || config->pitch <= 0.0 || config->arc_resolution < 2)
    {
        return 0;
    }

    if ((config->arc_resolution % 2) != 0)
    {
        return 0;
    }

    arc_count_exact = config->turns * (double)config->arc_resolution;
    full_arc_count  = (int)floor(arc_count_exact);
    frac_arc_count  = arc_count_exact - (double)full_arc_count;

    node_count = 2 * full_arc_count + 1;
    if (frac_arc_count > eps)
    {
        node_count += 2;
    }

    if (max_q_values < node_count)
    {
        return 0;
    }

    idx = 0;

    /* Full-arc nodes */
    for (k = 0; k <= 2 * full_arc_count; ++k)
    {
        out_q_values[idx++] = (double)k;
    }

    /* Final partial arc:
       start node already exists at q = 2 * full_arc_count
       append midpoint and endpoint only */
    if (frac_arc_count > eps)
    {
        double q_start = 2.0 * (double)full_arc_count;
        double q_mid   = q_start + frac_arc_count;
        double q_end   = q_start + 2.0 * frac_arc_count;

        out_q_values[idx++] = q_mid;
        out_q_values[idx++] = q_end;
    }

    *out_count = idx;
    return 1;
}

int cf_coil_generate_single_layer(const CoilForgeConfig *config, CF_Coil *coil)
{
    CF_SpiralParams params;
    double *q_values;
    int q_count;
    int i;

    if (config == NULL || coil == NULL)
    {
        return 0;
    }

    cf_coil_init(coil);

    if (config->turns <= 0.0)
    {
        return 0;
    }

    if (config->pitch <= 0.0)
    {
        return 0;
    }

    if (config->hole_radius < 0.0)
    {
        return 0;
    }

    if (config->arc_resolution < 2)
    {
        return 0;
    }

    if ((config->arc_resolution % 2) != 0)
    {
        return 0;
    }

    if (config->direction != 1 && config->direction != -1)
    {
        return 0;
    }

    params.hole_radius = config->hole_radius;
    params.turns       = config->turns;
    params.pitch       = config->pitch;
    params.angle_deg   = config->angle;
    params.direction   = config->direction;

    if (!cf_coil_get_node_count(config, &q_count))
    {
        return 0;
    }

    q_values = (double *)calloc((size_t)q_count, sizeof(double));
    if (q_values == NULL)
    {
        return 0;
    }

    if (!cf_coil_build_node_parameters(config, q_values, q_count, &q_count))
    {
        free(q_values);
        return 0;
    }

    coil->nodes = (CF_Vec2 *)calloc((size_t)q_count, sizeof(CF_Vec2));
    if (coil->nodes == NULL)
    {
        free(q_values);
        return 0;
    }

    coil->node_count = q_count;

    for (i = 0; i < q_count; ++i)
    {
        double q = q_values[i];
        double u = params.hole_radius
                 + q * params.pitch / (2.0 * (double)config->arc_resolution);

        CF_Vec2 local_point = cf_spiral_directional_point(u, &params);

        coil->nodes[i] = cf_vec2(
            local_point.x + config->center_x,
            local_point.y + config->center_y
        );
    }

    free(q_values);

    coil->via_node = coil->nodes[coil->node_count - 1];
    coil->has_via = (config->via_size > 0.0) ? 1 : 0;

    return 1;
}
