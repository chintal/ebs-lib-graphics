
/**
 * @file {{ image.name }}.c
 * @brief Image "{{ image.name }}" generated from "{{ image.source }}"
 *
 * Generated by ebs-image version {{ libversion }} using Image Format class
 * {{ classname }} and encoded with {{ image.encoding }}.
 *
 * The estimated size of the generated image is {{ image.packed_size }} bytes.
 *
 * @see {{ image.name }}.h
 */

#include "{{ image.name }}.h"
#include <stddef.h>


const image_t {{ image.name }} = {
    0x{{ '%04x' % image.size_x }},         // size_x
    0x{{ '%04x' % image.size_y }},         // size_y
    {{ image.palette }},        // palette
    {   // Image Format
        {{ image.encoding }},   // encoding
        {{ image.pixeltype }},  // pixeltype
        {{ image.bpp }},        // bpp
    },
    {   // Image Data{% for line in image.lines %}

        // Line {{ loop.index }}
    {% for row in line | batch(12) %}
    {% for b in row %}0x{{ '%02x' % b }}, {% endfor %}

    {% endfor %}
    {% endfor %}

    },
};
