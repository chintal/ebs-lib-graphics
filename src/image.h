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
 * @file image.h
 * @brief The image data handling library
 * 
 * @see image.c
 */

#ifndef IMAGE_H
#define IMAGE_H

#include <stdint.h>
#include "palette.h"

typedef uint16_t image_size_t;
typedef uint8_t image_bpp_t;

typedef enum IMAGE_ENCODING_t{
    IMAGE_ENCODING_RAW, 
    IMAGE_ENCODING_RLC
}image_encoding_t;

typedef enum IMAGE_PIXELTYPE_t{
    IMAGE_PIXELTYPE_RAW,
    IMAGE_PIXELTYPE_INDEXED
}image_pixeltype_t;

typedef struct IMAGE_FORMAT_t{
    const image_encoding_t encoding : 1;
    const image_pixeltype_t indexed : 1; 
    const image_bpp_t bpp : 6;
}image_format_t;

typedef struct IMAGE_t{
    const image_size_t size_x;
    const image_size_t size_y;
    palette_t * const palette;
    const image_format_t format;
    const uint8_t data [];
}image_t;

#endif
