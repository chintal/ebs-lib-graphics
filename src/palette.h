/* 
   Copyright (c)
     (c) 2018 Chintalagiri Shashank, Quazar Technologies Pvt. Ltd.
   
   This file is part of
   Embedded bootstraps : image library
   
   This library is free software: you can redistribute it and/or modify
   it under the terms of the GNU Lesser General Public License as published
   by the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU Lesser General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>. 
*/

/**
 * @file palette.h
 * @brief The image data handling library
 * 
 * @see palette.c
 */

#ifndef PALETTE_H
#define PALETTE_H

#include <stdint.h>
#include <ds/avltree.h>

// Image palette is based on the libds AVLT implementation, 
// and should use the same functions.

typedef uint16_t PALETTE_INDEX_t;

typedef struct PALETTE_COLOR_t{
    const PALETTE_INDEX_t key;
    struct PALETTE_COLOR_t * left;
    struct PALETTE_COLOR_t * right;
    uint8_t height;
    const uint8_t data [];
}palette_color_t;

typedef struct PALETTE_t{
    palette_color_t * root;
}palette_t;

static inline palette_color_t * palette_find_color(palette_t * palette, 
                                                   uint16_t key)
{
    return (palette_color_t *)avlt_find_node((void * )palette, key);
}

static inline void palette_insert_color(palette_t * palette, 
                                        palette_color_t * color)
{
    return avlt_insert_node((void *)palette, (void *)color);
}
#endif
