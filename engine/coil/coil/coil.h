#ifndef COILFORGE_COIL_H
#define COILFORGE_COIL_H

#include "../../geometry/vec2/vec2.h"
#include "../../geometry/spiral/spiral.h"
#include "../../api/coilforge_api.h"

typedef struct
{
    CF_Vec2 *nodes;
    int      node_count;
    CF_Vec2  via_node;
    int      has_via;
} CF_Coil;

/*
 * Compute the exact number of nodes required for the given config.
 * Supports fractional turns by appending two extra nodes for the final
 * partial arc:
 *   - partial arc midpoint
 *   - partial arc endpoint
 */
int cf_coil_get_node_count(const CoilForgeConfig *config, int *out_node_count);

/*
 * Build the abstract node-position parameter list q:
 *
 * Full arcs generate:
 *   0, 1, 2, ..., 2 * full_arc_count
 *
 * If a fractional arc remains, append:
 *   2 * full_arc_count + frac_arc_count
 *   2 * full_arc_count + 2 * frac_arc_count
 *
 * Example:
 *   turns = 10.56, arc_resolution = 2
 *   arc_count_exact = 21.12
 *   q = 0,1,2,...,42,42.12,42.24
 */
int cf_coil_build_node_parameters(
    const CoilForgeConfig *config,
    double *out_q_values,
    int max_q_values,
    int *out_count
);

/*
 * Generate the centerline node list for a single-layer coil.
 */
int cf_coil_generate_single_layer(const CoilForgeConfig *config, CF_Coil *coil);

/*
 * Free memory owned by a generated coil.
 */
void cf_coil_free(CF_Coil *coil);

#endif /* COILFORGE_COIL_H */
